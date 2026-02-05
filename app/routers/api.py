"""Simple API endpoint for sending prompts to ChatGPT with intelligent routing."""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.routers.schemas import PromptRequest, PromptResponse, RoutingDetails, RouteMode
from app.services.model_router import ModelRouter
from app.services.model_router import RouteMode as RouterRouteMode
from app.services.request_logger import RequestLogger
from app.services.rate_limiter import load_rate_limit_config, rate_limit_dependency
from app.services.routing_executor import (
    RoutingExecutor,
    RoutingExecutorError,
    create_openai_call_fn,
    create_openai_stream_fn,
)
from app.services.savings import estimate_tokens_saved

logger = logging.getLogger(__name__)
router = APIRouter()

# Rate limiting (per-IP, in-memory)
PROMPT_RATE_LIMIT = load_rate_limit_config(
    max_requests_env="RATE_LIMIT_PROMPT_MAX_REQUESTS",
    default_max_requests=30,
)
STREAM_RATE_LIMIT = load_rate_limit_config(
    max_requests_env="RATE_LIMIT_STREAM_MAX_REQUESTS",
    default_max_requests=10,
)
ANALYZE_RATE_LIMIT = load_rate_limit_config(
    max_requests_env="RATE_LIMIT_ANALYZE_MAX_REQUESTS",
    default_max_requests=60,
)

_limit_prompt = rate_limit_dependency(scope="prompt", config=PROMPT_RATE_LIMIT)
_limit_stream = rate_limit_dependency(scope="prompt_stream", config=STREAM_RATE_LIMIT)
_limit_analyze = rate_limit_dependency(scope="analyze", config=ANALYZE_RATE_LIMIT)

# Initialize the routing executor
try:
    llm_call_fn = create_openai_call_fn()
    llm_stream_fn = create_openai_stream_fn()
    routing_executor = RoutingExecutor(llm_call_fn=llm_call_fn)
except Exception as e:
    logger.warning(f"Warning: Failed to initialize routing executor: {e}")
    routing_executor = None
    llm_stream_fn = None


def _map_route_mode(schema_mode: RouteMode) -> RouterRouteMode:
    """Map schema RouteMode to service RouteMode."""
    return RouterRouteMode.FORCE if schema_mode == RouteMode.FORCE else RouterRouteMode.AUTO


def _require_executor() -> RoutingExecutor:
    if routing_executor is None or routing_executor.llm_call_fn is None:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY in .env file",
        )
    return routing_executor


def _require_stream_fn():
    if llm_stream_fn is None:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY in .env file",
        )
    return llm_stream_fn


def _sse(event: str, data: Dict[str, Any]) -> bytes:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    msg = f"event: {event}\n" + "".join(f"data: {line}\n" for line in payload.splitlines()) + "\n"
    return msg.encode("utf-8")


def _execute_prompt(request: PromptRequest) -> PromptResponse:
    executor = _require_executor()
    route_mode = _map_route_mode(request.route_mode)

    # Execute routing pipeline (includes optional self-eval + escalation)
    result = executor.execute(
        prompt=request.prompt,
        client_model=request.model,
        route_mode=route_mode,
        max_tokens=request.max_tokens,
    )

    routing_details = RoutingDetails(
        initial_tier=result["routing_details"]["initial_tier"],
        final_tier=result["routing_details"]["final_tier"],
        score=result["score"],
        hard_triggers=result["routing_details"]["hard_triggers"],
        escalated=result["escalated"],
        stage_a_confidence=result["routing_details"]["stage_a_confidence"],
        stage_a_escalate=result["routing_details"]["stage_a_escalate"],
    )

    return PromptResponse(
        success=True,
        response=result["response"],
        model_used=result["model_used"],
        tokens_used=result["tokens_used"],
        tokens_saved=int(result.get("tokens_saved") or 0),
        tier=result["tier"],
        latency_ms=result["latency_ms"],
        routing=routing_details,
    )


@router.post("/prompt", response_model=PromptResponse)
async def send_prompt(request: PromptRequest, _: None = Depends(_limit_prompt)):
    """
    Send a prompt to ChatGPT with intelligent model routing.
    
    This endpoint:
    1. Analyzes the prompt to extract features (code, complexity, stakes, etc.)
    2. Computes a difficulty/risk score
    3. Routes to appropriate model tier (cheap/mid/best)
    4. Optionally runs self-evaluation and escalates if needed
    5. Returns the response with routing metadata
    
    route_mode options:
    - "auto" (default): Server chooses the best model based on prompt analysis
    - "force": Use the client's requested model (for testing only)
    """
    try:
        return _execute_prompt(request)
    except RoutingExecutorError as e:
        logger.error(f"Routing execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/prompt/raw", response_model=PromptResponse)
async def send_prompt_raw(
    prompt: str = Body(..., media_type="text/plain", description="Raw prompt text (text/plain)"),
    model: str = Query("gpt-3.5-turbo", description="Model hint (ignored in AUTO mode, used in FORCE mode)"),
    max_tokens: int = Query(1000, ge=1, le=4000, description="Maximum tokens to generate"),
    route_mode: RouteMode = Query(RouteMode.AUTO, description="Routing mode: 'auto' or 'force'"),
    _: None = Depends(_limit_prompt),
):
    """
    Send a prompt using a raw text body.

    This is useful for pasting code snippets without having to JSON-escape quotes/newlines.
    """
    try:
        return _execute_prompt(
            PromptRequest(prompt=prompt, model=model, max_tokens=max_tokens, route_mode=route_mode)
        )
    except RoutingExecutorError as e:
        logger.error(f"Routing execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/prompt/stream")
async def stream_prompt(request: PromptRequest, _: None = Depends(_limit_stream)):
    """
    Stream tokens back to the client via Server-Sent Events (SSE).

    Events:
    - meta: routing + model info
    - delta: incremental text chunks {"text": "..."}
    - usage: token usage when available {"prompt_tokens":..., "completion_tokens":..., "total_tokens":...}
    - done: final metadata
    - error: error details

    Note: streaming uses the router's initial model selection and skips self-eval/escalation,
    since those require buffering the full response before returning content.
    """
    stream_fn = _require_stream_fn()

    route_mode = _map_route_mode(request.route_mode)
    routing = ModelRouter.route(
        prompt=request.prompt,
        client_model=request.model,
        route_mode=route_mode,
    )

    model = routing.initial_model
    tier = routing.initial_tier.value
    start_time = time.time()
    usage: Optional[Dict[str, Any]] = None

    def _gen():
        nonlocal usage
        # Early metadata so clients can show status immediately.
        yield _sse(
            "meta",
            {
                "model_used": model,
                "tier": tier,
                "score": routing.score,
                "hard_triggers": routing.hard_triggers.reasons,
                "streaming": True,
                "self_eval_enabled": False,
            },
        )

        try:
            messages = [{"role": "user", "content": request.prompt}]

            for ev in stream_fn(model, messages, request.max_tokens):
                if ev.get("type") == "delta":
                    yield _sse("delta", {"text": ev.get("text", "")})
                elif ev.get("type") == "usage":
                    usage = ev.get("usage") or {}
                    yield _sse("usage", usage)

            latency_ms = (time.time() - start_time) * 1000
            total_tokens = int((usage or {}).get("total_tokens") or 0)
            tokens_saved = 0
            if route_mode == RouterRouteMode.AUTO:
                tokens_saved = estimate_tokens_saved(
                    [
                        {
                            "model": model,
                            "prompt_tokens": int((usage or {}).get("prompt_tokens") or 0),
                            "completion_tokens": int((usage or {}).get("completion_tokens") or 0),
                        }
                    ]
                )

            RequestLogger.log_request(
                prompt=request.prompt,
                routing=routing,
                stage_a_result=None,
                final_model=model,
                final_tier=routing.initial_tier,
                tokens_stage_a=0,
                tokens_stage_b=total_tokens,
                total_tokens=total_tokens,
                tokens_saved=tokens_saved,
                latency_ms=latency_ms,
                success=True,
            )

            yield _sse(
                "done",
                {
                    "model_used": model,
                    "tier": tier,
                    "tokens_used": total_tokens,
                    "tokens_saved": tokens_saved,
                    "latency_ms": round(latency_ms, 2),
                },
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            RequestLogger.log_request(
                prompt=request.prompt,
                routing=routing,
                stage_a_result=None,
                final_model=model,
                final_tier=routing.initial_tier,
                tokens_stage_a=0,
                tokens_stage_b=0,
                total_tokens=0,
                tokens_saved=0,
                latency_ms=latency_ms,
                success=False,
                error=str(e),
            )
            yield _sse("error", {"error": str(e)})

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # Helps with some reverse proxies (e.g. nginx) that buffer responses by default.
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/prompt/stream/raw")
async def stream_prompt_raw(
    prompt: str = Body(..., media_type="text/plain", description="Raw prompt text (text/plain)"),
    model: str = Query("gpt-3.5-turbo", description="Model hint (ignored in AUTO mode, used in FORCE mode)"),
    max_tokens: int = Query(1000, ge=1, le=4000, description="Maximum tokens to generate"),
    route_mode: RouteMode = Query(RouteMode.AUTO, description="Routing mode: 'auto' or 'force'"),
    _: None = Depends(_limit_stream),
):
    """SSE streaming variant of /prompt/raw."""
    return await stream_prompt(
        PromptRequest(prompt=prompt, model=model, max_tokens=max_tokens, route_mode=route_mode)
    )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    api_key_status = "configured" if (routing_executor and routing_executor.llm_call_fn) else "not configured"
    return {
        "status": "healthy",
        "openai_api_key": api_key_status,
        "routing_enabled": True,
    }


@router.post("/analyze")
async def analyze_prompt(request: PromptRequest, _: None = Depends(_limit_analyze)):
    """
    Analyze a prompt without executing it.
    
    Returns the routing decision that would be made for this prompt,
    including features extracted, score computed, and model tier selected.
    Useful for debugging and understanding routing behavior.
    """
    from app.services.model_router import ModelRouter
    from app.services.prompt_features import DifficultyScorer
    
    route_mode = _map_route_mode(request.route_mode)

    routing = ModelRouter.route(prompt=request.prompt, client_model=request.model, route_mode=route_mode)
    
    # Get score breakdown
    score_breakdown = DifficultyScorer.get_score_breakdown(routing.features)
    
    return {
        "features": routing.features.to_dict(),
        "score": routing.score,
        "score_breakdown": score_breakdown,
        "hard_triggers": {
            "triggered": routing.hard_triggers.triggered,
            "reasons": routing.hard_triggers.reasons,
        },
        "routing": {
            "initial_tier": routing.initial_tier.value,
            "initial_model": routing.initial_model,
            "would_use_self_eval": routing.initial_tier.value != "best",
        }
    }
