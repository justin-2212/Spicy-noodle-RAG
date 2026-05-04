# """API request/response models."""

# from typing import List, Optional
# from pydantic import BaseModel


# class ChatRequest(BaseModel):
#     """Request for /chat endpoint."""
    
#     query: str
#     session_id: Optional[str] = None
#     stream: bool = True


# class CitationResult(BaseModel):
#     """Citation in response."""
    
#     text: str
#     source: str
#     page: Optional[int] = None


# class ChatResponse(BaseModel):
#     """Response from /chat endpoint."""
    
#     response: str
#     citations: List[CitationResult] = []
#     model: str = "unknown"


# class HealthResponse(BaseModel):
#     """Health check response."""
    
#     status: str
#     version: str
#     timestamp: str


# class StatusResponse(BaseModel):
#     """Service status response."""
    
#     running: bool
#     database_connected: bool
#     vector_store_connected: bool
#     llm_available: bool
#     message: str


# class ErrorResponse(BaseModel):
#     """Error response."""
    
#     error: str
#     code: str
#     message: str


# class IngestionResponse(BaseModel):
#     """Ingestion response."""
    
#     status: str
#     items_loaded: int
#     items_indexed: int
#     message: str

"""API request/response models."""

from typing import List, Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Single chat message."""
    
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request for /chat endpoint."""
    
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    """Response from /chat endpoint."""
    
    answer: str


class CitationResult(BaseModel):
    """Citation in response."""
    
    text: str
    source: str
    page: Optional[int] = None


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    version: str
    timestamp: str


class StatusResponse(BaseModel):
    """Service status response."""
    
    running: bool
    database_connected: bool
    vector_store_connected: bool
    llm_available: bool
    message: str


class ErrorResponse(BaseModel):
    """Error response."""
    
    error: str
    code: str
    message: str


class IngestionResponse(BaseModel):
    """Ingestion response."""
    
    status: str
    items_loaded: int
    items_indexed: int
    message: str