"""Difficulty estimator for LLM prompts."""
import re
from typing import Tuple

class DifficultyEstimator:
    """Estimates prompt difficulty based on length and keyword heuristics."""
    
    # Keywords indicating complex/difficult tasks
    COMPLEX_KEYWORDS = [
        "analyze", "complex", "detailed", "comprehensive", "explain",
        "reasoning", "logic", "proof", "theorem", "algorithm",
        "architecture", "design", "implementation", "optimize",
        "compare", "contrast", "evaluate", "critique", "research",
        "technical", "mathematical", "scientific", "engineering",
        "multi-step", "step-by-step", "elaborate", "in-depth"
    ]
    
    # Keywords indicating simple tasks
    SIMPLE_KEYWORDS = [
        "list", "name", "what is", "define", "yes or no",
        "simple", "basic", "quick", "brief", "short",
        "summarize", "tldr", "one sentence", "one word"
    ]
    
    # Length thresholds (in characters)
    SHORT_LENGTH = 100
    MEDIUM_LENGTH = 300
    
    @classmethod
    def estimate(cls, prompt: str) -> Tuple[float, str]:
        """
        Estimate difficulty of a prompt.
        
        Args:
            prompt: The input prompt text
            
        Returns:
            Tuple of (difficulty_score, difficulty_level)
            - difficulty_score: 0.0 to 1.0 (0=easy, 1=hard)
            - difficulty_level: "easy", "medium", or "hard"
        """
        score = 0.0
        
        # Factor 1: Prompt length (40% weight)
        length_score = cls._calculate_length_score(prompt)
        score += length_score * 0.4
        
        # Factor 2: Keyword analysis (40% weight)
        keyword_score = cls._calculate_keyword_score(prompt)
        score += keyword_score * 0.4
        
        # Factor 3: Structural complexity (20% weight)
        structure_score = cls._calculate_structure_score(prompt)
        score += structure_score * 0.2
        
        # Normalize to 0-1 range
        score = max(0.0, min(1.0, score))
        
        # Classify difficulty level
        if score < 0.33:
            difficulty_level = "easy"
        elif score < 0.67:
            difficulty_level = "medium"
        else:
            difficulty_level = "hard"
        
        return score, difficulty_level
    
    @classmethod
    def _calculate_length_score(cls, prompt: str) -> float:
        """Calculate score based on prompt length."""
        length = len(prompt)
        
        if length < cls.SHORT_LENGTH:
            return 0.2
        elif length < cls.MEDIUM_LENGTH:
            return 0.5
        else:
            # Scale up to 1.0 for very long prompts
            return min(1.0, 0.7 + (length - cls.MEDIUM_LENGTH) / 1000)
    
    @classmethod
    def _calculate_keyword_score(cls, prompt: str) -> float:
        """Calculate score based on keywords."""
        prompt_lower = prompt.lower()
        
        complex_count = sum(1 for keyword in cls.COMPLEX_KEYWORDS if keyword in prompt_lower)
        simple_count = sum(1 for keyword in cls.SIMPLE_KEYWORDS if keyword in prompt_lower)
        
        # More complex keywords -> higher score
        # More simple keywords -> lower score
        if complex_count > 0 and simple_count == 0:
            return min(1.0, 0.6 + complex_count * 0.1)
        elif simple_count > 0 and complex_count == 0:
            return max(0.0, 0.3 - simple_count * 0.1)
        elif complex_count > simple_count:
            return 0.7
        elif simple_count > complex_count:
            return 0.2
        else:
            return 0.5
    
    @classmethod
    def _calculate_structure_score(cls, prompt: str) -> float:
        """Calculate score based on structural complexity."""
        score = 0.0
        
        # Multiple sentences indicate complexity
        sentences = [s for s in re.split(r'[.!?]+', prompt) if s.strip()]
        if len(sentences) > 3:
            score += 0.3
        elif len(sentences) > 1:
            score += 0.15
        
        # Questions indicate complexity
        question_marks = prompt.count('?')
        if question_marks > 2:
            score += 0.3
        elif question_marks > 0:
            score += 0.15
        
        # Lists/bullets indicate structured requirements
        if any(char in prompt for char in ['-', '*', '1.', '2.']):
            score += 0.2
        
        # Code blocks or technical formatting
        if '```' in prompt or '`' in prompt:
            score += 0.2
        
        return min(1.0, score)
