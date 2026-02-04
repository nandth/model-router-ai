"""Services package for model routing."""
from app.services.model_router import (
    ModelRouter,
    ModelTier,
    RouteMode,
    RoutingDecision,
    SelfEvalResult,
    HardTriggerResult,
)
from app.services.prompt_features import (
    PromptFeatures,
    PromptFeatureExtractor,
    DifficultyScorer,
)
from app.services.routing_executor import (
    RoutingExecutor,
    RoutingExecutorError,
    create_openai_call_fn,
    create_openai_stream_fn,
)
from app.services.request_logger import (
    RequestLogger,
    configure_router_logging,
)

__all__ = [
    # Model router
    "ModelRouter",
    "ModelTier",
    "RouteMode",
    "RoutingDecision",
    "SelfEvalResult",
    "HardTriggerResult",
    # Prompt features
    "PromptFeatures",
    "PromptFeatureExtractor",
    "DifficultyScorer",
    # Routing executor
    "RoutingExecutor",
    "RoutingExecutorError",
    "create_openai_call_fn",
    "create_openai_stream_fn",
    # Request logger
    "RequestLogger",
    "configure_router_logging",
]
