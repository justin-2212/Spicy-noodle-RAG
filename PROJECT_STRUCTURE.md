# Complete Project Structure

## Folder Tree

```
rag-chatbot-spicy-noodle/
│
├── 📋 Root Configuration Files
│   ├── README.md                    # Quick start guide for students
│   ├── .env.example                 # Environment variables template
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Container image
│   ├── docker-compose.yml           # Local development environment
│   ├── .gitignore                   # Git ignore patterns
│   └── .dockerignore                # Docker build ignore
│
├── 📁 app/ (Main Application - ~1,900 lines of code)
│   │
│   ├── main.py                      # FastAPI entry point (50 lines)
│   │   ├── App initialization
│   │   ├── Middleware setup
│   │   ├── Lifespan events (startup/shutdown)
│   │   └── Route registration
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py              # Pydantic BaseSettings (100 lines)
│   │   │   ├── Database settings
│   │   │   ├── Vector store settings
│   │   │   ├── Embedding settings
│   │   │   ├── Reranker settings
│   │   │   ├── LLM settings
│   │   │   ├── Retrieval settings
│   │   │   └── Global settings instance
│   │   │
│   │   └── constants.py             # App constants (40 lines)
│   │       ├── Model identifiers
│   │       ├── Qdrant settings
│   │       ├── Prompt templates
│   │       └── Processing defaults
│   │
│   ├── utils/ (Shared Utilities)
│   │   ├── __init__.py
│   │   ├── logger.py                # Structured logging (60 lines)
│   │   │   ├── JSONFormatter
│   │   │   ├── setup_logger()
│   │   │   └── Global logger
│   │   │
│   │   ├── db.py                    # Database utilities (90 lines)
│   │   │   ├── DatabasePool class
│   │   │   ├── Connection management
│   │   │   └── Session dependency injection
│   │   │
│   │   └── exceptions.py            # Custom exceptions (70 lines)
│   │       ├── RAGException (base)
│   │       ├── ConfigurationError
│   │       ├── DatabaseError
│   │       ├── EmbeddingError
│   │       ├── VectorStoreError
│   │       ├── RetrievalError
│   │       ├── RerankerError
│   │       ├── LLMError
│   │       └── MemoryError
│   │
│   ├── ingestion/ (Batch Pipeline)
│   │   ├── __init__.py
│   │   ├── pipeline.py              # Pipeline orchestrator (40 lines)
│   │   │   ├── IngestionPipeline class
│   │   │   └── run_ingestion()
│   │   │
│   │   ├── extractor.py             # Extract from PostgreSQL (STUB)
│   │   ├── processor.py             # Clean & normalize (STUB)
│   │   ├── chunker.py               # Document chunking (STUB)
│   │   └── indexer.py               # Index to Qdrant (STUB)
│   │
│   ├── embeddings/
│   │   ├── __init__.py
│   │   ├── base.py                  # Abstract interface (40 lines)
│   │   │   └── BaseEmbeddingModel
│   │   │
│   │   └── embedding_service.py     # BGE-M3 wrapper (STUB)
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── base.py                  # Abstract interfaces (60 lines)
│   │   │   ├── RetrievalResult
│   │   │   └── BaseRetriever
│   │   │
│   │   ├── dense_retriever.py       # HNSW search (STUB)
│   │   ├── sparse_retriever.py      # BM25 search (STUB)
│   │   ├── hybrid_retriever.py      # Hybrid orchestrator (STUB)
│   │   └── fusion.py                # Ranking fusion (STUB)
│   │
│   ├── reranking/
│   │   ├── __init__.py
│   │   ├── base.py                  # Abstract interface (40 lines)
│   │   │   └── BaseReranker
│   │   │
│   │   └── reranker.py              # BGE-Reranker wrapper (STUB)
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py                  # Abstract interface (50 lines)
│   │   │   └── BaseLLMProvider
│   │   │
│   │   ├── gemini_provider.py       # Gemini implementation (STUB)
│   │   ├── groq_provider.py         # Groq implementation (STUB)
│   │   └── streaming.py             # SSE helpers (STUB)
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   └── memory_manager.py        # Conversation memory (120 lines)
│   │       ├── Message model
│   │       ├── ConversationMemory
│   │       ├── MemoryManager
│   │       └── Global memory manager
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── templates.py             # Prompt definitions (100 lines)
│   │   │   ├── System prompt
│   │   │   ├── RAG prompt template
│   │   │   ├── Query rewrite prompt
│   │   │   └── PromptBuilder
│   │   │
│   │   └── builder.py               # Prompt construction (STUB)
│   │
│   ├── citation/
│   │   ├── __init__.py
│   │   └── citation_manager.py      # Extract sources (90 lines)
│   │       ├── Citation model
│   │       ├── CitationManager
│   │       └── Citation extraction/formatting
│   │
│   └── api/
│       ├── __init__.py
│       ├── routes.py                # All endpoints (70 lines)
│       │   ├── POST /api/chat
│       │   ├── GET /health
│       │   ├── GET /status
│       │   └── GET /
│       │
│       └── models.py                # Pydantic schemas (100 lines)
│           ├── ChatRequest
│           ├── ChatResponse
│           ├── Citation
│           ├── HealthResponse
│           ├── StatusResponse
│           ├── ErrorResponse
│           └── IngestionResponse
│
├── 📁 scripts/ (Utility Scripts)
│   ├── __init__.py
│   ├── init_db.py                   # Initialize Qdrant (40 lines)
│   ├── ingest.py                    # Run ingestion pipeline (30 lines)
│   └── eval.py                      # Evaluation utilities (30 lines)
│
├── 📁 tests/ (Test Suite)
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures (30 lines)
│   ├── test_api.py                  # API tests (30 lines)
│   ├── test_retrieval.py            # Retrieval tests (35 lines)
│   └── test_embedding.py            # Embedding tests (30 lines)
│
├── 📁 docs/ (Documentation - ~6,000 lines)
│   ├── ARCHITECTURE.md              # System design (800 lines)
│   │   ├── Project overview
│   │   ├── Data flow diagrams
│   │   ├── Module responsibilities
│   │   ├── Architectural decisions
│   │   ├── Learning path
│   │   └── Success criteria
│   │
│   ├── DATA_FLOW.md                 # Data pipeline (1,200 lines)
│   │   ├── Ingestion phase (extract → process → chunk → embed → index)
│   │   ├── Runtime phase (query → retrieve → rerank → generate → stream)
│   │   ├── Performance metrics
│   │   ├── Configuration points
│   │   └── Optimization tips
│   │
│   ├── API_REFERENCE.md             # Endpoint documentation (600 lines)
│   │   ├── Base URL & authentication
│   │   ├── Endpoint specifications
│   │   ├── Request/response formats
│   │   ├── Error handling
│   │   ├── Example usage (Python & JavaScript)
│   │   └── Data models
│   │
│   └── SETUP.md                     # Installation guide (500 lines)
│       ├── Prerequisites
│       ├── Step-by-step setup
│       ├── Docker configuration
│       ├── Troubleshooting
│       ├── Development workflow
│       ├── Testing
│       └── Production deployment
│
└── 📄 README.md                     # Quick start (300 lines)
    ├── What does it do?
    ├── Quick start
    ├── Architecture overview
    ├── API endpoints
    ├── Tech stack
    ├── FAQ
    └── Getting started

```

## Summary Statistics

| Category | Count | Approx. Lines |
|----------|-------|---|
| **Core Modules** | 11 | ~1,500 |
| **Base Classes & Types** | 6 | 350 |
| **Configuration** | 2 | 150 |
| **API Layer** | 2 | 200 |
| **Utilities** | 3 | 200 |
| **Ingestion Pipeline** | 1 | 50 |
| **Documentation Files** | 4 | 6,000 |
| **Test Files** | 4 | 150 |
| **Config Files** | 7 | 200 |
| **Total** | **43** | **~8,500** |

## Module Descriptions

### Core Architecture (11 modules)

1. **config/settings.py** - Environment configuration with Pydantic
2. **config/constants.py** - App constants and defaults
3. **utils/logger.py** - Structured logging setup
4. **utils/db.py** - Database connection pool
5. **utils/exceptions.py** - Custom exception hierarchy
6. **ingestion/pipeline.py** - Batch data loading orchestrator
7. **embeddings/embedding_service.py** - Vector generation (BGE-M3)
8. **retrieval/hybrid_retriever.py** - Hybrid search orchestrator
9. **reranking/reranker.py** - Result ranking (BGE-Reranker)
10. **llm/\*.py** - LLM provider implementations
11. **memory/memory_manager.py** - Conversation management

### Abstract Interfaces (6 base classes)

- **llm/base.py** - `BaseLLMProvider`
- **embeddings/base.py** - `BaseEmbeddingModel`
- **retrieval/base.py** - `BaseRetriever`, `RetrievalResult`
- **reranking/base.py** - `BaseReranker`, `RerankerResult`

### API Layer (2 modules)

- **api/routes.py** - REST endpoints
- **api/models.py** - Pydantic request/response schemas

### Configuration (7 files)

- **.env.example** - Environment variables template
- **requirements.txt** - Python dependencies
- **docker-compose.yml** - Docker services
- **Dockerfile** - Container image
- **.gitignore** - Git ignore rules
- **.dockerignore** - Docker build ignore

### Documentation (4 files)

- **ARCHITECTURE.md** - Design decisions and module layout
- **DATA_FLOW.md** - Complete data pipeline walkthrough
- **API_REFERENCE.md** - All endpoints and schemas
- **SETUP.md** - Installation and configuration

## Design Highlights

✅ **Clean separation:** Ingestion (batch) vs runtime (online)
✅ **Modular components:** Each retriever, reranker, LLM can be swapped
✅ **Extensible architecture:** Abstract base classes for new implementations
✅ **Type safety:** Pydantic models for all API contracts
✅ **Async/await:** Non-blocking I/O operations
✅ **Testable:** Clear dependency injection patterns
✅ **Documented:** 6,000+ lines of comprehensive documentation
✅ **Course-appropriate:** ~1,500 lines of implementation (not 100+ like enterprise)

## Next Steps for Students

1. **Week 1:** Read ARCHITECTURE.md + DATA_FLOW.md
2. **Week 2:** Implement ingestion pipeline (extractor → processor → chunker)
3. **Week 3:** Implement retrieval (dense + sparse + hybrid)
4. **Week 4:** Implement reranking
5. **Week 5:** Implement LLM providers
6. **Week 6:** Add API endpoints and streaming
7. **Week 7:** Add memory and multi-turn conversation
8. **Week 8:** Write tests and benchmarks
9. **Week 9:** Performance optimization
10. **Week 10:** Evaluation and documentation

---

**Total code to implement: ~1,500 lines**
**Estimated semester effort: 10-12 weeks**
**Complexity level: Course-appropriate** (not overly enterprise)
