import httpx
from typing import List, AsyncGenerator, Any, Dict, Optional
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from sentence_transformers import CrossEncoder
from app.config.settings import settings
from app.utils.logger import logger

class QdrantRestRetriever(BaseRetriever):
    """Custom Qdrant retriever using REST API to avoid protobuf issues."""
    
    url: str
    collection_name: str
    embeddings: Any
    k: int = 5
    
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        # Sync version (required by BaseRetriever interface if not implementing _aget)
        query_vector = self.embeddings.embed_query(query)
        
        with httpx.Client() as client:
            response = client.post(
                f"{self.url}/collections/{self.collection_name}/points/search",
                json={
                    "vector": query_vector,
                    "limit": self.k,
                    "with_payload": True
                },
                timeout=30.0
            )
            response.raise_for_status()
            results = response.json()["result"]
            
        docs = []
        for res in results:
            payload = res.get("payload", {})
            # Map payload to page_content and metadata
            # We assume 'text' field exists in payload as per builder
            content = payload.get("text", str(payload))
            docs.append(Document(page_content=content, metadata=payload))
            
        return docs

class LangChainRAGChain:
    """RAG chain using LangChain and custom Qdrant REST retriever."""
    
    def __init__(self, llm):
        self.llm = llm
        
        # Initialize embeddings
        model_kwargs = {'device': settings.embedding.device}
        encode_kwargs = {'normalize_embeddings': True}
        
        # Using HuggingFaceEmbeddings from langchain_huggingface (replacement for HuggingFaceBgeEmbeddings)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding.model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        
        # Initialize Dense Retriever
        dense_retriever = QdrantRestRetriever(
            url=f"http://{settings.vector_store.host}:{settings.vector_store.port}",
            collection_name=settings.vector_store.collection_name,
            embeddings=self.embeddings,
            k=settings.retrieval.dense_top_k
        )
        
        # Initialize Sparse Retriever and Ensemble
        bm25_docs = self._fetch_all_documents_for_bm25()
        if bm25_docs:
            from langchain_community.retrievers import BM25Retriever
            # In this environment, EnsembleRetriever is in langchain_classic.retrievers
            try:
                from langchain.retrievers import EnsembleRetriever
            except ImportError:
                from langchain_classic.retrievers import EnsembleRetriever
            sparse_retriever = BM25Retriever.from_documents(bm25_docs)
            sparse_retriever.k = settings.retrieval.sparse_top_k
            
            # Combine them using EnsembleRetriever for RRF
            self.base_retriever = EnsembleRetriever(
                retrievers=[dense_retriever, sparse_retriever],
                weights=[0.3, 0.7]
            )
            logger.info("Initialized Hybrid Search with EnsembleRetriever (RRF)")
        else:
            self.base_retriever = dense_retriever
            logger.warning("BM25 docs not found, falling back to dense retriever only.")
        
        # Initialize Reranker
        logger.info(f"Loading reranker model: {settings.reranker.model_name}")
        self.reranker = CrossEncoder(
            settings.reranker.model_name,
            device=settings.reranker.device
        )
        
        # Setup Reranker (Manual LLM Reranking logic or Compressor)
        # Since LLMChainExtractor might be in langchain.chains, we'll do a simple prompt-based rerank if needed
        # For now, we'll just use the base retriever or a simple LCEL filter
        
        # 1. Query Rewriting Chain
        contextualize_q_system_prompt = (
            "Bạn là trợ lý giúp chuẩn hóa câu hỏi khách hàng cho hệ thống tìm kiếm (RAG). "
            "Dựa vào câu hỏi hiện tại và lịch sử trò chuyện (nếu có), hãy tạo ra một câu hỏi độc lập, đầy đủ ngữ cảnh để tìm kiếm dữ liệu. "
            "Nếu khách hàng dùng tên món ăn tắt hoặc chung chung (ví dụ: 'mì cay', 'lẩu bò', 'tokbokki'), "
            "hãy giữ nguyên hoặc mở rộng chúng một cách mô tả nhất để công cụ tìm kiếm dễ dàng nhận diện. "
            "KHÔNG TRẢ LỜI CÂU HỎI, chỉ trả về câu hỏi đã được chuẩn hóa."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        self.rewrite_chain = contextualize_q_prompt | self.llm | StrOutputParser()
        
        # 2. QA Chain
        system_prompt = (
            "Bạn là trợ lý AI chuyên nghiệp của một quán mì cay. "
            "CHỈ SỬ DỤNG các thông tin được cung cấp trong phần Context dưới đây để trả lời câu hỏi của khách hàng. "
            "TUYỆT ĐỐI KHÔNG bịa đặt, suy đoán, hoặc sử dụng kiến thức bên ngoài. "
            "Đặc biệt: KHÔNG ĐƯỢC lấy đánh giá (review/rating) của một sản phẩm cụ thể để gán cho toàn bộ quán. "
            "Nếu khách hàng sử dụng tên gọi tắt hoặc không đầy đủ (ví dụ: 'lẩu bò' thay vì 'Lẩu Tomyum Bò'), hãy linh hoạt đối chiếu với thông tin trong Context để trả lời nếu rõ ràng đó là cùng một sản phẩm. "
            "Nếu thông tin khách hàng hỏi thực sự KHÔNG CÓ trong Context, hãy trả lời chính xác: 'Xin lỗi, hiện tại tôi chưa có thông tin về vấn đề này.' và không giải thích thêm. "
            "Hãy diễn đạt câu trả lời một cách tự nhiên, đa dạng và thân thiện. Tránh lặp lại các mẫu câu 'học thuộc lòng' cứng nhắc. "
            "Hãy kiểm tra thật kỹ các con số về giá cả, thành phần combo, và đánh giá trước khi xuất ra. "
            "Sử dụng định dạng danh sách (bullet points) khi cần liệt kê.\n\n"
            "Context: {context}"
        )
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
            
        def rerank_docs(inputs):
            query = inputs["query"]
            docs = inputs["docs"]
            if not docs:
                return []
            
            # Prepare pairs for reranking
            pairs = [[query, doc.page_content] for doc in docs]
            scores = self.reranker.predict(pairs)
            
            # Add scores to metadata and sort
            for doc, score in zip(docs, scores):
                doc.metadata["rerank_score"] = float(score)
            
            sorted_docs = sorted(docs, key=lambda x: x.metadata["rerank_score"], reverse=True)
            
            # Log top scores for debugging
            if sorted_docs:
                logger.info(f"Top rerank score: {sorted_docs[0].metadata['rerank_score']:.4f}")
                logger.info(f"Top retrieved doc names: {[doc.metadata.get('product_name') for doc in sorted_docs[:3]]}")
                 
            return sorted_docs[:settings.retrieval.rerank_top_k]

        def limit_hybrid_docs(docs):
            if not docs:
                return []
            # Log hybrid top scores for debugging
            logger.info(f"Retrieved {len(docs)} documents after hybrid fusion. Limiting to {settings.retrieval.hybrid_top_k}.")
            return docs[:settings.retrieval.hybrid_top_k]

        self.rag_chain = (
            RunnableParallel({
                "context": (
                    RunnableParallel({
                        "query": lambda x: x["input"],
                        "docs": (lambda x: x["input"]) | self.base_retriever | limit_hybrid_docs
                    })
                    | rerank_docs
                    | format_docs
                ),
                "input": lambda x: x["input"]
            })
            | qa_prompt
            | self.llm
            | StrOutputParser()
        )

    async def generate(self, query: str, chat_history: List[Any] = None) -> str:
        """Generate a response synchronously."""
        if chat_history is None:
            chat_history = []
            
        # First, rewrite query if there is history
        # Always rewrite query to standardize product names
        standalone_query = await self.rewrite_chain.ainvoke({
            "input": query,
            "chat_history": chat_history
        })
        logger.info(f"Rewritten query: {standalone_query}")
            
        # Then, run RAG chain
        result = await self.rag_chain.ainvoke({
            "input": standalone_query,
            "chat_history": chat_history
        })
        
        return result
        
    async def stream(self, query: str, chat_history: List[Any] = None) -> AsyncGenerator[str, None]:
        """Stream the generation response."""
        if chat_history is None:
            chat_history = []
            
        # Always rewrite query to standardize product names
        standalone_query = await self.rewrite_chain.ainvoke({
            "input": query,
            "chat_history": chat_history
        })
            
        async for chunk in self.rag_chain.astream({
            "input": standalone_query,
            "chat_history": chat_history
        }):
            yield chunk

    def _fetch_all_documents_for_bm25(self) -> List[Document]:
        """Fetch all documents from Qdrant to initialize BM25Retriever."""
        docs = []
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"http://{settings.vector_store.host}:{settings.vector_store.port}/collections/{settings.vector_store.collection_name}/points/scroll",
                    json={"limit": 1000, "with_payload": True, "with_vector": False},
                    timeout=30.0
                )
                if response.status_code == 200:
                    results = response.json().get("result", {}).get("points", [])
                    for res in results:
                        payload = res.get("payload", {})
                        # Qdrant Indexer uses 'text' field for chunked text
                        content = payload.get("text", "")
                        if content:
                            docs.append(Document(page_content=content, metadata=payload))
            logger.info(f"Fetched {len(docs)} documents for BM25 Retriever")
        except Exception as e:
            logger.error(f"Failed to fetch documents for BM25: {e}")
            
        return docs

