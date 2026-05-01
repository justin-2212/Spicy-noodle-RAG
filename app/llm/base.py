"""Base classes for LLM providers."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM provider.
        
        Args:
            api_key: API key for the provider
        """
        self.api_key = api_key
    
    @abstractmethod
    async def generate(
        self,
        query: str,
        context: str,
        system_prompt: str = ""
    ) -> str:
        """
        Generate response (non-streaming).
        
        Args:
            query: User query
            context: Retrieved context from RAG
            system_prompt: System instructions
            
        Returns:
            Generated response
        """
        pass
    
    @abstractmethod
    async def stream(
        self,
        query: str,
        context: str,
        system_prompt: str = ""
    ) -> AsyncGenerator[str, None]:
        """
        Stream response token-by-token.
        
        Args:
            query: User query
            context: Retrieved context from RAG
            system_prompt: System instructions
            
        Yields:
            Response tokens
        """
        pass
