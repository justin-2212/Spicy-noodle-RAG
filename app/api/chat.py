"""Chat API endpoints."""

import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

import langchain
langchain.verbose = False
langchain.debug = False
langchain.llm_cache = None

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
from app.retrieval.langchain_rag_chain import LangChainRAGChain
from app.llm.langchain_provider import LangChainLLMProvider
from app.utils.logger import logger

router = APIRouter()

# Initialize RAG chain (lazy loading or at startup)
_rag_chain = None

def get_rag_chain():
    global _rag_chain
    if _rag_chain is None:
        logger.info("Initializing RAG Chain...")
        llm = LangChainLLMProvider().get_llm()
        _rag_chain = LangChainRAGChain(llm)
    return _rag_chain

class ChatMessage(BaseModel):
    role: str # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    answer: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat requests using the RAG chain.
    """
    try:
        rag_chain = get_rag_chain()
        
        # Convert history to LangChain format if needed
        # Our LangChainRAGChain.generate expects List[Any] for history
        # For now, let's keep it simple and just pass the message
        # In a real app, we would map the history to LangChain Message objects
        
        # Map history to LangChain Message objects
        chat_history = []
        if request.history:
            from langchain_core.messages import HumanMessage, AIMessage
            for msg in request.history:
                if msg.role == 'user':
                    chat_history.append(HumanMessage(content=msg.content))
                elif msg.role == 'assistant':
                    chat_history.append(AIMessage(content=msg.content))

        answer = await rag_chain.generate(request.message, chat_history=chat_history)
        
        return ChatResponse(answer=answer)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
