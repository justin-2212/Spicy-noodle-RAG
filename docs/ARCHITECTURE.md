# RAG Food Recommendation Service - Course Project Architecture

## 📋 Quick Overview

This is a **modular, course-project-appropriate RAG service** for a university AI course. It's simplified from enterprise patterns but maintains clean architecture principles suitable for academic work and portfolio demonstration.

**Purpose:** Build an intelligent food recommendation chatbot that queries restaurant data from PostgreSQL and generates personalized suggestions using LLMs.

---

## 📁 Folder Structure

```
rag-chatbot-spicy-noodle/
│
├── 📄 Root Configuration
│   ├── README.md                 # Quick start & setup
│   ├── .env.example              # Environment template
│   ├── requirements.txt          # Dependencies
│   ├── Dockerfile                # Container image
│   ├── docker-compose.yml        # Local development setup
│   └── .gitignore                # Git ignore rules
│
├── 📁 app/ (Main Application - 950 lines total)
│   │
│   ├── main.py                   # FastAPI app entry point (70 lines)
│   │   • Create FastAPI app instance
│   │   • Mount routers
│   │   • Configure CORS, middleware
│   │   • Health check endpoint
│   │
│   ├── config/
│   │   ├── settings.py           # Pydantic BaseSettings (100 lines)
│   │   │   • Load environment variables
│   │   │   • Database URL, API keys, ports
│   │   │   • Model paths and hyperparameters
│   │   │
│   │   └── constants.py          # App constants (50 lines)
│   │       • Collection names (Qdrant)
│   │       • Default hyperparameters
│   │       • Model identifiers
│   │
│   ├── utils/
│   │   ├── logger.py             # Logging setup (40 lines)
│   │   │   • Structured logging configuration
│   │   │
│   │   ├── db.py                 # Database utilities (80 lines)
│   │   │   • PostgreSQL connection pool
│   │   │   • Query helpers
│   │   │
│   │   └── exceptions.py         # Custom exceptions (50 lines)
│   │       • RAGException base class
│   │       • RetrievalError, EmbeddingError, etc.
│   │
│   ├── ingestion/ (BATCH PIPELINE - Runs once/scheduled)
│   │   ├── extractor.py          # Extract from PostgreSQL (80 lines)
│   │   │   • Query food items from backend DB
│   │   │   • Format documents (name, description, price, etc.)
│   │   │   • Handle chunking metadata
│   │   │
│   │   ├── processor.py          # Document processing (80 lines)
│   │   │   • Clean text (lowercase, whitespace)
│   │   │   • Normalize descriptions
│   │   │   • Validate data quality
│   │   │
│   │   ├── chunker.py            # Split into chunks (60 lines)
│   │   │   • Chunk long descriptions
│   │   │   • Preserve metadata (item_id, category)
│   │   │   • Overlapping chunks for better coverage
│   │   │
│   │   ├── indexer.py            # Index to Qdrant (100 lines)
│   │   │   • Create collections if needed
│   │   │   • Upload vectors + metadata
│   │   │   • Handle updates/deletes
│   │   │
│   │   └── pipeline.py           # Orchestrate ingestion (80 lines)
│   │       • Main ingestion flow
│   │       • Error handling & logging
│   │       • Progress tracking
│   │
│   ├── embeddings/ (VECTORIZATION)
│   │   └── embedding_service.py  # BGE-M3 wrapper (100 lines)
│   │       • Load/cache BGE-M3 model
│   │       • Generate vectors for text
│   │       • Batch processing support
│   │       • GPU/CPU device handling
│   │
│   ├── retrieval/ (RUNTIME - Query processing)
│   │   ├── dense_retriever.py    # HNSW search (80 lines)
│   │   │   • Query vector embedding
│   │   │   • Search Qdrant collection
│   │   │   • Return top-k results
│   │   │
│   │   ├── sparse_retriever.py   # BM25 search (100 lines)
│   │   │   • Keyword/BM25 matching
│   │   │   • Query term weighting
│   │   │   • Return ranked results
│   │   │
│   │   ├── hybrid_retriever.py   # Hybrid orchestrator (100 lines)
│   │   │   • Call both retrievers
│   │   │   • Fuse rankings (RRF)
│   │   │   • Combine scores
│   │   │   • Return top-k fused results
│   │   │
│   │   └── fusion.py             # Ranking fusion (50 lines)
│   │       • Reciprocal Rank Fusion (RRF)
│   │       • Weighted score combination
│   │
│   ├── reranking/
│   │   └── reranker.py           # BGE-Reranker wrapper (80 lines)
│   │       • Load reranker model
│   │       • Re-score documents
│   │       • Return top-k reranked
│   │
│   ├── llm/
│   │   ├── base.py               # Abstract LLM interface (40 lines)
│   │   │   • BaseProvider class
│   │   │   • generate() method
│   │   │   • stream() method
│   │   │
│   │   ├── gemini_provider.py    # Google Gemini (80 lines)
│   │   │   • API client setup
│   │   │   • Request formatting
│   │   │   • Response handling & streaming
│   │   │
│   │   ├── groq_provider.py      # Groq API (80 lines)
│   │   │   • API client setup
│   │   │   • Request formatting
│   │   │   • Response handling & streaming
│   │   │
│   │   └── streaming.py          # SSE helpers (60 lines)
│   │       • Format streaming responses
│   │       • Token event generation
│   │
│   ├── memory/
│   │   └── memory_manager.py     # Conversation memory (100 lines)
│   │       • Store/retrieve chat history
│   │       • Session management
│   │       • In-memory storage (file backup optional)
│   │
│   ├── prompts/
│   │   ├── templates.py          # Prompt definitions (80 lines)
│   │   │   • System prompt
│   │   │   • RAG prompt with context
│   │   │   • Query rewriting prompt
│   │   │
│   │   └── builder.py            # Build prompts (60 lines)
│   │       • Insert retrieved docs
│   │       • Format conversation history
│   │       • Build final prompt
│   │
│   ├── citation/
│   │   └── citation_manager.py   # Extract sources (70 lines)
│   │       • Extract source references from response
│   │       • Map to original documents
│   │       • Format citations
│   │
│   └── api/
│       ├── routes.py             # All API endpoints (120 lines)
│       │   • POST /chat - Main chat endpoint
│       │   • GET /health - Health check
│       │   • POST /ingest - Trigger ingestion
│       │   • GET /status - Service status
│       │
│       └── models.py             # Request/Response schemas (80 lines)
│           • ChatRequest, ChatResponse
│           • IngestionRequest, StatusResponse
│           • Pydantic validation
│
├── 📁 scripts/ (Standalone utilities)
│   ├── ingest.py                 # Run ingestion manually (40 lines)
│   ├── eval.py                   # Evaluation utilities (50 lines)
│   └── init_db.py                # Initialize Qdrant (30 lines)
│
├── 📁 tests/
│   ├── test_retrieval.py         # Retrieval tests
│   ├── test_embedding.py         # Embedding tests
│   ├── test_api.py               # API endpoint tests
│   └── conftest.py               # Pytest fixtures
│
└── 📁 docs/
    ├── ARCHITECTURE.md           # This file (design decisions)
    ├── API_REFERENCE.md          # API documentation
    ├── DATA_FLOW.md              # Data processing pipeline
    └── SETUP.md                  # Installation & local development
```

---

## 🔄 Data Flow

### Ingestion Flow (Batch - Once on startup)

```
PostgreSQL (food items)
      ↓
[extractor.py] - Query items, format docs
      ↓
[processor.py] - Clean, normalize text
      ↓
[chunker.py] - Split into chunks (preserve item metadata)
      ↓
[embedding_service.py] - Generate embeddings (BGE-M3)
      ↓
[indexer.py] - Upload to Qdrant with metadata
      ↓
Qdrant (vector index ready)
```

### Runtime Flow (Per-Query)

```
User Query (e.g., "Vegetarian dishes under $15")
      ↓
[routes.py] POST /chat endpoint receives request
      ↓
[memory_manager.py] - Retrieve conversation history
      ↓
[prompts/builder.py] - Build query prompt with history
      ↓
[embedding_service.py] - Embed query
      ↓
[retrieval/] - Hybrid retrieval:
    ├─ [dense_retriever.py] - HNSW search → top-20
    ├─ [sparse_retriever.py] - BM25 search → top-20
    └─ [hybrid_retriever.py] - Fuse results → top-10
      ↓
[reranking/reranker.py] - Re-rank with BGE-Reranker → top-5
      ↓
[prompts/builder.py] - Build final prompt with context
      ↓
[llm/] - Call LLM (Gemini/Groq) with streaming
      ↓
[streaming.py] - SSE stream tokens to client
      ↓
[citation_manager.py] - Extract references
      ↓
[memory_manager.py] - Save conversation
      ↓
Streamed response to frontend
```

---

## 🏗️ Key Architectural Decisions

### 1. **Separated Ingestion & Runtime**
- **Ingestion** runs once at startup or on-demand (batch processing)
- **Runtime** handles queries (online, latency-optimized)
- Different concerns = separate modules

**Why:** Ingestion can be slow and thorough. Runtime needs to be fast. Different optimization strategies.

### 2. **Minimal Module Count**
Unlike enterprise patterns, this keeps modules focused and discoverable:
- 11 core modules (not 40+)
- ~1500-2000 total lines of code
- Perfect for understanding in 1-2 semesters

### 3. **Clear Retrieval Pipeline**
Three separate retrievers that can be studied/optimized independently:
- **Dense:** Fast vector search (understand HNSW)
- **Sparse:** BM25 ranking (understand text search)
- **Hybrid:** Learn ranking fusion strategies

### 4. **Provider Abstraction**
LLM providers follow a simple interface:
```python
# app/llm/base.py
class BaseLLMProvider:
    async def generate(query, context) -> str
    async def stream(query, context) -> AsyncGenerator
```

Easy to:
- Add Anthropic, Ollama, etc.
- Switch providers at runtime
- Test with mocks

### 5. **Embedding & Reranking as Services**
Rather than scattering model calls, they're isolated:
- `embedding_service.py` - All BGE-M3 logic
- `reranking/reranker.py` - All reranker logic

Easy to:
- Swap models (try different embeddings)
- Optimize (batching, caching, GPU)
- Monitor (measure latency)

### 6. **Prompts as Data**
Prompts stored in `prompts/templates.py`, not hardcoded:
- Easy to experiment with prompt engineering
- Version control prompts
- Separate business logic from prompts

---

## 📊 Module Responsibilities

| Module | Responsibility | Key Files | ~Lines |
|--------|---|---|---|
| **config** | Environment & settings | settings.py, constants.py | 150 |
| **utils** | Logging, DB, exceptions | logger.py, db.py, exceptions.py | 170 |
| **ingestion** | Data pipeline (batch) | extractor, processor, chunker, indexer, pipeline | 400 |
| **embeddings** | Vector generation | embedding_service.py | 100 |
| **retrieval** | Query search | dense, sparse, hybrid, fusion | 330 |
| **reranking** | Result ranking | reranker.py | 80 |
| **llm** | Language model calls | base.py, gemini, groq, streaming | 300 |
| **memory** | Chat history | memory_manager.py | 100 |
| **prompts** | Prompt templates | templates.py, builder.py | 140 |
| **citation** | Source attribution | citation_manager.py | 70 |
| **api** | REST endpoints | routes.py, models.py | 200 |
| | **TOTAL** | | **~1900** |

---

## 🚀 Scalability Notes

### Suitable For:
- ✅ Course projects (1-2 semesters)
- ✅ Hackathons and MVPs
- ✅ Small-to-medium deployments (1K-100K queries/day)
- ✅ Portfolio demonstration

### Bottlenecks to Optimize Later:
1. **Embedding latency** - Batch processing, GPU allocation
2. **Qdrant latency** - Index tuning, distributed mode
3. **LLM latency** - Context reduction, caching
4. **Memory overhead** - Redis for distributed cache

### Future Improvements:
```
If scaling to production:
├── Add async task queue (Celery) for ingestion
├── Implement Redis caching layer
├── Distribute embedding/reranking to separate services
├── Add vector index optimization
├── Implement request rate limiting
└── Add monitoring (Prometheus/Grafana)
```

---

## 📚 Module Boundaries (What Goes Where)

| Question | Answer |
|---|---|
| **Where does PostgreSQL connection go?** | `app/utils/db.py` - singleton pool |
| **Where do I configure model names?** | `app/config/constants.py` - easy to change |
| **Where do I add a new LLM?** | Create `app/llm/new_provider.py` - inherit `BaseLLMProvider` |
| **Where are prompts?** | `app/prompts/templates.py` - easy to edit |
| **Where do I tune retrieval?** | `app/retrieval/` - three independent modules |
| **Where is error handling?** | `app/utils/exceptions.py` - hierarchical |
| **Where do I add tests?** | `tests/` - mirror app structure |
| **Where are API schemas?** | `app/api/models.py` - all Pydantic models |

---

## 🎓 Learning Path (Recommended Study Order)

1. **Week 1-2:** Understand folder structure & data flow
   - Read this file
   - Read `DATA_FLOW.md`
   
2. **Week 3-4:** Ingestion pipeline
   - Study `app/ingestion/` modules in order
   - Trace a food item from PostgreSQL → Qdrant
   
3. **Week 5-6:** Retrieval & embedding
   - Understand `app/embeddings/embedding_service.py`
   - Compare dense vs sparse retrieval
   - Study fusion strategies
   
4. **Week 7-8:** LLM integration & prompts
   - Add new LLM provider
   - Experiment with prompts
   - Implement streaming
   
5. **Week 9-10:** API & testing
   - Write endpoint tests
   - Test different retrieval configurations
   - Measure performance
   
6. **Week 11-12:** Optimization & deployment
   - Profile bottlenecks
   - Optimize top-k parameters
   - Deploy with Docker
   - Write evaluation report

---

## 🔧 Getting Started (30 minutes)

```bash
# 1. Clone and setup
git clone <repo>
cd rag-chatbot-spicy-noodle
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Start services
docker-compose up -d

# 4. Initialize
python scripts/init_db.py
python scripts/ingest.py

# 5. Run
python -m uvicorn app.main:app --reload

# 6. Test
curl http://localhost:8000/health
```

---

## 📝 Code Style Guidelines

This project follows:
- **Type hints** - All function signatures typed
- **Docstrings** - Module, class, function documentation
- **Error handling** - Custom exceptions, logging
- **Async/await** - All I/O operations async
- **Configuration** - No hardcoded values
- **Tests** - Unit + integration coverage

Example module style:
```python
"""Description of module."""

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class ItemProcessor:
    """Process food items for indexing."""
    
    async def process(self, items: List[dict]) -> List[dict]:
        """
        Clean and normalize food items.
        
        Args:
            items: Raw items from database
            
        Returns:
            Processed items
        """
        processed = []
        for item in items:
            try:
                cleaned = self._clean_text(item['description'])
                processed.append({**item, 'description': cleaned})
            except Exception as e:
                logger.error(f"Error processing {item['id']}: {e}")
                
        return processed
```

---

## ✅ Checklist for Course Project Completion

- [ ] All modules have docstrings
- [ ] No hardcoded values (use config)
- [ ] All async functions tested
- [ ] API endpoints tested
- [ ] Retrieval compared (dense vs sparse vs hybrid)
- [ ] Reranking impact measured
- [ ] Prompts documented
- [ ] Memory persists across restarts
- [ ] SSE streaming works
- [ ] Docker build succeeds
- [ ] README covers setup steps
- [ ] Data flow diagram in docs

---

## 🎯 Success Criteria

Your project is successful when:

1. ✅ Food items from PostgreSQL are indexed to Qdrant
2. ✅ Queries return relevant recommendations
3. ✅ Hybrid retrieval improves over single method
4. ✅ Reranking improves result quality
5. ✅ Different LLM prompts are tested
6. ✅ Streaming responses work
7. ✅ Conversation history is maintained
8. ✅ Performance is measured (latency, accuracy)
9. ✅ Code is documented & tested
10. ✅ Project can be deployed with Docker

---

## 📚 Next Steps

1. Read [SETUP.md](SETUP.md) - Installation guide
2. Read [DATA_FLOW.md](DATA_FLOW.md) - Detailed data pipeline
3. Read [API_REFERENCE.md](API_REFERENCE.md) - Endpoint documentation
4. Start with `app/config/settings.py` - Understand configuration
5. Trace ingestion pipeline end-to-end
6. Run first API call to /chat

---

**Good luck with your project! 🚀**
