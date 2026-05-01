# README - RAG Food Recommendation Service

A course-project RAG (Retrieval-Augmented Generation) microservice for intelligent food recommendations.

## 🎯 What This Project Does

Builds an AI chatbot that:
1. **Retrieves** relevant food items from restaurant database
2. **Ranks** results by relevance
3. **Generates** personalized recommendations using LLM
4. **Streams** responses in real-time

Example: *"I'm vegetarian and want something under $15"* → Gets personalized menu suggestions.

## 🏗️ Architecture

```
PostgreSQL (menu data) 
    ↓ [Ingestion Pipeline]
Qdrant (vector index)
    ↓
User Query 
    ↓ [Hybrid Retrieval + Reranking]
Top-5 Relevant Items
    ↓ [LLM Generation]
Streaming Response
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed design.

## 🚀 Quick Start (5 minutes)

### 1. Setup
```bash
# Clone repository
git clone <repo-url>
cd rag-chatbot-spicy-noodle

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials:
# - PostgreSQL connection string
# - Qdrant host/port
# - LLM API keys (Gemini or Groq)
```

### 3. Run Services
```bash
# Start PostgreSQL and Qdrant
docker-compose up -d

# Initialize vector database
python scripts/init_db.py

# Load food data from PostgreSQL
python scripts/ingest.py
```

### 4. Start API Server
```bash
python -m uvicorn app.main:app --reload

# API is now at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 5. Test It
```bash
# Chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Vegetarian dishes under $15"}'

# Health check
curl http://localhost:8000/health
```

## 📁 Project Structure

```
app/
├── config/          # Configuration & constants
├── utils/           # Logging, DB, exceptions
├── ingestion/       # Data loading pipeline (batch)
├── embeddings/      # Vector generation (BGE-M3)
├── retrieval/       # Search engines (dense + sparse + hybrid)
├── reranking/       # Result ranking (BGE-Reranker)
├── llm/             # LLM providers (Gemini, Groq)
├── memory/          # Conversation history
├── prompts/         # Prompt templates
├── citation/        # Source attribution
└── api/             # FastAPI endpoints

scripts/             # Utility scripts
tests/               # Test suite
docs/                # Documentation
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed folder explanation.

## 📚 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design & folder structure
- **[DATA_FLOW.md](docs/DATA_FLOW.md)** - Data processing pipeline
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - API endpoint documentation
- **[SETUP.md](docs/SETUP.md)** - Detailed installation guide

## 🔌 API Endpoints

### POST /chat
Main chat endpoint with RAG response.

**Request:**
```json
{
  "query": "Vegetarian dishes",
  "session_id": "user-123",
  "stream": true
}
```

**Response (streaming):**
```
event: token
data: {"token": "Based"}

event: token
data: {"token": " on"}

event: complete
data: {"citations": [...]}
```

### GET /health
Health check endpoint.

### POST /ingest
Trigger data ingestion from PostgreSQL.

See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for full API documentation.

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Vector DB | Qdrant |
| Source DB | PostgreSQL |
| Embeddings | BAAI/bge-m3 |
| Reranker | bge-reranker-base |
| LLM Providers | Gemini API, Groq API |
| Retrieval | Hybrid (Dense + BM25) |
| Streaming | Server-Sent Events |

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_retrieval.py

# Run with coverage
pytest --cov=app
```

## 📊 Performance Metrics

Typical performance on course-scale dataset:
- **Query latency:** 200-500ms (including streaming)
- **Embedding generation:** ~50ms
- **Retrieval:** ~100ms (dense + sparse + fusion)
- **Reranking:** ~50ms
- **LLM generation:** ~500-2000ms (depends on LLM)

## 🐳 Docker

```bash
# Build image
docker build -t rag-service:latest .

# Run container
docker run -p 8000:8000 \
  -e LLM_API_KEY=your-key \
  -e DATABASE_URL=postgresql://... \
  rag-service:latest
```

## 🤝 Contributing

This is a course project. For improvements:
1. Create a feature branch
2. Make changes with tests
3. Submit pull request

## 📝 Notes

- This is a **course-project simplified version**, not production-scale
- Perfect for academic understanding and portfolio demonstration
- Easily extensible for future features (agents, multimodal, etc.)

## ❓ FAQ

**Q: How do I add a new LLM provider?**  
A: Create `app/llm/new_provider.py` inheriting from `BaseLLMProvider`. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

**Q: How do I change embedding model?**  
A: Edit `app/config/constants.py` and `app/embeddings/embedding_service.py`.

**Q: Can I use without Qdrant?**  
A: You'd need to implement alternative in `app/retrieval/`. Currently requires Qdrant.

**Q: How do I improve retrieval quality?**  
A: Tune in `app/retrieval/hybrid_retriever.py` - adjust `top_k`, weights, fusion strategy.

**Q: Does it support multi-turn conversations?**  
A: Yes, via `app/memory/memory_manager.py` - stores conversation history.

## 📄 License

[Add your license]

## 📧 Contact

For questions about the project architecture, see documentation or contact course instructor.

---

**Ready to start?** Follow [SETUP.md](docs/SETUP.md) for detailed installation.
