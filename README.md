# 🍜 Spicy Noodle RAG Chatbot

Chatbot hỗ trợ khách hàng thông minh cho hệ thống quán Mì Cay, sử dụng kỹ thuật **RAG (Retrieval-Augmented Generation)** để cung cấp thông tin chính xác về menu, giá cả và đánh giá từ khách hàng.

## 🌟 Tính năng nổi bật

*   **🔍 Hybrid Search**: Kết hợp tìm kiếm vector (Dense) và tìm kiếm văn bản (Sparse/BM25) thông qua thuật toán RRF để tăng độ chính xác.
*   **🎯 BGE-Reranker**: Sử dụng mô hình Cross-Encoder để tái xếp hạng (re-rank) tài liệu, đảm bảo kết quả phù hợp nhất được đưa vào ngữ cảnh của LLM.
*   **✍️ Query Rewriting**: Tự động chuyển đổi câu hỏi hội thoại thành câu truy vấn tìm kiếm độc lập, giúp xử lý tốt các câu hỏi dựa trên lịch sử trò chuyện.
*   **⚡ Streaming Responses**: Hỗ trợ phản hồi theo dạng stream, mang lại trải nghiệm mượt mà giống ChatGPT.
*   **📊 Ingestion Pipeline**: Hệ thống tự động trích xuất dữ liệu từ Database (PostgreSQL), xử lý và đánh chỉ mục vào Vector Store (Qdrant).
*   **🧩 Smart Chunking**: Tự động phân đoạn văn bản thông minh, giữ nguyên cấu trúc cho các tài liệu tổng hợp (Summary Documents).

## 🛠️ Công nghệ sử dụng

*   **Backend**: FastAPI (Python)
*   **Framework RAG**: LangChain
*   **Vector Database**: Qdrant
*   **Database**: PostgreSQL
*   **Embeddings**: BAAI/bge-m3 (HuggingFace)
*   **Reranker**: BAAI/bge-reranker-base
*   **LLM**: Google Gemini / Groq

## 📁 Cấu trúc dự án

```text
rag-chatbot-spicy-noodle/
├── app/
│   ├── api/          # API Endpoints (Chat, Stream)
│   ├── ingestion/    # Logic xử lý dữ liệu (Loaders, Builders, Indexer)
│   ├── retrieval/    # Logic RAG (Retriever, Reranker, Chain)
│   ├── config/       # Cấu hình hệ thống (Settings, Constants)
│   ├── llm/          # Provider cho LLM (Gemini, Groq)
│   └── static/       # Giao diện người dùng đơn giản
├── scripts/          # Các script tiện ích (Run app, Ingest, Migration)
├── Dockerfile        # Docker image configuration
└── docker-compose.yml # Orchestration cho Postgres & Qdrant
```

## 🚀 Bắt đầu ngay

### 1. Cấu hình môi trường

Tạo file `.env` từ file mẫu:
```bash
cp .env.example .env
```
Điền các thông tin quan trọng như `LLM_GEMINI_API_KEY` hoặc `LLM_GROQ_API_KEY`.

### 2. Chạy dịch vụ hạ tầng (Docker)

Sử dụng Docker Compose để khởi chạy Postgres và Qdrant:
```bash
docker-compose up -d
```

### 3. Cài đặt và Chạy ứng dụng

**Sử dụng Virtual Environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # Trên Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Chạy ứng dụng:**
```bash
python scripts/run_app.py
```
Ứng dụng sẽ chạy tại: `http://localhost:8000`

### 4. Nạp dữ liệu vào Vector Database

Để nạp dữ liệu từ Database vào Qdrant, hãy chạy script ingestion:
```bash
python scripts/ingest.py
```

## 🔌 API Endpoints

### Chat API
*   **Endpoint**: `POST /api/chat`
*   **Payload**:
    ```json
    {
      "message": "Quán có những loại mì cay nào?",
      "history": [],
      "stream": true
    }
    ```

## 📝 Giấy phép
Dự án được phát triển cho mục đích học thuật và hỗ trợ hệ thống quán mì cay.
