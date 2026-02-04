"""Tests for routing policy."""
import pytest
from app.services.routing_policy import RoutingPolicy, ModelConfig, ModelTier


class TestRoutingPolicy:
    """Test cases for routing policy."""
    
    def test_easy_routes_to_cheap(self):
        """Test that easy difficulty routes to cheap models."""
        model = RoutingPolicy.select_model(0.2, "easy")
        config = ModelConfig.get_model_config(model)
        assert config["tier"] == ModelTier.CHEAP
    
    def test_medium_routes_to_mid(self):
        """Test that medium difficulty routes to mid-tier models."""
        model = RoutingPolicy.select_model(0.5, "medium")
        config = ModelConfig.get_model_config(model)
        assert config["tier"] == ModelTier.MID
    
    def test_hard_routes_to_best(self):
        """Test that hard difficulty routes to best-capability models."""
        model = RoutingPolicy.select_model(0.8, "hard")
        config = ModelConfig.get_model_config(model)
        assert config["tier"] == ModelTier.BEST
    
    def test_escalation_from_cheap(self):
        """Test escalation from cheap to mid tier."""
        initial_model = "gpt-3.5-turbo"
        escalated = RoutingPolicy.select_model(
            0.2, "easy", 
            previous_model=initial_model,
            escalate=True
        )
        
        initial_config = ModelConfig.get_model_config(initial_model)
        escalated_config = ModelConfig.get_model_config(escalated)
        
        # Should escalate to higher tier
        assert escalated != initial_model
    
    def test_escalation_from_mid(self):
        """Test escalation from mid to best tier."""
        initial_model = "gpt-4"
        escalated = RoutingPolicy.select_model(
            0.5, "medium",
            previous_model=initial_model,
            escalate=True
        )
        
        escalated_config = ModelConfig.get_model_config(escalated)
        assert escalated_config["tier"] == ModelTier.BEST
    
    def test_cost_estimation(self):
        """Test cost estimation."""
        cost = ModelConfig.estimate_cost("gpt-3.5-turbo", 1000, 500)
        assert cost > 0
        assert isinstance(cost, float)
    
    def test_get_models_by_tier(self):
        """Test getting models by tier."""
        cheap_models = ModelConfig.get_models_by_tier(ModelTier.CHEAP)
        mid_models = ModelConfig.get_models_by_tier(ModelTier.MID)
        best_models = ModelConfig.get_models_by_tier(ModelTier.BEST)
        
        assert len(cheap_models) > 0
        assert len(mid_models) > 0
        assert len(best_models) > 0
