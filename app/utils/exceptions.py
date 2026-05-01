"""Custom exception hierarchy."""


class RAGException(Exception):
    """Base exception for RAG service."""
    
    def __init__(self, message: str, code: str = "RAG_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ConfigurationError(RAGException):
    """Configuration-related errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "CONFIG_ERROR")


class DatabaseError(RAGException):
    """Database connection or query errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR")


class EmbeddingError(RAGException):
    """Embedding generation errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "EMBEDDING_ERROR")


class VectorStoreError(RAGException):
    """Qdrant operations errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "VECTOR_STORE_ERROR")


class RetrievalError(RAGException):
    """Retrieval pipeline errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "RETRIEVAL_ERROR")


class RerankerError(RAGException):
    """Reranking errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "RERANKER_ERROR")


class LLMError(RAGException):
    """LLM provider errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "LLM_ERROR")


class MemoryError(RAGException):
    """Memory management errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "MEMORY_ERROR")
