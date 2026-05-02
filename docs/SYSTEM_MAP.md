# Bản đồ Hệ thống (System Map)

Tài liệu này trình bày các chức năng chính của hệ thống RAG Chatbot Spicy Noodle và các file/thư mục tương ứng đảm nhận chức năng đó.

## 1. Luồng dữ liệu chính (Core Data Flow)

| Chức năng | Thư mục/File đảm nhận | Mô tả |
| :--- | :--- | :--- |
| **Điểm truy cập chính** | `app/main.py` | Khởi tạo FastAPI app, cấu hình CORS và mount các router/static files. |
| **API Chat** | `app/api/chat.py` | Xử lý các yêu cầu chat từ người dùng, quản lý lịch sử trò chuyện và gọi RAG chain. |
| **RAG Chain Logic** | `app/retrieval/langchain_rag_chain.py` | Trái tim của hệ thống: thực hiện viết lại câu hỏi (query rewriting), truy vấn (retrieval) và tạo câu trả lời (generation). |
| **LLM Provider** | `app/llm/langchain_provider.py` | Cấu hình và khởi tạo các mô hình ngôn ngữ (Gemini, Groq) với cơ chế fallback. |

## 2. Ingestion & Vector Store (Nạp dữ liệu & Lưu trữ vector)

| Chức năng | Thư mục/File đảm nhận | Mô tả |
| :--- | :--- | :--- |
| **Trích xuất dữ liệu** | `app/ingestion/extractor.py` | Đọc dữ liệu từ cơ sở dữ liệu PostgreSQL. |
| **Xử lý & Chỉnh sửa** | `app/ingestion/processor.py` | Làm sạch và chuẩn hóa nội dung văn bản. |
| **Phân đoạn văn bản** | `app/ingestion/chunker.py` | Chia nhỏ văn bản thành các đoạn (chunks) phù hợp cho việc nhúng (embedding). |
| **Đánh chỉ mục** | `app/ingestion/indexer.py` | Lưu trữ các vector và metadata vào Qdrant vector database. |
| **Pipeline điều phối** | `app/ingestion/pipeline.py` | Kết nối các bước trên thành một quy trình nạp dữ liệu hoàn chỉnh. |

## 3. Thành phần bổ trợ (Supporting Components)

| Chức năng | Thư mục/File đảm nhận | Mô tả |
| :--- | :--- | :--- |
| **Cấu hình** | `app/config/settings.py` | Quản lý biến môi trường và cấu hình hệ thống (API keys, model names, ports). |
| **Ghi nhật ký** | `app/utils/logger.py` | Cấu hình logging cho toàn bộ ứng dụng. |
| **Giao diện người dùng** | `app/static/` | Chứa các file HTML/CSS cho giao diện chat web. |
| **Lịch sử trò chuyện** | `app/memory/langchain_memory.py` | Các lớp hỗ trợ quản lý bộ nhớ hội thoại (LangChain format). |

## 4. Script điều hành

- `scripts/run_app.py`: Khởi chạy ứng dụng nhanh chóng.
- `scripts/ingest.py`: Chạy quy trình nạp dữ liệu từ PostgreSQL vào Qdrant.
- `scripts/test_rag.py`: Kiểm tra nhanh khả năng trả lời của hệ thống RAG.
