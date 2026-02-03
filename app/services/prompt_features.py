"""Prompt feature extraction for model routing."""
import re
from dataclasses import dataclass
from typing import List


@dataclass
class PromptFeatures:
    """Extracted features from a prompt for routing decisions."""
    
    # Length metrics
    len_chars: int
    len_words: int
    
    # Code indicators
    has_code_block: bool
    has_stack_trace: bool
    
    # Structure indicators
    multi_part: bool
    
    # Format requirements
    strict_format: bool
    
    # Freshness needs
    freshness_need: bool
    
    # Reasoning complexity
    hard_reasoning: bool
    
    # Risk level
    high_stakes: bool
    
    def to_dict(self) -> dict:
        """Convert features to dictionary for logging."""
        return {
            "len_chars": self.len_chars,
            "len_words": self.len_words,
            "has_code_block": self.has_code_block,
            "has_stack_trace": self.has_stack_trace,
            "multi_part": self.multi_part,
            "strict_format": self.strict_format,
            "freshness_need": self.freshness_need,
            "hard_reasoning": self.hard_reasoning,
            "high_stakes": self.high_stakes,
        }


class PromptFeatureExtractor:
    """Extract features from prompts for routing decisions."""
    
    # Stack trace indicators
    STACK_TRACE_PATTERNS = [
        r"traceback",
        r"stack\s*trace",
        r"exception",
        r"nullpointerexception",
        r"segfault",
        r"segmentation\s*fault",
        r"error\s*at\s*line",
        r"at\s+[\w\.]+\([\w\.]+:\d+\)",  # JVM-style stack trace (Java/Kotlin/Scala)
        r"file\s+\"[^\"]+\",\s*line\s+\d+",  # Python-style traceback
    ]
    
    # Multi-part indicators
    MULTI_PART_PATTERNS = [
        r"1\)\s*\w",
        r"2\)\s*\w",
        r"3\)\s*\w",
        r"\b(first|second|third|fourth|fifth)\b",
        r"\b(firstly|secondly|thirdly)\b",
        r"step\s*1\b",
        r"step\s*2\b",
        r"part\s*1\b",
        r"part\s*2\b",
    ]
    
    # Strict format indicators
    STRICT_FORMAT_PATTERNS = [
        r"\bjson\b",
        r"\bschema\b",
        r"exact\s*format",
        r"only\s*output",
        r"\brfc\b",
        r"must\s*validate",
        r"strict\s*format",
        r"output\s*only",
        r"respond\s*only\s*with",
        r"return\s*only",
    ]
    
    # Freshness need indicators
    FRESHNESS_PATTERNS = [
        r"\blatest\b",
        r"\btoday\b",
        r"\bcurrent\b",
        r"\bright\s*now\b",
        r"\bthis\s*week\b",
        r"\bthis\s*month\b",
        r"\brecently\b",
        r"\b20[2-3]\d\b",  # Years 2020-2039
        r"\bnow\b",
        r"\bup\s*to\s*date\b",
    ]
    
    # Hard reasoning indicators
    HARD_REASONING_PATTERNS = [
        r"\bprove\b",
        r"\bderive\b",
        r"\boptimize\b",
        r"\bcomplexity\b",
        r"\bedge\s*cases?\b",
        r"\bcorrectness\b",
        r"\barchitecture\b",
        r"\bformal\b",
        r"\btheorem\b",
        r"\bproof\b",
        r"\bmathematically\b",
        r"\bguarantee\b",
        r"\binvariant\b",
        r"\bverify\b",
        r"\bvalidate\b",
        r"\bassume\b",
        r"\bconstraint\b",
    ]
    
    # High stakes indicators
    HIGH_STAKES_PATTERNS = [
        # Medical
        r"\bmedical\b",
        r"\bdiagnosis\b",
        r"\bdosage\b",
        r"\bprescription\b",
        r"\bsymptoms?\b",
        r"\btreatment\b",
        r"\bmedication\b",
        r"\bhealth\s*condition\b",
        # Legal
        r"\blegal\b",
        r"\bcontract\b",
        r"\blawsuit\b",
        r"\blitigation\b",
        r"\battorney\b",
        r"\blawyer\b",
        r"\bcourt\b",
        r"\bliability\b",
        r"\bcompliance\b",
        # Financial
        r"\btax\b",
        r"\bfinancial\s*advice\b",
        r"\binvestment\s*advice\b",
        r"\bstock\s*recommendation\b",
        r"\btrade\s*recommendation\b",
        r"\bretirement\s*planning\b",
        r"\bmortgage\b",
        r"\bloan\s*advice\b",
        # Safety/Security
        r"\bsafety\s*critical\b",
        r"\bsecurity\s*vulnerability\b",
        r"\bharm\b",
        r"\bdangerous\b",
    ]
    
    @classmethod
    def extract(cls, prompt: str) -> PromptFeatures:
        """
        Extract features from a prompt.
        
        Args:
            prompt: The raw prompt text
            
        Returns:
            PromptFeatures with all extracted features
        """
        prompt_lower = prompt.lower()
        
        # Length metrics
        len_chars = len(prompt)
        len_words = len(prompt.split())
        
        # Code indicators
        has_code_block = "```" in prompt
        has_stack_trace = cls._matches_any_pattern(prompt_lower, cls.STACK_TRACE_PATTERNS)
        
        # Multi-part structure
        question_marks = prompt.count("?")
        has_multi_part_pattern = cls._matches_any_pattern(prompt_lower, cls.MULTI_PART_PATTERNS)
        multi_part = has_multi_part_pattern or question_marks >= 3
        
        # Strict format requirements
        strict_format = cls._matches_any_pattern(prompt_lower, cls.STRICT_FORMAT_PATTERNS)
        
        # Freshness need
        freshness_need = cls._matches_any_pattern(prompt_lower, cls.FRESHNESS_PATTERNS)
        
        # Hard reasoning
        hard_reasoning = cls._matches_any_pattern(prompt_lower, cls.HARD_REASONING_PATTERNS)
        
        # High stakes
        high_stakes = cls._matches_any_pattern(prompt_lower, cls.HIGH_STAKES_PATTERNS)
        
        return PromptFeatures(
            len_chars=len_chars,
            len_words=len_words,
            has_code_block=has_code_block,
            has_stack_trace=has_stack_trace,
            multi_part=multi_part,
            strict_format=strict_format,
            freshness_need=freshness_need,
            hard_reasoning=hard_reasoning,
            high_stakes=high_stakes,
        )
    
    @staticmethod
    def _matches_any_pattern(text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the given patterns."""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False


class DifficultyScorer:
    """Compute difficulty/risk score from prompt features."""
    
    # Scoring weights (tunable)
    WEIGHTS = {
        "code_or_stack": 20,      # has_code_block OR has_stack_trace
        "multi_part": 15,          # multi_part
        "hard_reasoning": 20,      # hard_reasoning
        "high_stakes": 25,         # high_stakes
        "freshness_need": 15,      # freshness_need
        "strict_format": 10,       # strict_format
        "long_prompt": 10,         # len_chars > 2000
        "very_long_prompt": 20,    # len_chars > 6000 (replaces long_prompt)
    }
    
    @classmethod
    def compute_score(cls, features: PromptFeatures) -> int:
        """
        Compute difficulty/risk score from features.
        
        Args:
            features: Extracted prompt features
            
        Returns:
            Score from 0-100
        """
        score = 0
        
        # Code or stack trace
        if features.has_code_block or features.has_stack_trace:
            score += cls.WEIGHTS["code_or_stack"]
        
        # Multi-part
        if features.multi_part:
            score += cls.WEIGHTS["multi_part"]
        
        # Hard reasoning
        if features.hard_reasoning:
            score += cls.WEIGHTS["hard_reasoning"]
        
        # High stakes
        if features.high_stakes:
            score += cls.WEIGHTS["high_stakes"]
        
        # Freshness need
        if features.freshness_need:
            score += cls.WEIGHTS["freshness_need"]
        
        # Strict format
        if features.strict_format:
            score += cls.WEIGHTS["strict_format"]
        
        # Length-based scoring
        if features.len_chars > 6000:
            score += cls.WEIGHTS["very_long_prompt"]
        elif features.len_chars > 2000:
            score += cls.WEIGHTS["long_prompt"]
        
        # Clamp to [0, 100]
        return max(0, min(100, score))
    
    @classmethod
    def get_score_breakdown(cls, features: PromptFeatures) -> dict:
        """Get detailed breakdown of how score was calculated."""
        breakdown = {
            "base": 0,
            "code_or_stack": cls.WEIGHTS["code_or_stack"] if (features.has_code_block or features.has_stack_trace) else 0,
            "multi_part": cls.WEIGHTS["multi_part"] if features.multi_part else 0,
            "hard_reasoning": cls.WEIGHTS["hard_reasoning"] if features.hard_reasoning else 0,
            "high_stakes": cls.WEIGHTS["high_stakes"] if features.high_stakes else 0,
            "freshness_need": cls.WEIGHTS["freshness_need"] if features.freshness_need else 0,
            "strict_format": cls.WEIGHTS["strict_format"] if features.strict_format else 0,
        }
        
        if features.len_chars > 6000:
            breakdown["length"] = cls.WEIGHTS["very_long_prompt"]
        elif features.len_chars > 2000:
            breakdown["length"] = cls.WEIGHTS["long_prompt"]
        else:
            breakdown["length"] = 0
        
        breakdown["total"] = sum(breakdown.values())
        return breakdown
