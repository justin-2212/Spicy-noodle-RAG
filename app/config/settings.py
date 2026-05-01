"""Application settings and configuration."""

from typing import Optional
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """PostgreSQL database configuration."""
    
    url: str = "postgresql://user:password@localhost:5432/food_db"
    echo: bool = False
    pool_size: int = 10
    
    class Config:
        env_prefix = "DB_"


class VectorStoreSettings(BaseSettings):
    """Qdrant vector store configuration."""
    
    host: str = "localhost"
    port: int = 6333
    collection_name: str = "food_items"
    vector_size: int = 1024  # BGE-M3 dimension
    
    class Config:
        env_prefix = "QDRANT_"


class EmbeddingSettings(BaseSettings):
    """Embedding model configuration."""
    
    model_name: str = "BAAI/bge-m3"
    device: str = "cuda"  # or "cpu"
    batch_size: int = 32
    cache_dir: str = "./models/embeddings"
    
    class Config:
        env_prefix = "EMBEDDING_"


class RerankerSettings(BaseSettings):
    """Reranker model configuration."""
    
    model_name: str = "BAAI/bge-reranker-base"
    device: str = "cuda"
    batch_size: int = 64
    cache_dir: str = "./models/reranker"
    
    class Config:
        env_prefix = "RERANKER_"


class LLMSettings(BaseSettings):
    """Language model configuration."""
    
    provider: str = "gemini"  # "gemini" or "groq"
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    model_name: str = "gemini-pro"  # or "mixtral-8x7b-32768"
    temperature: float = 0.7
    max_tokens: int = 1024
    
    class Config:
        env_prefix = "LLM_"


class RetrievalSettings(BaseSettings):
    """Retrieval configuration."""
    
    dense_top_k: int = 20
    sparse_top_k: int = 20
    hybrid_top_k: int = 10
    rerank_top_k: int = 5
    dense_weight: float = 0.6
    sparse_weight: float = 0.4
    
    class Config:
        env_prefix = "RETRIEVAL_"


class Settings(BaseSettings):
    """Main application settings."""
    
    # API
    app_name: str = "RAG Food Service"
    app_version: str = "0.1.0"
    api_title: str = "RAG Food Recommendation API"
    api_description: str = "Intelligent food recommendation service"
    debug: bool = False
    
    # Port
    port: int = 8000
    host: str = "0.0.0.0"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"
    
    # Nested settings
    database: DatabaseSettings = DatabaseSettings()
    vector_store: VectorStoreSettings = VectorStoreSettings()
    embedding: EmbeddingSettings = EmbeddingSettings()
    reranker: RerankerSettings = RerankerSettings()
    llm: LLMSettings = LLMSettings()
    retrieval: RetrievalSettings = RetrievalSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
