import httpx
from typing import List, AsyncGenerator, Any, Dict, Optional
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
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
        
        # We use BGE M3 or standard sentence transformers
        # BAAI/bge-m3 is heavy, might take time to download.
        self.embeddings = HuggingFaceBgeEmbeddings(
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
            from langchain.retrievers import EnsembleRetriever
            sparse_retriever = BM25Retriever.from_documents(bm25_docs)
            sparse_retriever.k = settings.retrieval.sparse_top_k
            
            # Combine them using EnsembleRetriever for RRF
            self.base_retriever = EnsembleRetriever(
                retrievers=[dense_retriever, sparse_retriever],
                weights=[settings.retrieval.dense_weight, settings.retrieval.sparse_weight]
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
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        self.rewrite_chain = contextualize_q_prompt | self.llm | StrOutputParser()
        
        # 2. QA Chain
        system_prompt = (
            "You are an expert assistant for a spicy noodle restaurant. "
            "Use the following pieces of retrieved context to answer the question. "
            "Carefully check all items and their prices. If the user asks for the 'most expensive', 'cheapest', "
            "or comparison, verify all values before answering. "
            "If you don't know the answer, just say that you don't know. "
            "Use formatting like bullet points when listing items. "
            "Context: {context}"
        )
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
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
                "input": lambda x: x["input"],
                "chat_history": lambda x: x["chat_history"]
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
        if chat_history:
            standalone_query = await self.rewrite_chain.ainvoke({
                "input": query,
                "chat_history": chat_history
            })
        else:
            standalone_query = query
            
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
            
        if chat_history:
            standalone_query = await self.rewrite_chain.ainvoke({
                "input": query,
                "chat_history": chat_history
            })
        else:
            standalone_query = query
            
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

