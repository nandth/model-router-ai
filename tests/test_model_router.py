"""Tests for model router logic."""
import pytest
from app.services.model_router import (
    ModelRouter,
    ModelTier,
    RouteMode,
    HardTriggerEvaluator,
    TierMapper,
    SelfEvalParser,
    get_model_for_tier,
    get_tier_for_model,
)
from app.services.prompt_features import PromptFeatures


class TestTierMapper:
    """Test cases for tier mapping."""
    
    def test_low_score_maps_to_cheap(self):
        """Test that low scores map to CHEAP tier."""
        assert TierMapper.map_score_to_tier(0) == ModelTier.CHEAP
        assert TierMapper.map_score_to_tier(15) == ModelTier.CHEAP
        assert TierMapper.map_score_to_tier(30) == ModelTier.CHEAP
    
    def test_mid_score_maps_to_mid(self):
        """Test that mid scores map to MID tier."""
        assert TierMapper.map_score_to_tier(31) == ModelTier.MID
        assert TierMapper.map_score_to_tier(50) == ModelTier.MID
        assert TierMapper.map_score_to_tier(70) == ModelTier.MID
    
    def test_high_score_maps_to_best(self):
        """Test that high scores map to BEST tier."""
        assert TierMapper.map_score_to_tier(71) == ModelTier.BEST
        assert TierMapper.map_score_to_tier(85) == ModelTier.BEST
        assert TierMapper.map_score_to_tier(100) == ModelTier.BEST


class TestHardTriggerEvaluator:
    """Test cases for hard trigger evaluation."""
    
    def test_high_stakes_triggers(self):
        """Test that high_stakes triggers BEST."""
        features = PromptFeatures(
            len_chars=50,
            len_words=10,
            has_code_block=False,
            has_stack_trace=False,
            multi_part=False,
            strict_format=False,
            freshness_need=False,
            hard_reasoning=False,
            high_stakes=True,
        )
        result = HardTriggerEvaluator.evaluate(features)
        
        assert result.triggered
        assert "high_stakes" in result.reasons[0]
    
    def test_stack_trace_triggers(self):
        """Test that has_stack_trace triggers BEST."""
        features = PromptFeatures(
            len_chars=50,
            len_words=10,
            has_code_block=False,
            has_stack_trace=True,
            multi_part=False,
            strict_format=False,
            freshness_need=False,
            hard_reasoning=False,
            high_stakes=False,
        )
        result = HardTriggerEvaluator.evaluate(features)
        
        assert result.triggered
        assert "stack_trace" in result.reasons[0]
    
    def test_hard_reasoning_and_multi_part_triggers(self):
        """Test that hard_reasoning AND multi_part triggers BEST."""
        features = PromptFeatures(
            len_chars=50,
            len_words=10,
            has_code_block=False,
            has_stack_trace=False,
            multi_part=True,
            strict_format=False,
            freshness_need=False,
            hard_reasoning=True,
            high_stakes=False,
        )
        result = HardTriggerEvaluator.evaluate(features)
        
        assert result.triggered
        assert "hard_reasoning AND multi_part" in result.reasons[0]
    
    def test_hard_reasoning_alone_does_not_trigger(self):
        """Test that hard_reasoning alone does not trigger."""
        features = PromptFeatures(
            len_chars=50,
            len_words=10,
            has_code_block=False,
            has_stack_trace=False,
            multi_part=False,
            strict_format=False,
            freshness_need=False,
            hard_reasoning=True,
            high_stakes=False,
        )
        result = HardTriggerEvaluator.evaluate(features)
        
        assert not result.triggered
    
    def test_no_triggers_on_simple_prompt(self):
        """Test that simple prompts don't trigger."""
        features = PromptFeatures(
            len_chars=50,
            len_words=10,
            has_code_block=False,
            has_stack_trace=False,
            multi_part=False,
            strict_format=False,
            freshness_need=False,
            hard_reasoning=False,
            high_stakes=False,
        )
        result = HardTriggerEvaluator.evaluate(features)
        
        assert not result.triggered
        assert len(result.reasons) == 0


class TestSelfEvalParser:
    """Test cases for self-eval response parsing."""
    
    def test_parse_valid_json(self):
        """Test parsing valid self-eval JSON."""
        response = '''{"answer": "The answer is 42", "confidence": 0.9, "should_escalate": false, "reasons": []}'''
        result = SelfEvalParser.parse_response(response)
        
        assert result.answer == "The answer is 42"
        assert result.confidence == 0.9
        assert result.should_escalate == False
        assert result.parse_error == False
    
    def test_parse_json_with_markdown_wrapper(self):
        """Test parsing JSON wrapped in markdown."""
        response = '''Here's my response:
```json
{"answer": "Hello world", "confidence": 0.85, "should_escalate": false, "reasons": ["all good"]}
```'''
        result = SelfEvalParser.parse_response(response)
        
        # Should extract the JSON even with wrapper
        assert "Hello world" in result.answer or result.parse_error
    
    def test_parse_invalid_json_fails_closed(self):
        """Test that invalid JSON fails closed."""
        response = "This is not JSON at all"
        result = SelfEvalParser.parse_response(response)
        
        assert result.parse_error
        assert result.should_escalate == True
        assert result.confidence == 0.0
    
    def test_parse_missing_answer_fails_closed(self):
        """Test that missing answer key fails closed."""
        response = '''{"confidence": 0.9, "should_escalate": false}'''
        result = SelfEvalParser.parse_response(response)
        
        assert result.parse_error
        assert result.should_escalate == True
    
    def test_confidence_clamped_to_valid_range(self):
        """Test that confidence is clamped to [0, 1]."""
        response = '''{"answer": "test", "confidence": 1.5, "should_escalate": false, "reasons": []}'''
        result = SelfEvalParser.parse_response(response)
        
        assert result.confidence == 1.0
    
    def test_should_escalate_with_low_confidence(self):
        """Test escalation decision with low confidence."""
        result = SelfEvalParser.parse_response(
            '''{"answer": "test", "confidence": 0.5, "should_escalate": false, "reasons": []}'''
        )
        
        # Should escalate because confidence < 0.75
        assert SelfEvalParser.should_escalate(result)
    
    def test_should_not_escalate_with_high_confidence(self):
        """Test no escalation with high confidence."""
        result = SelfEvalParser.parse_response(
            '''{"answer": "test", "confidence": 0.9, "should_escalate": false, "reasons": []}'''
        )
        
        assert not SelfEvalParser.should_escalate(result)
    
    def test_should_escalate_when_flagged(self):
        """Test escalation when should_escalate is true."""
        result = SelfEvalParser.parse_response(
            '''{"answer": "test", "confidence": 0.95, "should_escalate": true, "reasons": ["complex query"]}'''
        )
        
        # Should escalate because should_escalate=true, even with high confidence
        assert SelfEvalParser.should_escalate(result)


class TestModelRouter:
    """Test cases for model router."""
    
    def test_force_mode_uses_client_model(self):
        """Test that FORCE mode uses the client's model."""
        routing = ModelRouter.route(
            prompt="Simple question",
            client_model="gpt-4-turbo",
            route_mode=RouteMode.FORCE
        )
        
        assert routing.final_model == "gpt-4-turbo"
        assert routing.score == 0  # Not computed in force mode
    
    def test_auto_mode_ignores_client_model(self):
        """Test that AUTO mode ignores the client's model."""
        routing = ModelRouter.route(
            prompt="Simple question",
            client_model="gpt-4-turbo",
            route_mode=RouteMode.AUTO
        )
        
        # Simple question should route to CHEAP, not use client model
        assert routing.initial_tier == ModelTier.CHEAP
        assert routing.initial_model == "gpt-3.5-turbo"
    
    def test_high_stakes_routes_to_best(self):
        """Test that high stakes prompts route to BEST."""
        routing = ModelRouter.route(
            prompt="What is the correct dosage for this medication?",
            route_mode=RouteMode.AUTO
        )
        
        assert routing.initial_tier == ModelTier.BEST
        assert routing.hard_triggers.triggered
    
    def test_simple_prompt_routes_to_cheap(self):
        """Test that simple prompts route to CHEAP."""
        routing = ModelRouter.route(
            prompt="What is Python?",
            route_mode=RouteMode.AUTO
        )
        
        assert routing.initial_tier == ModelTier.CHEAP
        assert not routing.hard_triggers.triggered
    
    def test_escalation_tiers(self):
        """Test tier escalation logic."""
        assert ModelRouter.get_escalated_tier(ModelTier.CHEAP) == ModelTier.MID
        assert ModelRouter.get_escalated_tier(ModelTier.MID) == ModelTier.BEST
        assert ModelRouter.get_escalated_tier(ModelTier.BEST) == ModelTier.BEST
    
    def test_skip_self_eval_for_best(self):
        """Test that self-eval is skipped for BEST tier."""
        assert ModelRouter.should_skip_self_eval(ModelTier.BEST)
        assert not ModelRouter.should_skip_self_eval(ModelTier.CHEAP)
        assert not ModelRouter.should_skip_self_eval(ModelTier.MID)


class TestModelHelpers:
    """Test cases for model helper functions."""
    
    def test_get_model_for_tier(self):
        """Test getting model for tier."""
        assert get_model_for_tier(ModelTier.CHEAP) == "gpt-3.5-turbo"
        assert get_model_for_tier(ModelTier.MID) == "gpt-4"
        assert get_model_for_tier(ModelTier.BEST) == "gpt-4-turbo"
    
    def test_get_tier_for_model(self):
        """Test getting tier for model."""
        assert get_tier_for_model("gpt-3.5-turbo") == ModelTier.CHEAP
        assert get_tier_for_model("gpt-4") == ModelTier.MID
        assert get_tier_for_model("gpt-4-turbo") == ModelTier.BEST
        assert get_tier_for_model("unknown-model") is None
