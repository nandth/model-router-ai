"""Model router with self-evaluation and escalation logic."""
import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from app.services.prompt_features import PromptFeatures, PromptFeatureExtractor, DifficultyScorer

logger = logging.getLogger(__name__)


class ModelTier(str, Enum):
    """Model capability tiers."""
    CHEAP = "cheap"
    MID = "mid"
    BEST = "best"


class RouteMode(str, Enum):
    """Routing mode."""
    AUTO = "auto"   # Server chooses model (default)
    FORCE = "force"  # Use client's requested model (for testing)


@dataclass
class HardTriggerResult:
    """Result of hard trigger evaluation."""
    triggered: bool
    reasons: List[str] = field(default_factory=list)


@dataclass
class SelfEvalResult:
    """Result from Stage A self-evaluation."""
    answer: str
    confidence: float
    should_escalate: bool
    reasons: List[str]
    parse_error: bool = False


@dataclass
class RoutingDecision:
    """Complete routing decision with all metadata."""
    initial_tier: ModelTier
    final_tier: ModelTier
    initial_model: str
    final_model: str
    score: int
    features: PromptFeatures
    hard_triggers: HardTriggerResult
    self_eval: Optional[SelfEvalResult] = None
    escalated: bool = False


# Model configurations by tier
MODEL_CONFIGS = {
    ModelTier.CHEAP: {
        "model": "gpt-3.5-turbo",
        "provider": "openai",
        "cost_per_1k_input": 0.0005,
        "cost_per_1k_output": 0.0015,
        "max_tokens": 4096,
    },
    ModelTier.MID: {
        "model": "gpt-4",
        "provider": "openai",
        "cost_per_1k_input": 0.03,
        "cost_per_1k_output": 0.06,
        "max_tokens": 8192,
    },
    ModelTier.BEST: {
        "model": "gpt-4-turbo",
        "provider": "openai",
        "cost_per_1k_input": 0.01,
        "cost_per_1k_output": 0.03,
        "max_tokens": 128000,
    },
}


def get_model_for_tier(tier: ModelTier) -> str:
    """Get the model name for a given tier."""
    return MODEL_CONFIGS[tier]["model"]


def get_tier_for_model(model: str) -> Optional[ModelTier]:
    """Get the tier for a given model name."""
    for tier, config in MODEL_CONFIGS.items():
        if config["model"] == model:
            return tier
    return None


class HardTriggerEvaluator:
    """Evaluate hard triggers that force BEST model."""
    
    @classmethod
    def evaluate(cls, features: PromptFeatures) -> HardTriggerResult:
        """
        Check if any hard triggers fire.
        
        Hard triggers immediately route to BEST regardless of score:
        - high_stakes is true
        - has_stack_trace is true (cheap failures are expensive)
        - hard_reasoning AND multi_part (complex multi-step reasoning)
        
        Returns:
            HardTriggerResult with triggered flag and reasons
        """
        reasons = []
        
        if features.high_stakes:
            reasons.append("high_stakes detected (medical/legal/financial content)")
        
        if features.has_stack_trace:
            reasons.append("stack_trace detected (debugging requires accuracy)")
        
        if features.hard_reasoning and features.multi_part:
            reasons.append("hard_reasoning AND multi_part (complex multi-step reasoning)")
        
        return HardTriggerResult(
            triggered=len(reasons) > 0,
            reasons=reasons
        )


class TierMapper:
    """Map difficulty scores to model tiers."""
    
    # Thresholds
    CHEAP_MAX = 30
    MID_MAX = 70
    
    @classmethod
    def map_score_to_tier(cls, score: int) -> ModelTier:
        """
        Map a difficulty score to a model tier.
        
        Args:
            score: Difficulty score 0-100
            
        Returns:
            ModelTier based on score thresholds
        """
        if score <= cls.CHEAP_MAX:
            return ModelTier.CHEAP
        elif score <= cls.MID_MAX:
            return ModelTier.MID
        else:
            return ModelTier.BEST


class SelfEvalParser:
    """Parse and validate self-evaluation responses."""
    
    # Confidence threshold for escalation
    CONFIDENCE_THRESHOLD = 0.75
    
    @classmethod
    def parse_response(cls, response_text: str) -> SelfEvalResult:
        """
        Parse Stage A self-evaluation JSON response.
        
        Expected format:
        {
            "answer": "...",
            "confidence": 0.0-1.0,
            "should_escalate": true/false,
            "reasons": ["..."]
        }
        
        Fails closed: if parsing fails, treat as should_escalate=true
        
        Returns:
            SelfEvalResult with parsed or default values
        """
        try:
            # Try to extract JSON from response (may be wrapped in markdown)
            json_match = re.search(r'\{[^{}]*"answer"[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Try parsing entire response as JSON
                json_str = response_text.strip()
            
            data = json.loads(json_str)
            
            # Validate required keys
            if "answer" not in data:
                logger.warning("Self-eval response missing 'answer' key")
                return cls._fail_closed(response_text)
            
            answer = str(data.get("answer", ""))
            confidence = float(data.get("confidence", 0.0))
            should_escalate = bool(data.get("should_escalate", True))
            reasons = data.get("reasons", [])
            
            if not isinstance(reasons, list):
                reasons = [str(reasons)] if reasons else []
            
            # Clamp confidence to valid range
            confidence = max(0.0, min(1.0, confidence))
            
            return SelfEvalResult(
                answer=answer,
                confidence=confidence,
                should_escalate=should_escalate,
                reasons=reasons,
                parse_error=False
            )
            
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logger.warning(f"Failed to parse self-eval response: {e}")
            return cls._fail_closed(response_text)
    
    @classmethod
    def _fail_closed(cls, response_text: str) -> SelfEvalResult:
        """Return fail-closed result when parsing fails."""
        return SelfEvalResult(
            answer=response_text,  # Use raw response as answer
            confidence=0.0,
            should_escalate=True,
            reasons=["Failed to parse self-evaluation JSON"],
            parse_error=True
        )
    
    @classmethod
    def should_escalate(cls, result: SelfEvalResult) -> bool:
        """
        Determine if we should escalate based on self-eval result.
        
        Escalate if:
        - should_escalate is True, OR
        - confidence < 0.75
        """
        return result.should_escalate or result.confidence < cls.CONFIDENCE_THRESHOLD


class ModelRouter:
    """Main model routing logic."""
    
    # System prompt for Stage A self-evaluation
    SELF_EVAL_SYSTEM_PROMPT = """You are a helpful AI assistant. Answer the user's question while also self-assessing your response quality.

You MUST respond with a valid JSON object in this exact format:
{
    "answer": "Your complete answer to the user's question here",
    "confidence": 0.0 to 1.0,
    "should_escalate": true or false,
    "reasons": ["reason1", "reason2"]
}

Guidelines for confidence and escalation:
- Set confidence to 0.9-1.0 when you are certain and have clear, factual knowledge
- Set confidence to 0.7-0.9 when you are fairly confident but not completely certain
- Set confidence to 0.5-0.7 when you are uncertain or making educated guesses
- Set confidence below 0.5 when you are guessing or handwaving

Set should_escalate to true when:
- You detect missing information needed for a complete answer
- The requirements are ambiguous or unclear
- The reasoning is complex and you may have made errors
- The question involves high-stakes domains (medical, legal, financial)
- You cannot comply with a strict output format requirement
- You are uncertain about your answer's correctness

Always provide your best answer in the "answer" field, even if you recommend escalation."""

    # Router context message for Stage B
    ROUTER_CONTEXT_TEMPLATE = """[Router Context - For Your Information Only]
This request was initially processed by a lighter model which recommended escalation.
Prompt features: score={score}, features={features}
Stage A feedback: confidence={confidence}, reasons={reasons}

Please provide your answer directly. Follow any format requirements from the user.
Do not wrap your response in JSON or reference this router context."""

    @classmethod
    def route(
        cls,
        prompt: str,
        client_model: Optional[str] = None,
        route_mode: RouteMode = RouteMode.AUTO
    ) -> RoutingDecision:
        """
        Determine routing decision for a prompt.
        
        Args:
            prompt: The user's prompt
            client_model: Model requested by client (ignored in AUTO mode)
            route_mode: Routing mode (AUTO or FORCE)
            
        Returns:
            RoutingDecision with full routing information
        """
        # Force mode: use client's model, skip all routing
        if route_mode == RouteMode.FORCE and client_model:
            tier = get_tier_for_model(client_model) or ModelTier.CHEAP
            features = PromptFeatureExtractor.extract(prompt)
            return RoutingDecision(
                initial_tier=tier,
                final_tier=tier,
                initial_model=client_model,
                final_model=client_model,
                score=0,  # Not computed in force mode
                features=features,
                hard_triggers=HardTriggerResult(triggered=False),
                escalated=False
            )
        
        # Step 1: Extract features
        features = PromptFeatureExtractor.extract(prompt)
        
        # Step 2: Compute difficulty score
        score = DifficultyScorer.compute_score(features)
        
        # Step 3: Check hard triggers
        hard_triggers = HardTriggerEvaluator.evaluate(features)
        
        # Step 4: Determine initial tier
        if hard_triggers.triggered:
            initial_tier = ModelTier.BEST
        else:
            initial_tier = TierMapper.map_score_to_tier(score)
        
        initial_model = get_model_for_tier(initial_tier)
        
        # For now, final tier matches initial (self-eval happens in execution)
        return RoutingDecision(
            initial_tier=initial_tier,
            final_tier=initial_tier,
            initial_model=initial_model,
            final_model=initial_model,
            score=score,
            features=features,
            hard_triggers=hard_triggers,
            escalated=False
        )
    
    @classmethod
    def get_escalated_tier(cls, current_tier: ModelTier) -> ModelTier:
        """Get the next tier up for escalation."""
        if current_tier == ModelTier.CHEAP:
            return ModelTier.MID
        elif current_tier == ModelTier.MID:
            return ModelTier.BEST
        else:
            return ModelTier.BEST  # Already at best
    
    @classmethod
    def should_skip_self_eval(cls, tier: ModelTier) -> bool:
        """Determine if self-eval should be skipped for this tier."""
        # Skip self-eval for BEST tier (no point, can't escalate further)
        return tier == ModelTier.BEST
    
    @classmethod
    def build_self_eval_messages(cls, prompt: str) -> List[Dict[str, str]]:
        """Build messages for Stage A self-evaluation call."""
        return [
            {"role": "system", "content": cls.SELF_EVAL_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    
    @classmethod
    def build_stage_b_messages(
        cls,
        prompt: str,
        score: int,
        features: PromptFeatures,
        stage_a_result: SelfEvalResult
    ) -> List[Dict[str, str]]:
        """Build messages for Stage B escalated call."""
        # Compact features representation
        features_str = ", ".join([
            f"{k}={v}" for k, v in features.to_dict().items()
            if isinstance(v, bool) and v  # Only include True booleans
        ])
        
        # Compact reasons
        reasons_str = "; ".join(stage_a_result.reasons[:3])  # Limit to 3 reasons
        
        router_context = cls.ROUTER_CONTEXT_TEMPLATE.format(
            score=score,
            features=features_str or "none",
            confidence=stage_a_result.confidence,
            reasons=reasons_str or "none"
        )
        
        return [
            {"role": "system", "content": router_context},
            {"role": "user", "content": prompt}
        ]
