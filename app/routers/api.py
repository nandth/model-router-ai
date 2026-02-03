"""API endpoints for the model router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.routers.schemas import PromptRequest, PromptResponse, BudgetStatus, Statistics
from app.services.router_service import RouterService
from app.services.budget_service import BudgetService

router = APIRouter()
router_service = RouterService()
budget_service = BudgetService()


@router.post("/prompt", response_model=PromptResponse)
async def route_prompt(request: PromptRequest, db: Session = Depends(get_db)):
    """
    Route a prompt to the appropriate LLM model.
    
    This endpoint:
    1. Estimates the difficulty of the prompt
    2. Selects an appropriate model based on difficulty
    3. Checks budget constraints
    4. Calls the LLM API with retry logic
    5. Escalates to stronger models if confidence is low
    6. Tracks latency and cost
    """
    try:
        result = router_service.route_prompt(request.prompt, db, request.max_tokens)
        return PromptResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/budget", response_model=BudgetStatus)
async def get_budget_status(db: Session = Depends(get_db)):
    """
    Get current monthly budget status.
    
    Returns information about:
    - Monthly budget limit
    - Total spent this month
    - Remaining budget
    - Percentage used
    - Number of requests this month
    """
    try:
        status = budget_service.get_budget_status(db)
        return BudgetStatus(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=Statistics)
async def get_statistics(limit: int = 100, db: Session = Depends(get_db)):
    """
    Get usage statistics.
    
    Returns statistics about recent requests:
    - Total/successful/failed requests
    - Total cost and average latency
    - Token usage
    - Escalation rate
    """
    try:
        stats = router_service.get_statistics(db, limit)
        return Statistics(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
