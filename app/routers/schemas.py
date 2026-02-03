"""API schemas for request/response models."""
from pydantic import BaseModel, Field
from typing import Optional


class PromptRequest(BaseModel):
    """Request model for prompt routing."""
    prompt: str = Field(..., min_length=1, description="The prompt text to route to an LLM")
    max_tokens: Optional[int] = Field(1000, ge=1, le=4000, description="Maximum tokens to generate")


class PromptResponse(BaseModel):
    """Response model for prompt routing."""
    success: bool
    response: Optional[str] = None
    model_used: Optional[str] = None
    difficulty_score: Optional[float] = None
    difficulty_level: Optional[str] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    latency_ms: Optional[float] = None
    escalated: Optional[bool] = None
    retry_count: Optional[int] = None
    error: Optional[str] = None


class BudgetStatus(BaseModel):
    """Budget status response."""
    year: int
    month: int
    monthly_limit: float
    total_spent: float
    remaining: float
    percentage_used: float
    request_count: int


class Statistics(BaseModel):
    """Statistics response."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    total_cost: float
    avg_latency_ms: float
    total_tokens: int
    escalation_rate: float
