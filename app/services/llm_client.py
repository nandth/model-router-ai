"""Simple OpenAI client for sending prompts to ChatGPT."""
import os
from typing import Tuple
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMClientError(Exception):
    """Base exception for LLM client errors."""
    pass


class LLMClient:
    """Simple client for interacting with OpenAI API."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Check if API key is set and looks valid (starts with 'sk-')
        if not self.openai_api_key or not self.openai_api_key.startswith("sk-"):
            raise LLMClientError(
                "OpenAI API key not configured. Please set OPENAI_API_KEY in .env file"
            )
        
        self.openai_client = OpenAI(api_key=self.openai_api_key)
    
    def send_prompt(self, prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 1000) -> Tuple[str, int]:
        """
        Send a prompt to ChatGPT and get a response.
        
        Args:
            prompt: The prompt to send
            model: Model name (e.g., "gpt-3.5-turbo", "gpt-4")
            max_tokens: Maximum tokens to generate
            
        Returns:
            Tuple of (response_text, total_tokens_used)
        """
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            
            response_text = response.choices[0].message.content
            total_tokens = response.usage.total_tokens
            
            return response_text, total_tokens
            
        except Exception as e:
            raise LLMClientError(f"OpenAI API error: {str(e)}")
