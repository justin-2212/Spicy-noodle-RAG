"""Application settings and configuration."""

from typing import Optional
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """PostgreSQL database configuration."""
    
    model_config = ConfigDict(env_prefix="DB_", env_file=".env", extra="ignore")
    
    url: str = "postgresql://postgres:justinthang2005@localhost:5432/mi-cay"
    echo: bool = False
    pool_size: int = 10


class VectorStoreSettings(BaseSettings):
    """Qdrant vector store configuration."""
    
    model_config = ConfigDict(env_prefix="QDRANT_", env_file=".env", extra="ignore")
    
    host: str = "localhost"
    port: int = 6333
    collection_name: str = "products"
    vector_size: int = 1024  # BGE-M3 dimension


class EmbeddingSettings(BaseSettings):
    """Embedding model configuration."""
    
    model_config = ConfigDict(env_prefix="EMBEDDING_", env_file=".env", extra="ignore")
    
    model_name: str = "BAAI/bge-m3"
    device: str = "cpu"  # or "cuda"
    batch_size: int = 32
    cache_dir: str = "./models/embeddings"


class RerankerSettings(BaseSettings):
    """Reranker model configuration."""
    
    model_config = ConfigDict(env_prefix="RERANKER_")
    
    model_name: str = "BAAI/bge-reranker-v2-m3"
    device: str = "cpu"
    batch_size: int = 64
    cache_dir: str = "./models/reranker"


class LLMSettings(BaseSettings):
    """Language model configuration."""
    
    model_config = ConfigDict(env_prefix="LLM_", env_file=".env", extra="ignore")
    
    provider: str = "gemini"  # "gemini" or "groq"
    use_fallback: bool = True
    
    gemini_api_key: Optional[str] = None
    gemini_model_name: str = "gemini-2.5-flash"
    
    groq_api_key: Optional[str] = None
    groq_model_name: str = "llama-3.3-70b-versatile"
    
    temperature: float = 0.7
    max_tokens: int = 1024


class RetrievalSettings(BaseSettings):
    """Retrieval configuration."""
    
    model_config = ConfigDict(env_prefix="RETRIEVAL_")
    
    dense_top_k: int = 30
    sparse_top_k: int = 30
    hybrid_top_k: int = 20
    rerank_top_k: int = 10
    dense_weight: float = 0.5
    sparse_weight: float = 0.5


class Settings(BaseSettings):
    """Main application settings."""
    
    # API
    app_name: str = "RAG Spicy Noodle Service"
    app_version: str = "0.1.0"
    api_title: str = "RAG Spicy Noodle Recommendation API"
    api_description: str = "Intelligent spicy noodle recommendation service"
    fastapi_debug: bool = False
    
    # Port
    fastapi_port: int = 8000
    fastapi_host: str = "0.0.0.0"
    
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
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Global settings instance
settings = Settings()
