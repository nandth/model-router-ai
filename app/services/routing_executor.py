"""Routing executor service - executes the full routing pipeline."""
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from app.services.model_router import (
    ModelRouter,
    ModelTier,
    RouteMode,
    RoutingDecision,
    SelfEvalParser,
    SelfEvalResult,
    get_model_for_tier,
)
from app.services.request_logger import RequestLogger
from app.services.savings import estimate_tokens_saved

logger = logging.getLogger(__name__)


class RoutingExecutorError(Exception):
    """Base exception for routing executor errors."""
    pass


class RoutingExecutor:
    """
    Executes the complete routing pipeline including self-evaluation.
    
    This class orchestrates:
    1. Initial routing decision
    2. Stage A: Self-evaluation (for CHEAP/MID tiers)
    3. Stage B: Escalated response (if needed)
    4. Logging and observability
    """
    
    def __init__(self, llm_call_fn=None):
        """
        Initialize routing executor.
        
        Args:
            llm_call_fn: Function to call LLM. Signature:
                         (model: str, messages: List[Dict], max_tokens: int) -> Tuple[str, Dict[str, int]]
                         Returns (response_text, usage) where usage includes
                         prompt_tokens, completion_tokens, total_tokens.
        """
        self.llm_call_fn = llm_call_fn
    
    def execute(
        self,
        prompt: str,
        client_model: Optional[str] = None,
        route_mode: RouteMode = RouteMode.AUTO,
        max_tokens: int = 1000,
    ) -> Dict:
        """
        Execute the complete routing pipeline.
        
        Args:
            prompt: User's prompt
            client_model: Client's requested model (used in FORCE mode)
            route_mode: Routing mode (AUTO or FORCE)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict with response and routing metadata
        """
        start_time = time.time()
        
        # Step 1: Get initial routing decision
        routing = ModelRouter.route(prompt, client_model, route_mode)
        
        # Track tokens and escalation
        tokens_stage_a = 0
        tokens_stage_b = 0
        usage_stage_a: Optional[Dict[str, int]] = None
        usage_stage_b: Optional[Dict[str, int]] = None
        stage_a_result: Optional[SelfEvalResult] = None
        final_tier = routing.initial_tier
        final_model = routing.initial_model
        final_response = ""
        escalated = False
        tokens_saved = 0
        
        try:
            # FORCE mode or BEST tier: direct call, skip self-eval
            if route_mode == RouteMode.FORCE or routing.initial_tier == ModelTier.BEST:
                final_response, usage_stage_b = self._call_llm_direct(
                    model=routing.initial_model,
                    prompt=prompt,
                    max_tokens=max_tokens
                )
                tokens_stage_b = int((usage_stage_b or {}).get("total_tokens") or 0)
            else:
                # Stage A: Self-evaluation
                stage_a_response, usage_stage_a = self._call_llm_with_self_eval(
                    model=routing.initial_model,
                    prompt=prompt,
                    max_tokens=max_tokens
                )
                tokens_stage_a = int((usage_stage_a or {}).get("total_tokens") or 0)
                
                # Parse self-eval response
                stage_a_result = SelfEvalParser.parse_response(stage_a_response)
                
                # Decide if escalation is needed
                if SelfEvalParser.should_escalate(stage_a_result):
                    # Escalate to next tier
                    escalated = True
                    final_tier = ModelRouter.get_escalated_tier(routing.initial_tier)
                    final_model = get_model_for_tier(final_tier)
                    
                    # Stage B: Escalated call
                    final_response, usage_stage_b = self._call_llm_stage_b(
                        model=final_model,
                        prompt=prompt,
                        score=routing.score,
                        features=routing.features,
                        stage_a_result=stage_a_result,
                        max_tokens=max_tokens
                    )
                    tokens_stage_b = int((usage_stage_b or {}).get("total_tokens") or 0)
                else:
                    # Use Stage A answer as final
                    final_response = stage_a_result.answer
            
            latency_ms = (time.time() - start_time) * 1000

            # Savings: baseline-token-equivalent savings vs a baseline model (default: gpt-4).
            if route_mode == RouteMode.AUTO:
                calls: List[Dict[str, Any]] = []
                if usage_stage_a is not None:
                    calls.append(
                        {
                            "model": routing.initial_model,
                            "prompt_tokens": usage_stage_a.get("prompt_tokens", 0),
                            "completion_tokens": usage_stage_a.get("completion_tokens", 0),
                        }
                    )
                if usage_stage_b is not None:
                    calls.append(
                        {
                            "model": final_model,
                            "prompt_tokens": usage_stage_b.get("prompt_tokens", 0),
                            "completion_tokens": usage_stage_b.get("completion_tokens", 0),
                        }
                    )
                tokens_saved = estimate_tokens_saved(calls)
            
            # Log the request
            log_entry = RequestLogger.log_request(
                prompt=prompt,
                routing=routing,
                stage_a_result=stage_a_result,
                final_model=final_model,
                final_tier=final_tier,
                tokens_stage_a=tokens_stage_a,
                tokens_stage_b=tokens_stage_b,
                total_tokens=tokens_stage_a + tokens_stage_b,
                tokens_saved=tokens_saved,
                latency_ms=latency_ms,
                success=True,
            )
            
            return {
                "success": True,
                "response": final_response,
                "model_used": final_model,
                "tier": final_tier.value,
                "score": routing.score,
                "escalated": escalated,
                "tokens_used": tokens_stage_a + tokens_stage_b,
                "tokens_saved": tokens_saved,
                "latency_ms": round(latency_ms, 2),
                "routing_details": {
                    "initial_tier": routing.initial_tier.value,
                    "final_tier": final_tier.value,
                    "hard_triggers": routing.hard_triggers.reasons,
                    "stage_a_confidence": stage_a_result.confidence if stage_a_result else None,
                    "stage_a_escalate": stage_a_result.should_escalate if stage_a_result else None,
                }
            }
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            
            # Log the failure
            RequestLogger.log_request(
                prompt=prompt,
                routing=routing,
                stage_a_result=stage_a_result,
                final_model=final_model,
                final_tier=final_tier,
                tokens_stage_a=tokens_stage_a,
                tokens_stage_b=tokens_stage_b,
                total_tokens=tokens_stage_a + tokens_stage_b,
                tokens_saved=tokens_saved,
                latency_ms=latency_ms,
                success=False,
                error=str(e),
            )
            
            raise RoutingExecutorError(f"Routing execution failed: {e}") from e
    
    def _call_llm_direct(
        self,
        model: str,
        prompt: str,
        max_tokens: int
    ) -> Tuple[str, Dict[str, int]]:
        """Make a direct LLM call without self-eval wrapper."""
        if self.llm_call_fn is None:
            raise RoutingExecutorError("LLM call function not configured")
        
        messages = [{"role": "user", "content": prompt}]
        return self.llm_call_fn(model, messages, max_tokens)
    
    def _call_llm_with_self_eval(
        self,
        model: str,
        prompt: str,
        max_tokens: int
    ) -> Tuple[str, Dict[str, int]]:
        """Make an LLM call with self-eval system prompt."""
        if self.llm_call_fn is None:
            raise RoutingExecutorError("LLM call function not configured")
        
        messages = ModelRouter.build_self_eval_messages(prompt)
        return self.llm_call_fn(model, messages, max_tokens)
    
    def _call_llm_stage_b(
        self,
        model: str,
        prompt: str,
        score: int,
        features,
        stage_a_result: SelfEvalResult,
        max_tokens: int
    ) -> Tuple[str, Dict[str, int]]:
        """Make a Stage B escalated LLM call."""
        if self.llm_call_fn is None:
            raise RoutingExecutorError("LLM call function not configured")
        
        messages = ModelRouter.build_stage_b_messages(
            prompt=prompt,
            score=score,
            features=features,
            stage_a_result=stage_a_result
        )
        return self.llm_call_fn(model, messages, max_tokens)


def create_openai_client():
    """Create an OpenAI client if OPENAI_API_KEY is configured; else return None."""
    import os
    from openai import OpenAI
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    return OpenAI(api_key=api_key)


def create_openai_call_fn():
    """Create a non-streaming LLM call function using OpenAI client."""
    client = create_openai_client()
    if client is None:
        return None
    
    def call_openai(
        model: str,
        messages: List[Dict],
        max_tokens: int
    ) -> Tuple[str, Dict[str, int]]:
        """Call OpenAI API."""
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens
        )
        
        response_text = response.choices[0].message.content or ""
        usage_obj = response.usage
        prompt_tokens = int(getattr(usage_obj, "prompt_tokens", 0) or 0) if usage_obj else 0
        completion_tokens = int(getattr(usage_obj, "completion_tokens", 0) or 0) if usage_obj else 0
        total_tokens = int(getattr(usage_obj, "total_tokens", prompt_tokens + completion_tokens) or 0) if usage_obj else 0
        if total_tokens <= 0:
            total_tokens = prompt_tokens + completion_tokens
        
        return response_text, {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }
    
    return call_openai


def create_openai_stream_fn():
    """
    Create a streaming LLM call function using OpenAI chat.completions streaming.

    Yields dict events:
    - {"type": "delta", "text": "..."} for streamed text chunks
    - {"type": "usage", "usage": {...}} when usage is available (if supported)
    """
    client = create_openai_client()
    if client is None:
        return None

    def stream_openai(model: str, messages: List[Dict], max_tokens: int):
        # Request usage in the stream when supported by the API. Fall back gracefully
        # if the installed SDK / API doesn't support stream_options.
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                stream=True,
                stream_options={"include_usage": True},
            )
        except TypeError:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                stream=True,
            )

        for chunk in stream:
            # Text deltas
            try:
                choice0 = chunk.choices[0]
                delta = getattr(choice0, "delta", None)
                text = getattr(delta, "content", None)
            except Exception:
                text = None

            if text:
                yield {"type": "delta", "text": text}

            # Usage (typically appears in the final chunk when include_usage is enabled)
            usage = getattr(chunk, "usage", None)
            if usage is not None:
                yield {
                    "type": "usage",
                    "usage": {
                        "prompt_tokens": getattr(usage, "prompt_tokens", None),
                        "completion_tokens": getattr(usage, "completion_tokens", None),
                        "total_tokens": getattr(usage, "total_tokens", None),
                    },
                }

    return stream_openai
