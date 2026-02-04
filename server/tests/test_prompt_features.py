"""Tests for prompt feature extraction."""
import pytest
from app.services.prompt_features import PromptFeatureExtractor, DifficultyScorer, PromptFeatures


class TestPromptFeatureExtractor:
    """Test cases for prompt feature extraction."""
    
    def test_basic_extraction(self):
        """Test basic feature extraction."""
        prompt = "What is Python?"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.len_chars == len(prompt)
        assert features.len_words == 3
        assert not features.has_code_block
        assert not features.has_stack_trace
        assert not features.multi_part
        assert not features.strict_format
        assert not features.freshness_need
        assert not features.hard_reasoning
        assert not features.high_stakes
    
    def test_code_block_detection(self):
        """Test detection of code blocks."""
        prompt = "Explain this code:\n```python\nprint('hello')\n```"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.has_code_block
    
    def test_stack_trace_detection_traceback(self):
        """Test detection of Python traceback."""
        prompt = "I got this error: Traceback (most recent call last)"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.has_stack_trace
    
    def test_stack_trace_detection_exception(self):
        """Test detection of exception mentions."""
        prompt = "Getting NullPointerException in my Java code"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.has_stack_trace
    
    def test_stack_trace_detection_segfault(self):
        """Test detection of segfault."""
        prompt = "My C program crashes with segfault"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.has_stack_trace
    
    def test_multi_part_numbered(self):
        """Test detection of numbered multi-part structure."""
        prompt = "Please help with: 1) setup 2) configuration 3) deployment"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.multi_part
    
    def test_multi_part_ordinal(self):
        """Test detection of ordinal multi-part structure."""
        prompt = "First explain X, then second describe Y, third show Z"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.multi_part
    
    def test_multi_part_multiple_questions(self):
        """Test detection of multiple question marks."""
        prompt = "What is X? How does Y work? When should I use Z?"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.multi_part
    
    def test_strict_format_json(self):
        """Test detection of JSON format requirement."""
        prompt = "Return the result as JSON"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.strict_format
    
    def test_strict_format_schema(self):
        """Test detection of schema requirement."""
        prompt = "The output must match this schema"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.strict_format
    
    def test_strict_format_only_output(self):
        """Test detection of 'only output' requirement."""
        prompt = "Only output the final answer, nothing else"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.strict_format
    
    def test_freshness_need_latest(self):
        """Test detection of 'latest' freshness need."""
        prompt = "What are the latest updates to Python?"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.freshness_need
    
    def test_freshness_need_today(self):
        """Test detection of 'today' freshness need."""
        prompt = "What happened today in tech news?"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.freshness_need
    
    def test_freshness_need_current(self):
        """Test detection of 'current' freshness need."""
        prompt = "What is the current version of React?"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.freshness_need
    
    def test_hard_reasoning_prove(self):
        """Test detection of 'prove' hard reasoning."""
        prompt = "Prove that this algorithm is correct"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.hard_reasoning
    
    def test_hard_reasoning_optimize(self):
        """Test detection of 'optimize' hard reasoning."""
        prompt = "Optimize this code for performance"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.hard_reasoning
    
    def test_hard_reasoning_edge_cases(self):
        """Test detection of 'edge cases' hard reasoning."""
        prompt = "What edge cases should I consider?"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.hard_reasoning
    
    def test_high_stakes_medical(self):
        """Test detection of medical high stakes."""
        prompt = "What is the proper dosage for this medication?"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.high_stakes
    
    def test_high_stakes_legal(self):
        """Test detection of legal high stakes."""
        prompt = "Is this contract legally binding?"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.high_stakes
    
    def test_high_stakes_financial(self):
        """Test detection of financial high stakes."""
        prompt = "Should I invest in this stock? I need investment advice"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.high_stakes
    
    def test_high_stakes_tax(self):
        """Test detection of tax high stakes."""
        prompt = "How should I file my tax return?"
        features = PromptFeatureExtractor.extract(prompt)
        
        assert features.high_stakes


class TestDifficultyScorer:
    """Test cases for difficulty scoring."""
    
    def test_simple_prompt_low_score(self):
        """Test that simple prompts get low scores."""
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
        score = DifficultyScorer.compute_score(features)
        assert score == 0
    
    def test_code_block_adds_points(self):
        """Test that code blocks add to score."""
        features = PromptFeatures(
            len_chars=50,
            len_words=10,
            has_code_block=True,
            has_stack_trace=False,
            multi_part=False,
            strict_format=False,
            freshness_need=False,
            hard_reasoning=False,
            high_stakes=False,
        )
        score = DifficultyScorer.compute_score(features)
        assert score == 20  # code_or_stack weight
    
    def test_high_stakes_adds_points(self):
        """Test that high stakes add to score."""
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
        score = DifficultyScorer.compute_score(features)
        assert score == 25  # high_stakes weight
    
    def test_long_prompt_adds_points(self):
        """Test that long prompts add to score."""
        features = PromptFeatures(
            len_chars=3000,
            len_words=500,
            has_code_block=False,
            has_stack_trace=False,
            multi_part=False,
            strict_format=False,
            freshness_need=False,
            hard_reasoning=False,
            high_stakes=False,
        )
        score = DifficultyScorer.compute_score(features)
        assert score == 10  # long_prompt weight
    
    def test_very_long_prompt_adds_more_points(self):
        """Test that very long prompts add more to score."""
        features = PromptFeatures(
            len_chars=7000,
            len_words=1000,
            has_code_block=False,
            has_stack_trace=False,
            multi_part=False,
            strict_format=False,
            freshness_need=False,
            hard_reasoning=False,
            high_stakes=False,
        )
        score = DifficultyScorer.compute_score(features)
        assert score == 20  # very_long_prompt weight
    
    def test_combined_features_sum(self):
        """Test that multiple features sum up correctly."""
        features = PromptFeatures(
            len_chars=50,
            len_words=10,
            has_code_block=True,     # +20
            has_stack_trace=False,
            multi_part=True,          # +15
            strict_format=True,       # +10
            freshness_need=False,
            hard_reasoning=True,      # +20
            high_stakes=False,
        )
        score = DifficultyScorer.compute_score(features)
        assert score == 65  # 20 + 15 + 10 + 20
    
    def test_score_capped_at_100(self):
        """Test that score is capped at 100."""
        features = PromptFeatures(
            len_chars=10000,
            len_words=2000,
            has_code_block=True,      # +20
            has_stack_trace=True,     # already counted
            multi_part=True,          # +15
            strict_format=True,       # +10
            freshness_need=True,      # +15
            hard_reasoning=True,      # +20
            high_stakes=True,         # +25
        )
        score = DifficultyScorer.compute_score(features)
        assert score == 100  # capped
    
    def test_score_breakdown(self):
        """Test score breakdown calculation."""
        features = PromptFeatures(
            len_chars=50,
            len_words=10,
            has_code_block=True,
            has_stack_trace=False,
            multi_part=True,
            strict_format=False,
            freshness_need=False,
            hard_reasoning=False,
            high_stakes=False,
        )
        breakdown = DifficultyScorer.get_score_breakdown(features)
        
        assert breakdown["code_or_stack"] == 20
        assert breakdown["multi_part"] == 15
        assert breakdown["total"] == 35
