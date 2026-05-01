# Data Flow Documentation

## Overview

This document traces the complete data flow through the RAG system, from raw database records through to streaming responses.

## 1. Ingestion Phase (Batch - Run Once)

### 1.1 Extract

```
PostgreSQL Table: menu_items
├─ id: 1
├─ name: "Pad Thai"
├─ description: "Stir-fried rice noodles with shrimp, vegetables"
├─ price: 12.99
├─ category: "noodles"
└─ dietary_tags: ["gluten-free", "contains-shellfish"]
    ↓
extractor.extract_items()
    ↓
Document Structure:
{
    "id": "menu_item_1",
    "content": "Pad Thai. Stir-fried rice noodles with shrimp, vegetables. Price: $12.99",
    "metadata": {
        "item_id": 1,
        "name": "Pad Thai",
        "price": 12.99,
        "category": "noodles",
        "dietary_tags": ["gluten-free"]
    }
}
```

### 1.2 Process

```
Raw Document
    ↓
processor.process_items()
├─ Lowercase text
├─ Remove extra whitespace
├─ Normalize unicode
└─ Validate data quality
    ↓
Cleaned Document:
{
    "content": "pad thai. stir-fried rice noodles with shrimp, vegetables. price: $12.99",
    "metadata": {...}
}
```

### 1.3 Chunk

```
Long descriptions split into chunks
├─ Chunk 1: "pad thai. stir-fried rice noodles..." (token count < 500)
├─ Chunk 2: "...with vegetables. price: $12.99" (if description is long)
└─ Metadata preserved in each chunk:
    {
        "chunk_id": "menu_item_1_chunk_0",
        "source_id": "menu_item_1",
        "chunk_index": 0,
        "item_name": "Pad Thai"
    }
```

### 1.4 Embedding

```
Text Chunks
    ↓
embedding_service.embed(chunks)
    ↓
BGE-M3 Model (1024-dim vectors)
    ↓
Dense Vectors (HNSW index):
[0.234, -0.123, 0.456, ..., 0.789]  (1024 dimensions)
    ↓
Sparse Vectors (BM25 tokens):
{"stir": 0.8, "fried": 0.7, "pad": 0.9, ...}
```

### 1.5 Index

```
Dense vectors + Sparse vectors + Metadata
    ↓
indexer.index_to_qdrant()
    ↓
Qdrant Collection: "food_items"
├─ Vector ID: hash(item_id + chunk_id)
├─ Dense Vector: [0.234, -0.123, ...]
├─ Sparse Vector: {"stir": 0.8, ...}
├─ Payload (metadata):
│   ├─ text: "pad thai. stir-fried..."
│   ├─ source: "menu_item_1"
│   ├─ name: "Pad Thai"
│   ├─ price: 12.99
│   └─ category: "noodles"
└─ Timestamp: 2024-01-15T10:30:00Z
```

## 2. Runtime Phase (Per-Query - Online)

### 2.1 User Query

```
ChatRequest:
{
    "query": "I want vegetarian dishes under $15",
    "session_id": "user-123",
    "stream": true
}
```

### 2.2 Memory & History

```
memory_manager.get_history(session_id)
    ↓
Conversation History:
[
    {"role": "user", "content": "Vegetarian options?"},
    {"role": "assistant", "content": "We have several vegetarian items..."},
    {"role": "user", "content": "I want vegetarian dishes under $15"}
]
```

### 2.3 Embedding Query

```
Query: "I want vegetarian dishes under $15"
    ↓
embedding_service.embed([query])
    ↓
Query Dense Vector: [0.145, -0.234, 0.567, ...]
Query Sparse Vector: {"vegetarian": 0.9, "dishes": 0.8, "15": 0.6}
```

### 2.4 Dense Retrieval

```
Query Dense Vector
    ↓
qdrant_client.search(
    collection="food_items",
    query_vector=query_dense,
    limit=20,
    search_params=HNSWSearchParams(...)
)
    ↓
Top 20 Dense Results:
[
    {
        "id": "item_5_chunk_0",
        "score": 0.87,  (cosine similarity)
        "payload": {...menu item data...}
    },
    {
        "id": "item_12_chunk_0",
        "score": 0.84,
        "payload": {...}
    },
    ...
]
```

### 2.5 Sparse Retrieval (BM25)

```
Query Terms: ["vegetarian", "dishes", "15"]
    ↓
sparse_retriever.retrieve(query, top_k=20)
    ↓
BM25 Ranking:
[
    {
        "id": "item_3_chunk_0",
        "score": 0.92,  (BM25 score)
        "text": "vegetarian pasta..."
    },
    {
        "id": "item_8_chunk_0",
        "score": 0.88,
        "text": "vegetarian stir fry..."
    },
    ...
]
```

### 2.6 Hybrid Fusion

```
Dense Results (top 20) + Sparse Results (top 20)
    ↓
fusion.reciprocal_rank_fusion(
    dense_results,
    sparse_results,
    dense_weight=0.6,
    sparse_weight=0.4
)
    ↓
Fused & Combined Scores:
[
    {
        "id": "item_5_chunk_0",
        "fused_score": 0.78,  (weighted combination)
        "dense_score": 0.87,
        "sparse_score": 0.68
    },
    {
        "id": "item_3_chunk_0",
        "fused_score": 0.76,
        "dense_score": 0.79,
        "sparse_score": 0.92
    },
    ...  (top 10 items)
]
```

### 2.7 Reranking

```
Query + Top 10 Hybrid Results
    ↓
reranker.rerank(
    query="I want vegetarian dishes under $15",
    documents=[...],
    top_k=5
)
    ↓
BGE-Reranker (cross-encoder model)
    ↓
Final Top-5 Reranked:
[
    {
        "id": "item_5_chunk_0",
        "rerank_score": 0.94,
        "text": "Vegetable pad thai. Stir-fried rice noodles...",
        "metadata": {
            "name": "Vegetable Pad Thai",
            "price": 13.99,
            "category": "noodles"
        }
    },
    {
        "id": "item_3_chunk_0",
        "rerank_score": 0.91,
        "text": "Vegetarian pasta primavera...",
        "metadata": {
            "name": "Pasta Primavera",
            "price": 14.50
        }
    },
    ...  (3 more items)
]
```

### 2.8 Prompt Building

```
prompts.build_rag_prompt(
    context=[top-5 items],
    query="I want vegetarian dishes under $15",
    history=[conversation history]
)
    ↓
System Prompt:
"You are a helpful food recommendation assistant..."

Final Prompt:
```
Based on the following menu items, provide recommendations:

Menu Items:
1. Vegetable Pad Thai - $13.99
   Stir-fried rice noodles with mixed vegetables...

2. Pasta Primavera - $14.50
   Seasonal vegetables with pasta...

[4 more items...]

Conversation History:
User: "Vegetarian options?"
Assistant: "We have several vegetarian items..."
User: "I want vegetarian dishes under $15"

Please provide helpful recommendations.
```
    ↓
```

### 2.9 LLM Generation (Streaming)

```
{system_prompt, full_prompt}
    ↓
llm_provider.stream(query, context, system_prompt)
    ↓
LLM Response (token stream):
```
Based on your preference for vegetarian dishes 
under $15, I'd recommend:

1. **Vegetable Pad Thai** ($13.99)
   A delicious stir-fried rice noodle dish...

2. **Pasta Primavera** ($14.50)
   Fresh seasonal vegetables...
```
    ↓
```

### 2.10 Streaming Response

```
Token: "Based"
    ↓
SSE Event: {"token": "Based"}
    ↓
[Send to client via SSE]

Token: " on"
    ↓
SSE Event: {"token": " on"}
    ↓
[Stream continues...]

Token: "[EOS]"  (end of sequence)
    ↓
Complete Signal:
{
    "status": "complete",
    "citations": [
        {
            "text": "Vegetable Pad Thai",
            "source": "menu_item_5"
        },
        ...
    ]
}
```

### 2.11 Citation Extraction

```
LLM Response + Retrieved Docs
    ↓
citation_manager.extract_citations(response, docs)
    ↓
Citations:
[
    {
        "text": "Vegetable Pad Thai",
        "source": "menu_item_5",
        "price": 13.99,
        "category": "noodles"
    },
    {
        "text": "Pasta Primavera",
        "source": "menu_item_3",
        "price": 14.50,
        "category": "pasta"
    }
]
```

### 2.12 Memory Save

```
memory_manager.add_message(
    session_id="user-123",
    role="user",
    content="I want vegetarian dishes under $15"
)

memory_manager.add_message(
    session_id="user-123",
    role="assistant",
    content="Based on your preference....[full response]"
)
    ↓
Session History Updated:
[
    ...previous messages...,
    {role: "user", content: "I want vegetarian dishes under $15"},
    {role: "assistant", content: "Based on your preference..."}
]
```

## 3. Performance Notes

| Stage | Typical Latency |
|-------|---|
| Embedding | 50-100ms |
| Dense Retrieval | 20-50ms |
| Sparse Retrieval | 30-100ms |
| Fusion | 5-10ms |
| Reranking | 50-150ms |
| **Total Retrieval** | **150-300ms** |
| LLM Generation | 500-2000ms (depends on model) |
| Streaming | Real-time |

## 4. Configuration Points

### What Can Be Tuned?

1. **Retrieval Parameters** (`app/config/settings.py`):
   - `dense_top_k`: How many dense results to get (default: 20)
   - `sparse_top_k`: How many BM25 results (default: 20)
   - `hybrid_top_k`: Results after fusion (default: 10)
   - `rerank_top_k`: Final results (default: 5)
   - `dense_weight`, `sparse_weight`: Fusion weights

2. **Chunking** (`app/config/constants.py`):
   - `CHUNK_SIZE`: Document chunk size (default: 500)
   - `CHUNK_OVERLAP`: Overlap between chunks (default: 100)

3. **LLM** (`app/config/settings.py`):
   - `provider`: Choose provider (Gemini, Groq)
   - `temperature`: Response creativity (0.0-1.0)
   - `max_tokens`: Max response length

4. **Model Selection** (`app/config/constants.py`):
   - `EMBEDDING_MODEL`: Embedding model name
   - `RERANKER_MODEL`: Reranker model name

---

**Tips for optimization:**
- Increase `rerank_top_k` if missing relevant items
- Decrease `dense_top_k` if retrieval is slow
- Adjust `dense_weight` vs `sparse_weight` based on query types
- Use GPU for embedding/reranking if available
