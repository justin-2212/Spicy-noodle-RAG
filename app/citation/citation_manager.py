"""Citation extraction and formatting."""

from typing import List
from pydantic import BaseModel


class Citation(BaseModel):
    """Citation reference."""
    
    text: str
    source: str
    metadata: dict = {}


class CitationManager:
    """Extract and format citations from responses."""
    
    @staticmethod
    def extract_citations(
        response: str,
        retrieved_docs: List[dict]
    ) -> List[Citation]:
        """
        Extract citations from response.
        
        Args:
            response: LLM response text
            retrieved_docs: Retrieved documents
            
        Returns:
            List of citations
        """
        citations = []
        
        # Simple citation extraction:
        # Check if document text appears in response
        for doc in retrieved_docs:
            if doc.get("text") in response:
                citations.append(Citation(
                    text=doc.get("text", ""),
                    source=doc.get("source", ""),
                    metadata=doc.get("metadata", {})
                ))
        
        return citations
    
    @staticmethod
    def format_citation(citation: Citation, style: str = "text") -> str:
        """
        Format citation in given style.
        
        Args:
            citation: Citation to format
            style: Format style (text, apa, mla)
            
        Returns:
            Formatted citation
        """
        if style == "apa":
            return f"(Source: {citation.source})"
        elif style == "mla":
            return f"(MLA: {citation.source})"
        else:
            return f"[{citation.source}]"
