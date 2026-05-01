# Setup Guide - RAG Food Recommendation Service

Complete installation and setup instructions for local development.

## Prerequisites

- **Python:** 3.11+
- **Docker:** 21.0+
- **Docker Compose:** 2.0+
- **Git:** Latest version
- **API Keys:** Gemini or Groq API key for LLM

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd rag-chatbot-spicy-noodle
```

## Step 2: Create Virtual Environment

### Option A: venv (Recommended)

```bash
# Create
python -m venv .venv

# Activate
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

# Verify
which python  # Should show path to .venv/bin/python
```

### Option B: conda

```bash
conda create -n rag-service python=3.11
conda activate rag-service
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; import torch; print('✓ Dependencies installed')"
```

## Step 4: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your values
nano .env  # Or use your preferred editor
```

### Required Environment Variables

```env
# PostgreSQL (will be created in Docker)
DB_URL=postgresql://user:password@localhost:5432/food_db

# Qdrant (will be running in Docker)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# LLM Provider - Choose ONE
LLM_PROVIDER=gemini
LLM_GEMINI_API_KEY=your-api-key-here

# OR
LLM_PROVIDER=groq
LLM_GROQ_API_KEY=your-api-key-here
```

### Optional Tweaks

```env
# For faster local development (CPU)
EMBEDDING_DEVICE=cpu
RERANKER_DEVICE=cpu

# Or GPU if available
EMBEDDING_DEVICE=cuda
RERANKER_DEVICE=cuda

# Smaller batch sizes for limited memory
EMBEDDING_BATCH_SIZE=8
RERANKER_BATCH_SIZE=16
```

## Step 5: Start Docker Services

```bash
# Start PostgreSQL, Qdrant, Redis
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f qdrant
docker-compose logs -f postgres
```

Wait 10-15 seconds for services to be healthy.

## Step 6: Initialize Database

```bash
# Initialize Qdrant collections
python scripts/init_db.py

# Should output: "Qdrant initialized successfully"
```

## Step 7: Load Sample Data (Optional)

```bash
# Run ingestion pipeline
python scripts/ingest.py

# This will:
# 1. Query PostgreSQL for menu items
# 2. Process and chunk documents
# 3. Generate embeddings
# 4. Index to Qdrant

# Check Qdrant UI for indexed items
# http://localhost:6333/dashboard
```

## Step 8: Start API Server

```bash
# Development with auto-reload
python -m uvicorn app.main:app --reload --port 8000

# Production
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Server is now running at: `http://localhost:8000`

## Step 9: Test the API

### Health Check

```bash
curl http://localhost:8000/health
```

### Interactive Docs

Open in browser:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Test Chat

```bash
# Non-streaming
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What vegetarian options do you have?"}'

# Streaming
curl -N -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What vegetarian options do you have?"}'
```

## Step 10: Run Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_api.py

# With coverage
pytest --cov=app

# Verbose output
pytest -v
```

## Troubleshooting

### PostgreSQL Connection Error

```bash
# Check if container is running
docker ps | grep postgres

# Check logs
docker-compose logs postgres

# Restart
docker-compose restart postgres

# Verify connection
docker-compose exec postgres psql -U user -d food_db -c "SELECT 1"
```

### Qdrant Connection Error

```bash
# Check Qdrant
docker ps | grep qdrant

# Check logs
docker-compose logs qdrant

# Qdrant UI
open http://localhost:6333/dashboard

# Restart
docker-compose restart qdrant
```

### GPU Not Detected

```python
# Check if PyTorch sees GPU
python -c "import torch; print(torch.cuda.is_available())"

# If False, use CPU instead
# Set in .env: EMBEDDING_DEVICE=cpu
```

### Model Download Issues

```bash
# Models download automatically on first use
# They're cached in ./models/ directory

# If stuck, manually download:
python -c "from sentence_transformers import SentenceTransformer; \
           SentenceTransformer('BAAI/bge-m3')"

# Check disk space (models are ~700MB)
du -sh ./models/
```

### Memory Issues

```bash
# Reduce batch sizes in .env
EMBEDDING_BATCH_SIZE=4
RERANKER_BATCH_SIZE=8

# Or reduce model:
# Use smaller model variant
EMBEDDING_MODEL_NAME=BAAI/bge-small-en-v1.5
```

### API Timeout

```bash
# Increase timeout in .env or code
# For streaming, use patience flag in curl:
curl -N --connect-timeout 30 ...
```

## Development Workflow

### 1. Making Changes

```bash
# Uvicorn automatically reloads on file changes
# Just edit and save!
```

### 2. Testing Changes

```bash
# Run relevant tests
pytest tests/test_api.py -v

# Or specific test
pytest tests/test_api.py::test_health_check -v
```

### 3. Debugging

```python
# Add logging
from app.utils.logger import logger

logger.info("Debug message")
logger.error(f"Error: {error}")

# Check logs
docker-compose logs -f
```

### 4. Database Inspection

```bash
# PostgreSQL
docker-compose exec postgres psql -U user -d food_db
# Then: SELECT * FROM menu_items;

# Qdrant
# UI: http://localhost:6333/dashboard
# Or API: http://localhost:6333/api/
```

## Docker Development

### Build Custom Image

```bash
docker build -t rag-service:latest .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -e LLM_GEMINI_API_KEY=your-key \
  -e DATABASE_URL=postgresql://... \
  rag-service:latest
```

### Stop All Services

```bash
docker-compose down

# Also remove volumes (clean slate)
docker-compose down -v
```

## Production Deployment

### Using Docker Compose

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Using Kubernetes

```bash
# (Example - customize as needed)
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Environment Variables

```bash
# Production .env
export DEBUG=False
export LOG_LEVEL=WARNING
export DATABASE_URL=postgresql://prod-db:5432/food_prod
export QDRANT_HOST=qdrant-prod
export LLM_PROVIDER=gemini
export LLM_GEMINI_API_KEY=***
```

## Performance Tuning

### For Development

```env
LOG_LEVEL=DEBUG
DEBUG=True
DB_ECHO=True  # SQL logging
```

### For Production

```env
LOG_LEVEL=WARNING
DEBUG=False
DB_POOL_SIZE=20  # Increase pool
EMBEDDING_BATCH_SIZE=64  # Batch more
```

### Profiling

```bash
# Profile API latency
python -m cProfile -s cumtime app/main.py

# Memory profiling
pip install memory-profiler
python -m memory_profiler app/main.py
```

## Next Steps

1. **Read Documentation:**
   - [ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System design
   - [DATA_FLOW.md](../docs/DATA_FLOW.md) - Data pipeline
   - [API_REFERENCE.md](../docs/API_REFERENCE.md) - API docs

2. **Explore Code:**
   - Start with `app/config/settings.py` - understand configuration
   - Then `app/main.py` - FastAPI app structure
   - Then `app/api/routes.py` - endpoints

3. **Implement Features:**
   - Implement retrieval components (`app/retrieval/`)
   - Implement LLM providers (`app/llm/`)
   - Add ingestion from PostgreSQL (`app/ingestion/`)

4. **Write Tests:**
   - Add tests in `tests/` directory
   - Test retrieval quality
   - Test LLM integration

## FAQ

**Q: How do I change the LLM provider?**
A: Edit `.env` - set `LLM_PROVIDER` to `gemini` or `groq`, and provide corresponding API key.

**Q: Do I need to run Docker?**
A: Yes, PostgreSQL and Qdrant are easiest via Docker. You could install locally but not recommended.

**Q: Can I use a different embedding model?**
A: Edit `app/config/constants.py` - change `EMBEDDING_MODEL`. Note: different models may have different dimensions.

**Q: How do I seed the database with menu items?**
A: Create a migration or seed script to insert data into PostgreSQL, then run `python scripts/ingest.py`.

**Q: What if I get CUDA out of memory?**
A: Set `EMBEDDING_DEVICE=cpu` in `.env` or reduce batch sizes.

---

**Everything set up?** Start the server and visit `http://localhost:8000/docs`! 🚀
