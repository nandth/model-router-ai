"""LLM client service with retry and escalation logic."""
import os
import time
from typing import Optional, Tuple, Dict
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import OpenAI, APIError, APIConnectionError
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class LLMClientError(Exception):
    """Base exception for LLM client errors."""
    pass


class LLMClient:
    """Client for interacting with LLM APIs."""
    
    def __init__(self):
        """Initialize LLM clients."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Initialize clients
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
        else:
            self.openai_client = None
        
        if self.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=self.anthropic_api_key)
        else:
            self.anthropic_client = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIError, APIConnectionError))
    )
    def call_openai(self, model: str, prompt: str, max_tokens: int = 1000) -> Tuple[str, int, int, float]:
        """
        Call OpenAI API with retry logic.
        
        Args:
            model: Model name (e.g., "gpt-3.5-turbo")
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Tuple of (response_text, input_tokens, output_tokens, latency_ms)
        """
        if not self.openai_client:
            raise LLMClientError("OpenAI API key not configured")
        
        start_time = time.time()
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            
            return response_text, input_tokens, output_tokens, latency_ms
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            raise LLMClientError(f"OpenAI API error: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def call_anthropic(self, model: str, prompt: str, max_tokens: int = 1000) -> Tuple[str, int, int, float]:
        """
        Call Anthropic API with retry logic.
        
        Args:
            model: Model name (e.g., "claude-2")
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Tuple of (response_text, input_tokens, output_tokens, latency_ms)
        """
        if not self.anthropic_client:
            raise LLMClientError("Anthropic API key not configured")
        
        start_time = time.time()
        
        try:
            message = self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = message.content[0].text
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            
            return response_text, input_tokens, output_tokens, latency_ms
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            raise LLMClientError(f"Anthropic API error: {str(e)}")
    
    def call_model(self, model: str, prompt: str, max_tokens: int = 1000) -> Tuple[str, int, int, float]:
        """
        Call the appropriate LLM based on model name.
        
        Args:
            model: Model name
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Tuple of (response_text, input_tokens, output_tokens, latency_ms)
        """
        # Import here to avoid circular dependency
        from app.services.routing_policy import ModelConfig
        
        config = ModelConfig.get_model_config(model)
        if not config:
            raise LLMClientError(f"Unknown model: {model}")
        
        provider = config["provider"]
        
        if provider == "openai":
            return self.call_openai(model, prompt, max_tokens)
        elif provider == "anthropic":
            return self.call_anthropic(model, prompt, max_tokens)
        else:
            raise LLMClientError(f"Unknown provider: {provider}")
    
    def should_escalate(self, response_text: str) -> bool:
        """
        Determine if response quality is low and should escalate.
        
        This is a simple heuristic - in production, you might use
        more sophisticated confidence scoring.
        
        Args:
            response_text: Model response
            
        Returns:
            True if should escalate to stronger model
        """
        # Check for common indicators of low confidence
        low_confidence_phrases = [
            "i'm not sure",
            "i don't know",
            "unclear",
            "cannot determine",
            "insufficient information",
            "i cannot",
            "i'm unable"
        ]
        
        response_lower = response_text.lower()
        
        # Very short responses might indicate difficulty
        if len(response_text) < 50:
            return True
        
        # Check for low confidence phrases
        for phrase in low_confidence_phrases:
            if phrase in response_lower:
                return True
        
        return False
