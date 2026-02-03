"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.database import init_db
from app.routers import api

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Model Router AI",
    description="Backend service that routes text prompts to different LLM APIs based on difficulty and cost constraints",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api.router, prefix="/api", tags=["api"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Model Router AI",
        "version": "1.0.0",
        "endpoints": {
            "route_prompt": "/api/prompt",
            "budget_status": "/api/budget",
            "statistics": "/api/stats",
            "health": "/api/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
