"""Simple API endpoint for sending prompts to ChatGPT with intelligent routing."""
import logging
from fastapi import APIRouter, HTTPException

from app.routers.schemas import PromptRequest, PromptResponse, RoutingDetails, RouteMode
from app.services.model_router import RouteMode as RouterRouteMode
from app.services.routing_executor import RoutingExecutor, create_openai_call_fn, RoutingExecutorError

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize the routing executor
try:
    llm_call_fn = create_openai_call_fn()
    routing_executor = RoutingExecutor(llm_call_fn=llm_call_fn)
except Exception as e:
    logger.warning(f"Warning: Failed to initialize routing executor: {e}")
    routing_executor = None


def _map_route_mode(schema_mode: RouteMode) -> RouterRouteMode:
    """Map schema RouteMode to service RouteMode."""
    return RouterRouteMode.FORCE if schema_mode == RouteMode.FORCE else RouterRouteMode.AUTO


@router.post("/prompt", response_model=PromptResponse)
async def send_prompt(request: PromptRequest):
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
    if routing_executor is None or routing_executor.llm_call_fn is None:
        raise HTTPException(
            status_code=500, 
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY in .env file"
        )
    
    try:
        route_mode = _map_route_mode(request.route_mode)
        
        # Execute routing pipeline
        result = routing_executor.execute(
            prompt=request.prompt,
            client_model=request.model,
            route_mode=route_mode,
            max_tokens=request.max_tokens or 1000,
        )
        
        # Build routing details
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
            tier=result["tier"],
            latency_ms=result["latency_ms"],
            routing=routing_details,
        )
        
    except RoutingExecutorError as e:
        logger.error(f"Routing execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


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
async def analyze_prompt(request: PromptRequest):
    """
    Analyze a prompt without executing it.
    
    Returns the routing decision that would be made for this prompt,
    including features extracted, score computed, and model tier selected.
    Useful for debugging and understanding routing behavior.
    """
    from app.services.model_router import ModelRouter
    from app.services.prompt_features import DifficultyScorer
    
    route_mode = _map_route_mode(request.route_mode)
    
    # Get routing decision without executing
    routing = ModelRouter.route(
        prompt=request.prompt,
        client_model=request.model,
        route_mode=route_mode,
    )
    
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
