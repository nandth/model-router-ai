"""Budget tracking and enforcement service."""
import os
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.database import MonthlyBudget
from dotenv import load_dotenv

load_dotenv()


class BudgetService:
    """Service for managing and enforcing budget limits."""
    
    def __init__(self):
        """Initialize budget service."""
        self.monthly_limit = float(os.getenv("MONTHLY_BUDGET_LIMIT", "100.0"))
    
    def check_budget(self, db: Session, estimated_cost: float) -> bool:
        """
        Check if request can proceed without exceeding budget.
        
        Args:
            db: Database session
            estimated_cost: Estimated cost of the request
            
        Returns:
            True if budget allows, False otherwise
        """
        current_spent = self.get_current_month_spending(db)
        return (current_spent + estimated_cost) <= self.monthly_limit
    
    def get_current_month_spending(self, db: Session) -> float:
        """Get total spending for current month."""
        now = datetime.utcnow()
        
        budget = db.query(MonthlyBudget).filter(
            MonthlyBudget.year == now.year,
            MonthlyBudget.month == now.month
        ).first()
        
        return budget.total_spent if budget else 0.0
    
    def update_spending(self, db: Session, cost: float) -> None:
        """
        Update monthly spending.
        
        Args:
            db: Database session
            cost: Cost to add to monthly spending
        """
        now = datetime.utcnow()
        
        budget = db.query(MonthlyBudget).filter(
            MonthlyBudget.year == now.year,
            MonthlyBudget.month == now.month
        ).first()
        
        if budget:
            budget.total_spent += cost
            budget.request_count += 1
            budget.last_updated = now
        else:
            budget = MonthlyBudget(
                year=now.year,
                month=now.month,
                total_spent=cost,
                request_count=1,
                last_updated=now
            )
            db.add(budget)
        
        db.commit()
    
    def get_budget_status(self, db: Session) -> dict:
        """
        Get current budget status.
        
        Returns:
            Dictionary with budget information
        """
        now = datetime.utcnow()
        current_spent = self.get_current_month_spending(db)
        
        budget = db.query(MonthlyBudget).filter(
            MonthlyBudget.year == now.year,
            MonthlyBudget.month == now.month
        ).first()
        
        return {
            "year": now.year,
            "month": now.month,
            "monthly_limit": self.monthly_limit,
            "total_spent": current_spent,
            "remaining": self.monthly_limit - current_spent,
            "percentage_used": (current_spent / self.monthly_limit * 100) if self.monthly_limit > 0 else 0,
            "request_count": budget.request_count if budget else 0
        }
