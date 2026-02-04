"""API schemas for request/response models."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, List, Optional
from enum import Enum


class RouteMode(str, Enum):
    """Routing mode for model selection."""
    AUTO = "auto"   # Server chooses model based on prompt analysis (default)
    FORCE = "force"  # Use client's requested model (for testing only)


class PromptRequest(BaseModel):
    """Request model for sending a prompt to ChatGPT."""
    prompt: str = Field(..., min_length=1, description="The prompt text to send to ChatGPT")
    model: Optional[str] = Field(
        "gpt-3.5-turbo", 
        description="Model hint (ignored in AUTO mode, used in FORCE mode)"
    )
    max_tokens: Optional[int] = Field(
        1000, 
        ge=1, 
        le=4000, 
        description="Maximum tokens to generate"
    )
    route_mode: Optional[RouteMode] = Field(
        RouteMode.AUTO,
        description="Routing mode: 'auto' (server chooses) or 'force' (use client model)"
    )


class RoutingDetails(BaseModel):
    """Details about the routing decision."""
    model_config = ConfigDict(protected_namespaces=())
    
    initial_tier: str = Field(..., description="Initial tier selected (cheap/mid/best)")
    final_tier: str = Field(..., description="Final tier after escalation")
    score: int = Field(..., description="Difficulty/risk score (0-100)")
    hard_triggers: List[str] = Field(default_factory=list, description="Hard triggers that fired")
    escalated: bool = Field(False, description="Whether escalation occurred")
    stage_a_confidence: Optional[float] = Field(None, description="Stage A self-eval confidence")
    stage_a_escalate: Optional[bool] = Field(None, description="Stage A escalation recommendation")


class PromptResponse(BaseModel):
    """Response model from ChatGPT with routing information."""
    model_config = ConfigDict(protected_namespaces=())
    
    success: bool = Field(True, description="Whether the request succeeded")
    response: str = Field(..., description="The response from ChatGPT")
    model_used: str = Field(..., description="The model that actually produced the response")
    tokens_used: int = Field(..., description="Total tokens used (input + output)")
    tier: Optional[str] = Field(None, description="Model tier used (cheap/mid/best)")
    latency_ms: Optional[float] = Field(None, description="Total latency in milliseconds")
    routing: Optional[RoutingDetails] = Field(None, description="Routing decision details")
    error: Optional[str] = Field(None, description="Error message if failed")
