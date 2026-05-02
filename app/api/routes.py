"""API routes using LangChain."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.api.models import ChatRequest, ChatResponse
from app.config.settings import settings
from app.utils.logger import logger
from app.llm.langchain_provider import LangChainLLMProvider
from app.retrieval.langchain_rag_chain import LangChainRAGChain
from app.memory.langchain_memory import LangChainMemory

router = APIRouter()

# Initialize LLM with unified provider (including fallbacks)
base_llm = LangChainLLMProvider().get_llm()

# Initialize RAG chain
rag_chain = LangChainRAGChain(base_llm)

# Memory storage
session_memories = {}


@router.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint with LangChain RAG."""
    session_id = request.session_id or "default"
    
    # Get or create memory
    if session_id not in session_memories:
        session_memories[session_id] = LangChainMemory(base_llm, session_id)
    
    memory = session_memories[session_id]
    
    # Get chat history
    chat_history = memory.get_messages()
    
    # Add user message
    memory.add_message("user", request.query)
    
    if request.stream:
        # Streaming response
        async def response_generator():
            response_text = ""
            async for chunk in rag_chain.stream(
                request.query,
                chat_history=chat_history
            ):
                response_text += chunk
                yield f"data: {{'token': '{chunk}'}}\n\n"
            
            # Add assistant message to memory
            memory.add_message("assistant", response_text)
            
            # Send completion signal
            yield f"event: complete\ndata: {{'response': '{response_text}'}}\n\n"
        
        return StreamingResponse(response_generator(), media_type="text/event-stream")
    else:
        # Non-streaming response
        response = await rag_chain.generate(
            request.query,
            chat_history=chat_history
        )
        
        # Add to memory
        memory.add_message("assistant", response)
        
        return ChatResponse(
            response=response,
            model=f"{settings.llm.provider}+fallback" if settings.llm.use_fallback else settings.llm.provider
        )


@router.get("/health")
async def health_check():
    """Health check."""
    from datetime import datetime
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat()
    }