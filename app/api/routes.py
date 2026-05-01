"""API routes."""

from fastapi import APIRouter, Depends
from app.api.models import ChatRequest, ChatResponse, HealthResponse, StatusResponse
from app.utils.logger import logger

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint with RAG.
    
    This endpoint:
    1. Retrieves relevant menu items
    2. Reranks for quality
    3. Generates recommendation with LLM
    4. Optionally streams response
    
    Args:
        request: ChatRequest with query and options
        
    Returns:
        ChatResponse with recommendations
    """
    # TODO: Implement full pipeline
    # 1. Retrieve context
    # 2. Rerank results
    # 3. Generate response
    # 4. Extract citations
    
    return ChatResponse(
        response="Placeholder response",
        citations=[]
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    from app.config.settings import settings
    from datetime import datetime
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get service status."""
    # TODO: Check actual component status
    return StatusResponse(
        running=True,
        database_connected=False,
        vector_store_connected=False,
        llm_available=False,
        message="Service is running"
    )
