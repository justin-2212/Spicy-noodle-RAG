"""Base classes for reranking."""

from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel


class RerankerResult(BaseModel):
    """Result from reranker."""
    
    id: str
    text: str
    score: float
    metadata: dict


class BaseReranker(ABC):
    """Abstract base class for rerankers."""
    
    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: List[dict],
        top_k: int = 5
    ) -> List[RerankerResult]:
        """
        Rerank documents for query relevance.
        
        Args:
            query: User query
            documents: List of documents to rerank
            top_k: Number of results to return
            
        Returns:
            Reranked results
        """
        pass
