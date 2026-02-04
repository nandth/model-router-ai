"""Structured logging for model routing requests."""
import json
import logging
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.model_router import (
    RoutingDecision,
    SelfEvalResult,
    ModelTier,
)
from app.services.prompt_features import PromptFeatures

# Configure structured logger
router_logger = logging.getLogger("model_router.requests")


class RequestLogger:
    """Structured JSON logging for routing requests."""
    
    # Maximum preview length for prompt (privacy)
    PROMPT_PREVIEW_LENGTH = 120
    
    @classmethod
    def log_request(
        cls,
        prompt: str,
        routing: RoutingDecision,
        stage_a_result: Optional[SelfEvalResult] = None,
        final_model: Optional[str] = None,
        final_tier: Optional[ModelTier] = None,
        tokens_stage_a: int = 0,
        tokens_stage_b: int = 0,
        total_tokens: int = 0,
        latency_ms: float = 0.0,
        success: bool = True,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Log a routing request as structured JSON.
        
        Args:
            prompt: Original prompt (will be truncated for privacy)
            routing: Initial routing decision
            stage_a_result: Self-eval result if Stage A was run
            final_model: Actual model used for final response
            final_tier: Final tier after escalation
            tokens_stage_a: Tokens used in Stage A
            tokens_stage_b: Tokens used in Stage B
            total_tokens: Total tokens used
            latency_ms: Total latency in milliseconds
            success: Whether request succeeded
            error: Error message if failed
            
        Returns:
            The log entry dict for testing/inspection
        """
        log_entry = cls._build_log_entry(
            prompt=prompt,
            routing=routing,
            stage_a_result=stage_a_result,
            final_model=final_model,
            final_tier=final_tier,
            tokens_stage_a=tokens_stage_a,
            tokens_stage_b=tokens_stage_b,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            success=success,
            error=error,
        )
        
        # Log as single JSON line
        router_logger.info(json.dumps(log_entry))
        
        return log_entry
    
    @classmethod
    def _build_log_entry(
        cls,
        prompt: str,
        routing: RoutingDecision,
        stage_a_result: Optional[SelfEvalResult] = None,
        final_model: Optional[str] = None,
        final_tier: Optional[ModelTier] = None,
        tokens_stage_a: int = 0,
        tokens_stage_b: int = 0,
        total_tokens: int = 0,
        latency_ms: float = 0.0,
        success: bool = True,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build the log entry dictionary."""
        features = routing.features
        
        # Compute escalation status explicitly
        escalated = cls._compute_escalation_status(routing, final_tier)
        
        # Build base entry
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prompt": {
                "length_chars": features.len_chars,
                "length_words": features.len_words,
                "preview": cls._truncate_prompt(prompt),
            },
            "features": {
                "has_code_block": features.has_code_block,
                "has_stack_trace": features.has_stack_trace,
                "multi_part": features.multi_part,
                "strict_format": features.strict_format,
                "freshness_need": features.freshness_need,
                "hard_reasoning": features.hard_reasoning,
                "high_stakes": features.high_stakes,
            },
            "score": routing.score,
            "hard_triggers": {
                "triggered": routing.hard_triggers.triggered,
                "reasons": routing.hard_triggers.reasons,
            },
            "routing": {
                "initial_tier": routing.initial_tier.value,
                "initial_model": routing.initial_model,
                "final_tier": (final_tier or routing.final_tier).value,
                "final_model": final_model or routing.final_model,
                "escalated": escalated,
            },
            "tokens": {
                "stage_a": tokens_stage_a,
                "stage_b": tokens_stage_b,
                "total": total_tokens or (tokens_stage_a + tokens_stage_b),
            },
            "latency_ms": round(latency_ms, 2),
            "success": success,
        }
        
        # Add self-eval info if Stage A was run
        if stage_a_result:
            entry["stage_a"] = {
                "confidence": stage_a_result.confidence,
                "should_escalate": stage_a_result.should_escalate,
                "reasons": stage_a_result.reasons[:5],  # Limit reasons
                "parse_error": stage_a_result.parse_error,
            }
        
        # Add error if present
        if error:
            entry["error"] = error
        
        return entry
    
    @classmethod
    def _compute_escalation_status(
        cls,
        routing: RoutingDecision,
        final_tier: Optional[ModelTier]
    ) -> bool:
        """
        Compute whether escalation occurred.
        
        Returns True if:
        - routing.escalated is True, OR
        - final_tier is different from initial_tier
        """
        if routing.escalated:
            return True
        if final_tier is not None and final_tier != routing.initial_tier:
            return True
        return False
    
    @classmethod
    def _truncate_prompt(cls, prompt: str) -> str:
        """Truncate prompt to preview length for privacy."""
        if len(prompt) <= cls.PROMPT_PREVIEW_LENGTH:
            return prompt
        return prompt[:cls.PROMPT_PREVIEW_LENGTH] + "..."


def configure_router_logging(
    log_level: int = logging.INFO,
    log_file: Optional[str] = None
) -> None:
    """
    Configure the router logger.
    
    Args:
        log_level: Logging level
        log_file: Optional file path for log output
    """
    logger = logging.getLogger("model_router.requests")
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter (just the message, since we're outputting JSON)
    formatter = logging.Formatter("%(message)s")
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
