"""Main FastAPI application for ChatGPT API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import api

# Create FastAPI app
app = FastAPI(
    title="ChatGPT API",
    description="Simple API to send prompts to ChatGPT",
    version="2.0.0"
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
        "name": "ChatGPT API",
        "version": "2.0.0",
        "description": "Simple API to send prompts to ChatGPT",
        "docs": "/docs",
        "endpoints": {
            "send_prompt": "/api/prompt",
            "health": "/api/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
