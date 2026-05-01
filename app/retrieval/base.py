"""Base classes for retrieval."""

from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel


class RetrievalResult(BaseModel):
    """Result from retrieval."""
    
    id: str
    text: str
    score: float
    metadata: dict


class BaseRetriever(ABC):
    """Abstract base class for retrievers."""
    
    @abstractmethod
    async def retrieve(
        self,
        query: str,
        top_k: int = 10
    ) -> List[RetrievalResult]:
        """
        Retrieve documents for query.
        
        Args:
            query: User query
            top_k: Number of results to return
            
        Returns:
            List of retrieval results
        """
        pass
