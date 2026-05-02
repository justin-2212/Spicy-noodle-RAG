# Spicy Noodle RAG Workflow Architecture

Tài liệu này mô tả chi tiết luồng hoạt động (workflow) của hệ thống Retrieval-Augmented Generation (RAG) hiện tại trong dự án Spicy Noodle Chatbot, cùng với ánh xạ chức năng đến các file mã nguồn tương ứng.

## 1. Giai đoạn Ingestion & Indexing (Chuẩn bị dữ liệu)

Giai đoạn này đảm nhiệm việc lấy dữ liệu từ cơ sở dữ liệu quan hệ, biến đổi, nhúng (embed) và lưu trữ vào Vector Database.

- **Luồng hoạt động chính:**
  1. **Trích xuất dữ liệu (Extraction):** Dữ liệu được truy vấn từ PostgreSQL (bao gồm products, categories, toppings, reviews).
  2. **Biến đổi & Chia nhỏ (Transform & Chunking):** Dữ liệu được định dạng thành văn bản và chia nhỏ bằng `RecursiveCharacterTextSplitter` (chunk_size: 500, chunk_overlap: 50).
  3. **Tạo Vector (Embedding):** Sử dụng mô hình `BAAI/bge-m3` để tạo dense vectors (kích thước 1024) cho từng chunk văn bản.
  4. **Lưu trữ (Indexing):** Các chunk và vectors được đẩy lên Qdrant Vector Store thông qua REST API để dễ dàng truy vấn.

- **Các file đảm nhiệm:**
  - `app/ingestion/pipeline.py`: Xây dựng ETL pipeline, đọc dữ liệu từ DB (PostgreSQL).
  - `app/ingestion/indexer.py`: Đảm nhận phần Text Splitting, gọi model BGE-M3 qua LangChain (`HuggingFaceBgeEmbeddings`), tạo payload và nạp dữ liệu vào Qdrant bằng httpx.

## 2. Giai đoạn Retrieval & Generation (Truy xuất & Sinh văn bản)

Giai đoạn cốt lõi khi người dùng gửi câu hỏi (query) lên hệ thống, xử lý qua Langchain Runnable Parallel Chain (LCEL).

- **Luồng hoạt động chính:**
  1. **Query Rewriting (Viết lại câu hỏi):**
     Hệ thống nhận câu hỏi mới kèm Chat History. Nếu có lịch sử, câu hỏi được viết lại thành một câu hỏi độc lập (Standalone Query) thông qua một LLM Chain để giữ nguyên ngữ cảnh mà không phụ thuộc vào lịch sử chat.
  2. **Hybrid Search với Reciprocal Rank Fusion (RRF):**
     Sử dụng `EnsembleRetriever` kết hợp 2 phương pháp tìm kiếm:
     - **Dense Retriever (`QdrantRestRetriever`):** Truy vấn các chunk có ý nghĩa tương đồng bằng cosine similarity trên Qdrant thông qua REST API (Lấy ra `DENSE_TOP_K = 20`).
     - **Sparse Retriever (`BM25Retriever`):** Truy vấn từ khóa chính xác thông qua thuật toán BM25. Documents được load từ Qdrant ngay lúc khởi tạo chain (Lấy ra `SPARSE_TOP_K = 20`).
     - **RRF Fusion:** Trộn 2 danh sách kết quả lại và đánh trọng số (`DENSE_WEIGHT=0.6`, `SPARSE_WEIGHT=0.4`) thông qua thuật toán RRF. Sau đó chỉ giới hạn lại số lượng kết quả bằng `HYBRID_TOP_K = 10`.
  3. **Reranking (Xếp hạng lại):**
     Danh sách 10 documents sau khi Hybrid Search sẽ được đưa qua mô hình `BAAI/bge-reranker-v2-m3` (CrossEncoder) để đánh giá chéo (cross-score) với câu hỏi của người dùng. Trả về top `RERANK_TOP_K = 3` documents chính xác nhất.
  4. **Generation (Sinh câu trả lời):**
     Dữ liệu văn bản từ 3 documents tốt nhất được gộp lại (format_docs) làm `context` và đẩy vào `QA Prompt`. LLM (Groq / Gemini) nhận context và đưa ra câu trả lời cuối cùng ở dạng JSON, Markdown, hoặc Text.

- **Các file đảm nhiệm:**
  - `app/retrieval/langchain_rag_chain.py`: File trung tâm chứa lớp `LangChainRAGChain` tích hợp:
    - `QdrantRestRetriever` (Custom Dense Retriever)
    - `BM25Retriever` (Sparse Retriever)
    - `EnsembleRetriever` (RRF Hybrid Search)
    - Reranking function bằng `sentence_transformers.CrossEncoder`.
    - LCEL Chains (`rewrite_chain` và `rag_chain`).

## 3. Cấu hình & Quản lý môi trường (Settings)

Hệ thống được thiết kế để dễ dàng điều chỉnh cấu hình tìm kiếm và LLM tùy theo quy mô dự án. Với cơ sở dữ liệu nhỏ (vài chục - vài trăm items), các thông số đã được tối ưu:

- **Các file đảm nhiệm:**
  - `app/config/settings.py`: Khai báo các mô hình Pydantic (`RetrievalSettings`, `LLMSettings`, ...) tải các biến từ `.env`.
  - `.env`: Nơi lưu trữ cấu hình môi trường với các thiết lập:
    - `RETRIEVAL_DENSE_TOP_K=20`
    - `RETRIEVAL_SPARSE_TOP_K=20`
    - `RETRIEVAL_HYBRID_TOP_K=10`
    - `RETRIEVAL_RERANK_TOP_K=3`
    - Cơ chế LLM Fallback (Groq -> Gemini).

## 4. Giao diện API & Tương tác

Cung cấp các endpoint REST cho frontend giao tiếp, duy trì bộ nhớ (memory) và stream câu trả lời theo thời gian thực (Server-Sent Events).

- **Các file đảm nhiệm:**
  - `app/api/chat.py` (hoặc `endpoints.py`): Tiếp nhận request, khởi tạo RAG Chain, truyền lịch sử chat (từ memory) và trả về response qua `StreamingResponse`.
  - `app/llm/llm_factory.py`: Quản lý việc khởi tạo LLM (Groq / Gemini) dựa trên cấu hình, xử lý luồng Fallback khi gặp lỗi API limit.

## Tổng kết sơ đồ ngắn gọn (LCEL Chain Flow)

`User Query` -> `Rewrite Chain (with History)` -> `Standalone Query` -> `Hybrid Search (Qdrant + BM25)` -> `RRF Fusion (Top 10)` -> `BGE-Reranker (Top 3)` -> `QA Chain (Prompt + Context)` -> `LLM Response`.
