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
                # pyrefly: ignore [missing-import]
                from langchain.retrievers import EnsembleRetriever
            except ImportError:
                from langchain_classic.retrievers import EnsembleRetriever
            sparse_retriever = BM25Retriever.from_documents(bm25_docs)
            sparse_retriever.k = settings.retrieval.sparse_top_k
            
            # Combine them using EnsembleRetriever for RRF
            self.base_retriever = EnsembleRetriever(
                retrievers=[dense_retriever, sparse_retriever],
                weights=[settings.retrieval.dense_weight, settings.retrieval.sparse_weight]
            )
            logger.info(f"Initialized Hybrid Search with weights Dense={settings.retrieval.dense_weight}, Sparse={settings.retrieval.sparse_weight}")
        else:
            self.base_retriever = dense_retriever
            logger.warning("BM25 docs not found, falling back to dense retriever only.")
        
        # Initialize Reranker
        logger.info(f"Loading reranker model: {settings.reranker.model_name}")
        self.reranker = CrossEncoder(
            settings.reranker.model_name,
            device=settings.reranker.device
        )
        
        # 1. Query Rewriting Chain
        contextualize_q_system_prompt = (
            "Bạn là trợ lý tối ưu hóa câu lệnh tìm kiếm cho hệ thống RAG. "
            "NHIỆM VỤ: Chuyển đổi câu hỏi của người dùng thành 1 câu TRUY VẤN TÌM KIẾM duy nhất. "
            "QUY TẮC CỰC KỲ QUAN TRỌNG: "
            "1. CHỈ sử dụng thông tin từ câu hỏi hiện tại và lịch sử trò chuyện. "
            "2. TUYỆT ĐỐI KHÔNG được thêm bất kỳ tên món ăn, thành phần hoặc thông tin nào KHÔNG có trong đầu vào. "
            "3. Nếu người dùng hỏi 'có những loại nào', 'tất cả', 'bao nhiêu loại', hãy GIỮ LẠI các từ khóa này để tìm kiếm tài liệu tổng hợp. "
            "4. KHÔNG TRẢ LỜI CÂU HỎI. "
            "5. Kết quả chỉ chứa duy nhất câu truy vấn. "
            "Ví dụ đúng: 'quán có những loại gà nào' -> 'tất cả các loại gà rán'."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        self.rewrite_chain = contextualize_q_prompt | self.llm | StrOutputParser()
        
        # 2. QA Chain
        system_prompt = (
            "Bạn là trợ lý ảo chuyên nghiệp và cẩn thận của quán mì cay. "
            "NHIỆM VỤ: Trả lời câu hỏi khách hàng dựa TRỰC TIẾP và DUY NHẤT vào Context được cung cấp. "
            
            "QUY TẮC PHẢI TUÂN THỦ (ĐỂ TRÁNH LỖI ẢO GIÁC): "
            "1. Trước khi trả lời về số lượng món ăn (ví dụ: 'có mấy loại', 'tất cả'), hãy THỰC HIỆN CÁC BƯỚC: "
            "   a. Quét toàn bộ Context để tìm tất cả các món thuộc nhóm yêu cầu. "
            "   b. ĐẾM chính xác số lượng món tìm thấy. "
            "   c. ĐỐI CHIẾU tên từng món để đảm bảo không bỏ sót (đặc biệt là các món Gà Rán, Mì Cay). "
            "2. Luôn trình bày danh sách dưới dạng ĐÁNH SỐ THỨ TỰ (1, 2, 3...) để đảm bảo tính minh bạch. "
            "3. Nếu thông tin trong Context khác với những gì bạn đã trả lời trước đó, hãy ƯU TIÊN Context mới nhất và đính chính lại một cách lịch sự. "
            "4. TUYỆT ĐỐI KHÔNG được trả lời 'chỉ có 1 loại' nếu trong Context xuất hiện từ 2 món trở lên thuộc cùng nhóm đó. "
            "5. Luôn cung cấp giá tiền đi kèm với tên món ăn.\n\n"
            "Context:\n{context}"
        )
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        def format_docs(docs):
            if not docs:
                return "Không tìm thấy thông tin phù hợp trong cơ sở dữ liệu."
            
            logger.info(f"Passing {len(docs)} documents to LLM for generation.")
            formatted = []
            for i, doc in enumerate(docs):
                product_name = doc.metadata.get("product_name", "Món ăn")
                formatted.append(f"--- [Sản phẩm: {product_name}] ---\n{doc.page_content}")
            return "\n\n".join(formatted)
            
        def rerank_docs(inputs):
            query = inputs["query"].lower()
            docs = inputs["docs"]
            if not docs:
                return []
            
            # Prepare pairs for reranking
            pairs = [[query, doc.page_content] for doc in docs]
            scores = self.reranker.predict(pairs)
            
            # Global query keywords
            is_global_query = any(kw in query for kw in ["tất cả", "mấy loại", "danh sách", "menu", "tổng cộng", "bao gồm"])
            
            # Add scores to metadata and sort
            for doc, score in zip(docs, scores):
                final_score = float(score)
                # Boost summary documents for global queries
                if is_global_query and doc.metadata.get("is_summary"):
                    final_score += 2.0 # Significant boost for summary docs
                
                doc.metadata["rerank_score"] = final_score
            
            sorted_docs = sorted(docs, key=lambda x: x.metadata["rerank_score"], reverse=True)
            
            # Log top scores for debugging
            if sorted_docs:
                logger.info(f"Rerank Score (Top 1): {sorted_docs[0].metadata['rerank_score']:.4f} for {sorted_docs[0].metadata.get('product_name')} (Global: {is_global_query})")
                 
            return sorted_docs[:settings.retrieval.rerank_top_k]

        def limit_hybrid_docs(docs):
            if not docs:
                return []
            logger.info(f"Hybrid retrieval returned {len(docs)} docs.")
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
                "input": lambda x: x["input"],
                "chat_history": lambda x: x.get("chat_history", [])
            })
            | qa_prompt
            | self.llm
            | StrOutputParser()
        )

    async def generate(self, query: str, chat_history: List[Any] = None) -> str:
        """Generate a response synchronously."""
        if chat_history is None:
            chat_history = []
            
        # Standardize query
        standalone_query = await self.rewrite_chain.ainvoke({
            "input": query,
            "chat_history": chat_history
        })
        # Basic cleanup in case LLM adds quotes or "Search query:" prefix
        standalone_query = standalone_query.strip().replace('"', '').replace("'", "")
        if ":" in standalone_query and len(standalone_query.split(":")[0]) < 20:
             standalone_query = standalone_query.split(":")[-1].strip()
             
        logger.info(f"Standalone search query: '{standalone_query}' (Original: '{query}')")
            
        # Run RAG chain
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

