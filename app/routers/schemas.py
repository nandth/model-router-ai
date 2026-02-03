"""API schemas for request/response models."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class PromptRequest(BaseModel):
    """Request model for sending a prompt to ChatGPT."""
    prompt: str = Field(..., min_length=1, description="The prompt text to send to ChatGPT")
    model: Optional[str] = Field("gpt-3.5-turbo", description="OpenAI model to use (gpt-3.5-turbo or gpt-4)")
    max_tokens: Optional[int] = Field(1000, ge=1, le=4000, description="Maximum tokens to generate")


class PromptResponse(BaseModel):
    """Response model from ChatGPT."""
    model_config = ConfigDict(protected_namespaces=())
    
    response: str = Field(..., description="The response from ChatGPT")
    model: str = Field(..., description="The model that was used")
    tokens_used: int = Field(..., description="Total tokens used (input + output)")
    error: Optional[str] = None
