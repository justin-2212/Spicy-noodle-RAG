"""Initialize Qdrant vector store."""

import asyncio
from app.utils.logger import logger


async def init_qdrant():
    """Initialize Qdrant collections."""
    from app.config.settings import settings
    from qdrant_client import AsyncQdrantClient
    
    logger.info("Initializing Qdrant...")
    
    try:
        client = AsyncQdrantClient(
            host=settings.vector_store.host,
            port=settings.vector_store.port
        )
        
        # Check connection
        collection_info = await client.get_collections()
        logger.info(f"Connected to Qdrant. Collections: {collection_info}")
        
        # TODO: Create collection if it doesn't exist
        # collection_name = settings.vector_store.collection_name
        # if collection_name not in [c.name for c in collection_info.collections]:
        #     await client.create_collection(...)
        
        logger.info("Qdrant initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(init_qdrant())
