# API Reference

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication. In production, add JWT or API keys via middleware.

---

## Endpoints

### 1. POST /api/chat - Main Chat Endpoint

Main endpoint for getting RAG-powered recommendations.

#### Request

```json
{
  "query": "I want vegetarian dishes under $15",
  "session_id": "user-123",
  "stream": true
}
```

**Parameters:**
- `query` (string, required): User's question or preference
- `session_id` (string, optional): Session ID for conversation history. Defaults to UUID.
- `stream` (boolean, optional): If true, stream response. If false, return complete response. Default: true

#### Response (Non-streaming)

```json
{
  "response": "Based on your preference...",
  "citations": [
    {
      "text": "Vegetable Pad Thai",
      "source": "menu_item_5",
      "page": null
    }
  ],
  "model": "gemini-pro"
}
```

#### Response (Streaming - Server-Sent Events)

```
event: token
data: {"token": "Based"}

event: token
data: {"token": " on"}

event: token
data: {"token": " your"}

event: complete
data: {"citations": [...]}
```

**Streaming Details:**
- Each token is sent as a separate SSE event
- Last event is `complete` with final citations
- Client can stop listening anytime
- Reduce latency by rendering tokens as they arrive

#### Example cURL

**Non-streaming:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Vegetarian options under $15",
    "stream": false
  }'
```

**Streaming:**
```bash
curl -N -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Vegetarian options under $15",
    "stream": true
  }'
```

#### Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Invalid request (missing query, etc.) |
| 500 | Server error (check logs) |

---

### 2. GET /health - Health Check

Check if service is running.

#### Response

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### 3. GET /status - Service Status

Detailed status of service components.

#### Response

```json
{
  "running": true,
  "database_connected": true,
  "vector_store_connected": true,
  "llm_available": true,
  "message": "All systems operational"
}
```

---

### 4. GET / - Root

Root endpoint with API information.

#### Response

```json
{
  "message": "RAG Food Recommendation Service",
  "version": "0.1.0",
  "docs": "/docs"
}
```

---

## Data Models

### ChatRequest

```python
{
  "query": str,           # Required. User query
  "session_id": str,      # Optional. Session ID for history
  "stream": bool          # Optional. Default: true
}
```

### ChatResponse

```python
{
  "response": str,        # Generated response
  "citations": [          # Sources used
    {
      "text": str,        # Cited text/item name
      "source": str,      # Source identifier
      "page": int or null # Optional page number
    }
  ],
  "model": str            # LLM model used
}
```

### Citation

```python
{
  "text": str,            # Cited content
  "source": str,          # Source reference
  "metadata": dict        # Additional info
}
```

---

## Error Handling

All errors return JSON:

```json
{
  "error": "Invalid Request",
  "code": "VALIDATION_ERROR",
  "message": "Query cannot be empty"
}
```

### Common Errors

| Error | Code | Solution |
|-------|------|----------|
| Query empty | VALIDATION_ERROR | Provide non-empty query |
| Database down | DATABASE_ERROR | Check PostgreSQL/Qdrant |
| LLM unavailable | LLM_ERROR | Check API keys & connectivity |
| Rate limited | RATE_LIMIT_ERROR | Wait and retry |

---

## Rate Limiting

Not currently implemented. Add middleware for production.

---

## Conversation Management

### Session IDs

- If you don't provide `session_id`, a new session is created
- Use same `session_id` for related queries to maintain history
- Each session keeps last 20 messages
- Sessions stored in memory (not persisted across restarts)

### Example Multi-turn Conversation

```python
# Turn 1
POST /api/chat
{
  "query": "What vegetarian options do you have?",
  "session_id": "user-123"
}

# Turn 2 - Same session to get history
POST /api/chat
{
  "query": "Any of those under $10?",
  "session_id": "user-123"
}

# System will include previous conversation in context
```

---

## Example Usage (Python)

```python
import httpx
import json

# Non-streaming
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/chat",
        json={
            "query": "Vegetarian dishes under $15",
            "stream": False
        }
    )
    data = response.json()
    print(data["response"])

# Streaming
async with httpx.AsyncClient() as client:
    async with client.stream(
        "POST",
        "http://localhost:8000/api/chat",
        json={
            "query": "Vegetarian dishes under $15",
            "stream": True
        }
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                event = json.loads(line[6:])
                print(event.get("token", ""), end="", flush=True)
```

---

## Example Usage (JavaScript)

```javascript
// Non-streaming
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'Vegetarian dishes under $15',
    stream: false
  })
});

const data = await response.json();
console.log(data.response);

// Streaming
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'Vegetarian dishes under $15',
    stream: true
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const text = decoder.decode(value);
  const lines = text.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const event = JSON.parse(line.slice(6));
      process.stdout.write(event.token || '');
    }
  }
}
```

---

## API Documentation (Auto-generated)

Access interactive Swagger docs at: `http://localhost:8000/docs`

Or ReDoc at: `http://localhost:8000/redoc`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2024-01 | Initial course project release |

---

## Support

For issues, see [ARCHITECTURE.md](ARCHITECTURE.md) or contact course instructor.
