"""Indexer for RAG documents into Qdrant."""

import httpx
import uuid
from typing import List, Dict, Any
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from app.config.settings import settings
from app.utils.logger import logger

class QdrantIndexer:
    """Index documents into Qdrant vector store using REST API."""
    
    def __init__(self):
        """Initialize indexer."""
        model_kwargs = {'device': settings.embedding.device}
        encode_kwargs = {'normalize_embeddings': True}
        
        self.embeddings = HuggingFaceBgeEmbeddings(
            model_name=settings.embedding.model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        self.base_url = f"http://{settings.vector_store.host}:{settings.vector_store.port}"
        
    async def index_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Convert dict documents to vectors and index to Qdrant via REST.
        """
        try:
            if not documents:
                logger.warning("No documents to index.")
                return True
                
            logger.info(f"Indexing {len(documents)} documents to Qdrant collection '{settings.vector_store.collection_name}' via REST...")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                # 1. Recreate collection
                logger.info(f"Recreating collection '{settings.vector_store.collection_name}'...")
                # Delete first
                await client.delete(f"{self.base_url}/collections/{settings.vector_store.collection_name}")
                
                # Create
                response = await client.put(
                    f"{self.base_url}/collections/{settings.vector_store.collection_name}",
                    json={
                        "vectors": {
                            "size": settings.vector_store.vector_size,
                            "distance": "Cosine"
                        }
                    }
                )
                response.raise_for_status()
                
                # 2. Chunk documents
                logger.info("Chunking documents...")
                from langchain_text_splitters import RecursiveCharacterTextSplitter
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=100,
                    separators=["\n\n", "\n", ". ", " ", ""]
                )
                
                chunked_docs = []
                for doc in documents:
                    metadata = doc.get("metadata", {})
                    # SKIP chunking for summary documents to keep full lists together
                    if metadata.get("is_summary"):
                        chunked_docs.append({
                            "id": doc.get("id"),
                            "text": doc["text"],
                            "metadata": {
                                **metadata,
                                "chunk_id": 0,
                                "original_id": doc.get("id")
                            }
                        })
                        continue

                    # Normal chunking for regular products
                    chunks = text_splitter.split_text(doc["text"])
                    for i, chunk in enumerate(chunks):
                        product_name = metadata.get("product_name", "")
                        chunk_text = f"Món: {product_name}\n{chunk}" if product_name else chunk
                        
                        chunked_docs.append({
                            "id": doc.get("id"),
                            "text": chunk_text,
                            "metadata": {
                                **metadata,
                                "chunk_id": i,
                                "original_id": doc.get("id")
                            }
                        })
                
                logger.info(f"Split {len(documents)} documents into {len(chunked_docs)} chunks")
                
                # 3. Generate embeddings and preparing points
                logger.info("Generating embeddings and preparing points...")
                texts = [doc["text"] for doc in chunked_docs]
                vectors = self.embeddings.embed_documents(texts)
                
                points = []
                for i, (doc, vector) in enumerate(zip(chunked_docs, vectors)):
                    # Use unique ID for each chunk
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"product_{doc.get('id')}_chunk_{doc['metadata']['chunk_id']}"))
                    
                    payload = doc.get("metadata", {})
                    payload["text"] = doc["text"]
                    
                    points.append({
                        "id": point_id,
                        "vector": vector,
                        "payload": payload
                    })
                
                # 3. Upload points in batches
                batch_size = 50
                for i in range(0, len(points), batch_size):
                    batch = points[i : i + batch_size]
                    logger.info(f"Uploading batch {i//batch_size + 1} ({len(batch)} points)...")
                    response = await client.put(
                        f"{self.base_url}/collections/{settings.vector_store.collection_name}/points?wait=true",
                        json={"points": batch}
                    )
                    response.raise_for_status()
            
            logger.info("✓ Indexing completed successfully via REST.")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to index documents: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
