# README - Spicy Noodle RAG Recommendation Service

A course-project RAG (Retrieval-Augmented Generation) microservice for an AI-powered spicy noodle restaurant chatbot.

---

# 🎯 Project Overview

This project builds an intelligent AI chatbot for a spicy noodle restaurant system.

The chatbot can:

1. Retrieve relevant menu items from the restaurant database
2. Understand customer preferences and dietary needs
3. Rank menu recommendations by relevance
4. Generate personalized food suggestions using LLMs
5. Stream responses in real-time

Example queries:

* “I want a non-spicy seafood noodle.”
* “Recommend a spicy noodle under $10.”
* “What is good for someone who cannot eat beef?”
* “Suggest a vegetarian side dish.”

---

# 🏗️ System Architecture

```text
PostgreSQL (restaurant menu database)
        ↓
Ingestion Pipeline
        ↓
Qdrant Vector Database
        ↓
User Query
        ↓
Hybrid Retrieval (Dense + BM25)
        ↓
Reranking
        ↓
LLM Generation
        ↓
Streaming Chat Response
```

The RAG service works as an independent AI microservice connected to:

* frontend repository
* backend repository
* PostgreSQL database

For detailed architecture:
See `docs/ARCHITECTURE.md`

---

# 🍜 Restaurant Context

This chatbot is designed for a spicy noodle restaurant system.

The menu database may include:

* spicy noodle dishes
* ramen
* side dishes
* beverages
* toppings
* combo meals

Each menu item can contain:

* name
* description
* price
* spice level
* ingredients
* dietary tags
* category
* calories
* availability

The chatbot uses RAG to provide context-aware recommendations based on this restaurant data.

---

# 🚀 Quick Start

## 1. Clone Repository

```bash
git clone <repo-url>
cd rag-chatbot-spicy-noodle
```

---

## 2. Create Virtual Environment

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment

```bash
cp .env.example .env
```

Configure:

* PostgreSQL connection
* Qdrant configuration
* Gemini API or Groq API key

---

## 5. Start Infrastructure Services

```bash
docker-compose up -d
```

This starts:

* PostgreSQL
* Qdrant
* Redis

---

## 6. Initialize Database

```bash
python scripts/init_db.py
```

---

## 7. Ingest Restaurant Data

```bash
python scripts/ingest.py
```

This step:

* loads menu data from PostgreSQL
* processes documents
* creates embeddings
* indexes vectors into Qdrant

---

## 8. Run API Server

```bash
python -m uvicorn app.main:app --reload
```

Server:

* API: http://localhost:8000
* Swagger Docs: http://localhost:8000/docs

---

# 🧪 Example API Usage

## Chat Request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Recommend a medium spicy beef noodle under $12",
    "session_id": "user-001",
    "stream": true
  }'
```

---

## Example Response

```text
Based on your preferences, you may like:

1. Spicy Beef Ramen
- Medium spicy level
- Tender sliced beef
- Price: $10.99

2. Kimchi Seafood Noodle
- Mild-medium spicy
- Includes shrimp and squid
- Price: $11.50
```

---

# 📁 Project Structure

```text
app/
├── config/          # Configuration & constants
├── utils/           # Logger, database, exceptions
├── ingestion/       # Data ingestion pipeline
├── embeddings/      # Embedding generation (BGE-M3)
├── retrieval/       # Dense, sparse, hybrid retrieval
├── reranking/       # Result reranking
├── llm/             # Gemini/Groq integration
├── memory/          # Conversation memory
├── prompts/         # Prompt templates
├── citation/        # Citation generation
└── api/             # FastAPI endpoints

scripts/             # Utility scripts
tests/               # Test suite
docs/                # Documentation
```

Detailed explanation:
See `docs/ARCHITECTURE.md`

---

# 🔌 Main API Endpoints

## POST /chat

Main RAG chatbot endpoint.

### Request

```json
{
  "query": "Recommend a spicy seafood noodle",
  "session_id": "user-001",
  "stream": true
}
```

### Features

* Hybrid retrieval
* Conversational memory
* Reranking
* Streaming response
* Citation support

---

## POST /ingest

Triggers ingestion pipeline from PostgreSQL into Qdrant.

---

## GET /health

Health check endpoint.

---

# 🛠️ Technology Stack

| Component       | Technology            |
| --------------- | --------------------- |
| Framework       | FastAPI               |
| Vector Database | Qdrant                |
| Source Database | PostgreSQL            |
| Embedding Model | BAAI/bge-m3           |
| Reranker        | bge-reranker-base     |
| Retrieval       | Hybrid Retrieval      |
| ANN Search      | HNSW                  |
| LLM Providers   | Gemini API / Groq API |
| Streaming       | SSE                   |

---

# 🧠 Core AI Features

## Hybrid Retrieval

Combines:

* dense semantic retrieval
* BM25 keyword retrieval

for better recommendation quality.

---

## ANN Search

Uses HNSW indexing inside Qdrant for fast semantic search.

---

## Reranking

Uses cross-encoder reranking to improve final retrieval relevance.

---

## Conversational Memory

Supports multi-turn conversations with chat history tracking.

---

## Streaming Response

Streams generated responses token-by-token using SSE.

---

# 🧪 Testing

Run all tests:

```bash
pytest
```

Run specific test:

```bash
pytest tests/test_retrieval.py
```

Run coverage:

```bash
pytest --cov=app
```

---

# 🐳 Docker

Build image:

```bash
docker build -t spicy-noodle-rag .
```

Run container:

```bash
docker run -p 8000:8000 spicy-noodle-rag
```

---

# 📊 Expected Workflow

```text
Restaurant Database
        ↓
Ingestion Pipeline
        ↓
Vector Indexing
        ↓
Customer Query
        ↓
Hybrid Retrieval
        ↓
Reranking
        ↓
Prompt Building
        ↓
LLM Generation
        ↓
Streaming Recommendation
```

---

# 🎓 Educational Purpose

This project is designed as a university AI engineering course project.

Goals:

* understand RAG architecture
* learn vector search
* build hybrid retrieval systems
* integrate LLM APIs
* design modular AI services
* practice microservice architecture

This is not intended to be a large-scale enterprise production system, but follows production-inspired engineering practices.

---

# 🚀 Future Extensions

Possible future improvements:

* multilingual support
* image-based food search
* multimodal RAG
* agentic workflows
* recommendation personalization
* analytics dashboard
* user preference learning

---

# ❓ FAQ

## Can I change the LLM provider?

Yes. Add a new provider inside:
`app/llm/`

---

## Can I replace Qdrant?

Yes, but retrieval modules must be updated.

---

## Does the chatbot support conversation history?

Yes, via:
`app/memory/memory_manager.py`

---

## Can I use another embedding model?

Yes. Update:

* `app/config/constants.py`
* embedding service implementation

---

# 📄 License

Add your preferred license.

---

# 📧 Contact

For academic questions or project discussion, contact the project team or course instructor.

---

Ready to start?
See `docs/SETUP.md` for full installation and development guide.
