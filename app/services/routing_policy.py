"""Model routing policy and configuration."""
from typing import Dict, List, Optional
from enum import Enum

class ModelTier(str, Enum):
    """Model capability tiers."""
    CHEAP = "cheap"
    MID = "mid"
    HIGH = "high"

class ModelConfig:
    """Configuration for LLM models."""
    
    MODELS = {
        # Cheap models - for easy tasks
        "gpt-3.5-turbo": {
            "tier": ModelTier.CHEAP,
            "provider": "openai",
            "cost_per_1k_input": 0.0005,
            "cost_per_1k_output": 0.0015,
            "max_tokens": 4096,
            "description": "Fast and cheap, good for simple tasks"
        },
        
        # Mid-tier models - for medium difficulty
        "gpt-4": {
            "tier": ModelTier.MID,
            "provider": "openai",
            "cost_per_1k_input": 0.03,
            "cost_per_1k_output": 0.06,
            "max_tokens": 8192,
            "description": "Balanced performance and cost"
        },
        "claude-2": {
            "tier": ModelTier.MID,
            "provider": "anthropic",
            "cost_per_1k_input": 0.008,
            "cost_per_1k_output": 0.024,
            "max_tokens": 100000,
            "description": "Good for longer contexts"
        },
        
        # High-capability models - for hard tasks
        "gpt-4-turbo": {
            "tier": ModelTier.HIGH,
            "provider": "openai",
            "cost_per_1k_input": 0.01,
            "cost_per_1k_output": 0.03,
            "max_tokens": 128000,
            "description": "Latest and most capable"
        },
        "claude-3-opus": {
            "tier": ModelTier.HIGH,
            "provider": "anthropic",
            "cost_per_1k_input": 0.015,
            "cost_per_1k_output": 0.075,
            "max_tokens": 200000,
            "description": "Most powerful reasoning"
        }
    }
    
    @classmethod
    def get_models_by_tier(cls, tier: ModelTier) -> List[str]:
        """Get list of model names for a given tier."""
        return [
            name for name, config in cls.MODELS.items()
            if config["tier"] == tier
        ]
    
    @classmethod
    def get_model_config(cls, model_name: str) -> Optional[Dict]:
        """Get configuration for a specific model."""
        return cls.MODELS.get(model_name)
    
    @classmethod
    def estimate_cost(cls, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a model call."""
        config = cls.get_model_config(model_name)
        if not config:
            return 0.0
        
        input_cost = (input_tokens / 1000) * config["cost_per_1k_input"]
        output_cost = (output_tokens / 1000) * config["cost_per_1k_output"]
        
        return input_cost + output_cost


class RoutingPolicy:
    """Routes prompts to appropriate models based on difficulty."""
    
    @staticmethod
    def select_model(difficulty_score: float, difficulty_level: str, 
                     previous_model: Optional[str] = None,
                     escalate: bool = False) -> str:
        """
        Select the appropriate model based on difficulty.
        
        Args:
            difficulty_score: Difficulty score (0.0 to 1.0)
            difficulty_level: "easy", "medium", or "hard"
            previous_model: Previously used model (for escalation)
            escalate: Whether to escalate to a higher tier
            
        Returns:
            Model name to use
        """
        # Handle escalation
        if escalate and previous_model:
            return RoutingPolicy._escalate_model(previous_model)
        
        # Route based on difficulty
        if difficulty_level == "easy":
            # Use cheapest model for easy tasks
            models = ModelConfig.get_models_by_tier(ModelTier.CHEAP)
            return models[0] if models else "gpt-3.5-turbo"
        
        elif difficulty_level == "medium":
            # Use mid-tier model
            models = ModelConfig.get_models_by_tier(ModelTier.MID)
            # Prefer GPT-4 for better balance
            return "gpt-4" if "gpt-4" in models else models[0]
        
        else:  # hard
            # Use high-capability model
            models = ModelConfig.get_models_by_tier(ModelTier.HIGH)
            # Prefer GPT-4 Turbo for best performance
            return "gpt-4-turbo" if "gpt-4-turbo" in models else models[0]
    
    @staticmethod
    def _escalate_model(current_model: str) -> str:
        """Escalate to a stronger model."""
        config = ModelConfig.get_model_config(current_model)
        if not config:
            return "gpt-4-turbo"
        
        current_tier = config["tier"]
        
        # Escalate to next tier
        if current_tier == ModelTier.CHEAP:
            models = ModelConfig.get_models_by_tier(ModelTier.MID)
            return models[0] if models else "gpt-4"
        elif current_tier == ModelTier.MID:
            models = ModelConfig.get_models_by_tier(ModelTier.HIGH)
            return models[0] if models else "gpt-4-turbo"
        else:
            # Already at highest tier
            return current_model
