"""Simple API endpoint for sending prompts to ChatGPT."""
from fastapi import APIRouter, HTTPException

from app.routers.schemas import PromptRequest, PromptResponse
from app.services.llm_client import LLMClient, LLMClientError

router = APIRouter()

# Initialize the LLM client once
try:
    llm_client = LLMClient()
except LLMClientError as e:
    print(f"Warning: {e}")
    llm_client = None


@router.post("/prompt", response_model=PromptResponse)
async def send_prompt(request: PromptRequest):
    """
    Send a prompt to ChatGPT and get a response.
    
    This endpoint:
    1. Takes a prompt and optional model/max_tokens
    2. Sends it to OpenAI's ChatGPT API
    3. Returns the response
    """
    if llm_client is None:
        raise HTTPException(
            status_code=500, 
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY in .env file"
        )
    
    try:
        response_text, tokens_used = llm_client.send_prompt(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens
        )
        
        return PromptResponse(
            response=response_text,
            model=request.model,
            tokens_used=tokens_used
        )
    except LLMClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    api_key_status = "configured" if llm_client is not None else "not configured"
    return {
        "status": "healthy",
        "openai_api_key": api_key_status
    }
