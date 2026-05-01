"""Application constants."""

# Model identifiers
EMBEDDING_MODEL = "BAAI/bge-m3"
RERANKER_MODEL = "BAAI/bge-reranker-base"

# Qdrant settings
QDRANT_COLLECTION = "food_items"
VECTOR_DIMENSION = 1024

# Citation settings
CITATION_FORMATS = {
    "apa": "{author}. {title}. {source}, {year}.",
    "mla": "{author}. \"{title}.\" {source}, {year}.",
    "chicago": "{author}. {title}. {source}, {year}."
}

# Default LLM models
LLM_MODELS = {
    "gemini": "gemini-pro",
    "groq": "mixtral-8x7b-32768",
}

# Retrieval defaults
DEFAULT_TOP_K = 10
DEFAULT_DENSE_WEIGHT = 0.6
DEFAULT_SPARSE_WEIGHT = 0.4

# Prompt templates
SYSTEM_PROMPT = """You are a helpful food recommendation assistant for a restaurant. 
You help customers find dishes that match their preferences, dietary requirements, and budget.
Always be friendly, professional, and provide personalized recommendations based on the available menu items."""

# Processing settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
MIN_CHUNK_SIZE = 100
