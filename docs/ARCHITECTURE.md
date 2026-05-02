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
├── 📁 app/ (Main Application)
│   │
│   ├── main.py                   # FastAPI app entry point
│   │   • Create FastAPI app instance
│   │   • Mount routers
│   │   • Configure CORS, middleware
│   │
│   ├── config/
│   │   ├── settings.py           # Pydantic BaseSettings
│   │   │   • Load environment variables
│   │   │   • Database URL, API keys, ports
│   │   │
│   │   └── constants.py          # App constants
│   │
│   ├── utils/
│   │   ├── logger.py             # Logging setup
│   │   └── db.py                 # Database utilities (PostgreSQL)
│   │
│   ├── ingestion/ (BATCH PIPELINE)
│   │   ├── extractor.py          # Extract from PostgreSQL
│   │   ├── processor.py          # Document processing
│   │   ├── chunker.py            # Split into chunks
│   │   ├── indexer.py            # Index to Qdrant
│   │   └── pipeline.py           # Orchestrate ingestion
│   │
│   ├── retrieval/ (RUNTIME)
│   │   └── langchain_rag_chain.py # Core RAG Logic (LangChain)
│   │
│   ├── llm/
│   │   └── langchain_provider.py  # LLM Factory (Gemini/Groq)
│   │
│   ├── memory/
│   │   └── langchain_memory.py    # Conversation memory
│   │
│   └── api/
│       ├── chat.py               # Chat API endpoint
│       └── models.py             # Request/Response schemas
│
├── 📁 scripts/ (Standalone utilities)
│   ├── ingest.py                 # Run ingestion manually
│   ├── eval.py                   # Evaluation utilities
│   └── init_db.py                # Initialize Qdrant
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

### Ingestion Flow (Batch)

```
PostgreSQL (food items)
      ↓
[extractor.py] - Query items
      ↓
[processor.py] - Clean text
      ↓
[chunker.py] - Split into chunks
      ↓
[indexer.py] - Upload to Qdrant (using LangChain BGE Embeddings)
      ↓
Qdrant (vector index ready)
```

### Runtime Flow (Per-Query)

```
User Query
      ↓
[api/chat.py] POST /chat endpoint receives request
      ↓
[retrieval/langchain_rag_chain.py] - Core Orchestration:
    ├─ [rewrite_chain] - Formulate standalone question
    ├─ [QdrantRestRetriever] - Search Qdrant
    └─ [qa_chain] - Generate answer with context
      ↓
[llm/langchain_provider.py] - Call LLM (Gemini/Groq)
      ↓
JSON response to frontend
```

---

## 🏗️ Key Architectural Decisions

### 1. **Separated Ingestion & Runtime**
- **Ingestion** runs once to populate the vector store.
- **Runtime** handles live user queries.

### 2. **LangChain Centric Design**
The system uses LangChain for:
- RAG chain orchestration (`LangChainRAGChain`)
- Vector store interactions
- LLM provider management with fallback support

### 3. **Modular Providers**
LLM and Memory logic are encapsulated in specific providers, making it easy to swap implementations or add new features without affecting the core API.

---

## 📊 Module Responsibilities

| Module | Responsibility | Key Files |
|--------|---|---|
| **config** | Environment & settings | settings.py |
| **utils** | Logging, DB | logger.py, db.py |
| **ingestion** | Data pipeline (batch) | extractor, processor, chunker, indexer, pipeline |
| **retrieval** | Core RAG logic | langchain_rag_chain.py |
| **llm** | Language model calls | langchain_provider.py |
| **memory** | Chat history | langchain_memory.py |
| **api** | REST endpoints | chat.py, models.py |

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
