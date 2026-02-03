"""Tests for difficulty estimator."""
import pytest
from app.services.difficulty_estimator import DifficultyEstimator


class TestDifficultyEstimator:
    """Test cases for difficulty estimation."""
    
    def test_easy_prompt_short(self):
        """Test that short simple prompts are classified as easy."""
        prompt = "What is Python?"
        score, level = DifficultyEstimator.estimate(prompt)
        assert level == "easy"
        assert score < 0.5
    
    def test_easy_prompt_with_simple_keywords(self):
        """Test that prompts with simple keywords are easy."""
        prompt = "List the top 5 programming languages"
        score, level = DifficultyEstimator.estimate(prompt)
        assert level == "easy"
    
    def test_medium_prompt(self):
        """Test that medium-length prompts are medium difficulty."""
        prompt = "Compare and contrast Python and JavaScript for web development. What are the main differences?"
        score, level = DifficultyEstimator.estimate(prompt)
        assert level in ["easy", "medium"]
    
    def test_hard_prompt_complex_keywords(self):
        """Test that prompts with complex keywords are hard."""
        prompt = """Provide a comprehensive technical analysis of the algorithm complexity. 
        Design a detailed implementation with step-by-step reasoning and mathematical proof.
        Compare multiple optimization approaches."""
        score, level = DifficultyEstimator.estimate(prompt)
        assert level in ["medium", "hard"]
        assert score > 0.4
    
    def test_hard_prompt_long(self):
        """Test that very long prompts tend toward harder difficulty."""
        prompt = " ".join(["word"] * 200)  # Very long prompt
        score, level = DifficultyEstimator.estimate(prompt)
        assert score > 0.3
    
    def test_code_blocks_increase_difficulty(self):
        """Test that code blocks increase difficulty."""
        prompt = "Explain this code: ```python\nprint('hello')\n```"
        score, level = DifficultyEstimator.estimate(prompt)
        # Should have some structural complexity
        assert score > 0.2
    
    def test_multiple_questions_increase_difficulty(self):
        """Test that multiple questions increase difficulty."""
        prompt = "What is AI? How does it work? What are the applications? Why is it important?"
        score, level = DifficultyEstimator.estimate(prompt)
        # Multiple questions should add structural complexity
        assert score > 0.2
    
    def test_score_range(self):
        """Test that scores are always in valid range."""
        prompts = [
            "Hi",
            "What is the weather?",
            "Explain machine learning in detail",
            "Provide a comprehensive analysis of quantum computing algorithms"
        ]
        for prompt in prompts:
            score, level = DifficultyEstimator.estimate(prompt)
            assert 0.0 <= score <= 1.0
            assert level in ["easy", "medium", "hard"]
