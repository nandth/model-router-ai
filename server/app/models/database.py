"""Database models for tracking LLM requests and budget."""
from sqlalchemy import Column, Integer, Float, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class RequestLog(Base):
    """Log of all LLM requests."""
    __tablename__ = "request_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    prompt = Column(String, nullable=False)
    difficulty_score = Column(Float, nullable=False)
    model_used = Column(String, nullable=False)
    tokens_used = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    latency_ms = Column(Float, nullable=False)
    success = Column(Integer, default=1)  # 1 for success, 0 for failure
    retry_count = Column(Integer, default=0)
    escalated = Column(Integer, default=0)  # 1 if escalated, 0 otherwise
    response_text = Column(String, nullable=True)
    error_message = Column(String, nullable=True)


class MonthlyBudget(Base):
    """Track monthly budget usage."""
    __tablename__ = "monthly_budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    total_spent = Column(Float, default=0.0)
    request_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)


# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./model_router.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
