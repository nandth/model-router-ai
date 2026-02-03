"""Main router service orchestrating prompt routing."""
from typing import Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.difficulty_estimator import DifficultyEstimator
from app.services.routing_policy import RoutingPolicy, ModelConfig
from app.services.llm_client import LLMClient, LLMClientError
from app.services.budget_service import BudgetService
from app.models.database import RequestLog


class RouterService:
    """Main service for routing prompts to LLM models."""
    
    def __init__(self):
        """Initialize router service."""
        self.difficulty_estimator = DifficultyEstimator()
        self.llm_client = LLMClient()
        self.budget_service = BudgetService()
    
    def route_prompt(self, prompt: str, db: Session, max_tokens: int = 1000) -> Dict:
        """
        Route a prompt to the appropriate LLM model.
        
        Args:
            prompt: User prompt
            db: Database session
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dictionary with response and metadata
        """
        # Step 1: Estimate difficulty
        difficulty_score, difficulty_level = self.difficulty_estimator.estimate(prompt)
        
        # Step 2: Select model based on difficulty
        selected_model = RoutingPolicy.select_model(difficulty_score, difficulty_level)
        
        # Step 3: Estimate cost (rough estimate based on prompt length)
        estimated_input_tokens = len(prompt.split()) * 1.3  # Rough estimate
        estimated_cost = ModelConfig.estimate_cost(
            selected_model,
            int(estimated_input_tokens),
            max_tokens
        )
        
        # Step 4: Check budget
        if not self.budget_service.check_budget(db, estimated_cost):
            return {
                "success": False,
                "error": "Monthly budget limit exceeded",
                "budget_status": self.budget_service.get_budget_status(db)
            }
        
        # Step 5: Call LLM with retry logic
        retry_count = 0
        escalated = False
        current_model = selected_model
        
        while retry_count < 3:
            try:
                response_text, input_tokens, output_tokens, latency_ms = self.llm_client.call_model(
                    current_model, prompt, max_tokens
                )
                
                # Calculate actual cost
                actual_cost = ModelConfig.estimate_cost(current_model, input_tokens, output_tokens)
                
                # Step 6: Check if we should escalate
                if retry_count == 0 and self.llm_client.should_escalate(response_text):
                    # Try escalating to a stronger model
                    escalated_model = RoutingPolicy.select_model(
                        difficulty_score, difficulty_level,
                        previous_model=current_model,
                        escalate=True
                    )
                    
                    if escalated_model != current_model:
                        # Log the initial attempt
                        self._log_request(
                            db, prompt, difficulty_score, current_model,
                            input_tokens, output_tokens, actual_cost, latency_ms,
                            success=True, retry_count=0, escalated=1,
                            response_text=response_text
                        )
                        
                        # Try with escalated model
                        current_model = escalated_model
                        escalated = True
                        continue
                
                # Success - log and return
                self._log_request(
                    db, prompt, difficulty_score, current_model,
                    input_tokens, output_tokens, actual_cost, latency_ms,
                    success=True, retry_count=retry_count, escalated=1 if escalated else 0,
                    response_text=response_text
                )
                
                # Update budget
                self.budget_service.update_spending(db, actual_cost)
                
                return {
                    "success": True,
                    "response": response_text,
                    "model_used": current_model,
                    "difficulty_score": difficulty_score,
                    "difficulty_level": difficulty_level,
                    "tokens_used": input_tokens + output_tokens,
                    "cost": actual_cost,
                    "latency_ms": latency_ms,
                    "escalated": escalated,
                    "retry_count": retry_count
                }
                
            except LLMClientError as e:
                retry_count += 1
                
                if retry_count >= 3:
                    # Final failure - log and return error
                    self._log_request(
                        db, prompt, difficulty_score, current_model,
                        0, 0, 0.0, 0.0,
                        success=False, retry_count=retry_count, escalated=1 if escalated else 0,
                        error_message=str(e)
                    )
                    
                    return {
                        "success": False,
                        "error": f"Failed after {retry_count} retries: {str(e)}",
                        "model_attempted": current_model,
                        "difficulty_score": difficulty_score
                    }
        
        # Should not reach here
        return {
            "success": False,
            "error": "Unexpected error in routing"
        }
    
    def _log_request(self, db: Session, prompt: str, difficulty_score: float,
                     model: str, input_tokens: int, output_tokens: int,
                     cost: float, latency_ms: float, success: bool = True,
                     retry_count: int = 0, escalated: int = 0,
                     response_text: Optional[str] = None,
                     error_message: Optional[str] = None) -> None:
        """Log request to database."""
        log_entry = RequestLog(
            timestamp=datetime.utcnow(),
            prompt=prompt[:500],  # Truncate long prompts
            difficulty_score=difficulty_score,
            model_used=model,
            tokens_used=input_tokens + output_tokens,
            cost=cost,
            latency_ms=latency_ms,
            success=1 if success else 0,
            retry_count=retry_count,
            escalated=escalated,
            response_text=response_text[:1000] if response_text else None,  # Truncate
            error_message=error_message
        )
        
        db.add(log_entry)
        db.commit()
    
    def get_statistics(self, db: Session, limit: int = 100) -> Dict:
        """
        Get usage statistics.
        
        Args:
            db: Database session
            limit: Number of recent requests to include
            
        Returns:
            Dictionary with statistics
        """
        # Get recent requests
        recent_requests = db.query(RequestLog).order_by(
            RequestLog.timestamp.desc()
        ).limit(limit).all()
        
        if not recent_requests:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "success_rate": 0.0,
                "total_cost": 0.0,
                "avg_latency_ms": 0.0,
                "total_tokens": 0,
                "escalation_rate": 0.0
            }
        
        # Calculate statistics
        total_requests = len(recent_requests)
        successful = sum(1 for r in recent_requests if r.success == 1)
        failed = total_requests - successful
        total_cost = sum(r.cost for r in recent_requests)
        avg_latency = sum(r.latency_ms for r in recent_requests) / total_requests
        total_tokens = sum(r.tokens_used for r in recent_requests)
        escalated = sum(1 for r in recent_requests if r.escalated == 1)
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful,
            "failed_requests": failed,
            "success_rate": (successful / total_requests * 100) if total_requests > 0 else 0,
            "total_cost": round(total_cost, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "total_tokens": total_tokens,
            "escalation_rate": (escalated / total_requests * 100) if total_requests > 0 else 0,
            "recent_requests": [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "model": r.model_used,
                    "difficulty_score": r.difficulty_score,
                    "success": bool(r.success),
                    "cost": r.cost,
                    "latency_ms": r.latency_ms,
                    "escalated": bool(r.escalated)
                }
                for r in recent_requests[:10]  # Show only 10 most recent
            ]
        }
