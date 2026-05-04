"""Ingestion pipeline orchestrator for RAG system."""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.logger import logger
from app.ingestion.loaders import ProductLoader, CategoryLoader, ToppingLoader
from app.ingestion.builders import ProductDocumentBuilder


class IngestionPipeline:
    """
    Orchestrate data ingestion from PostgreSQL to prepare documents for RAG.
    
    Pipeline flow:
    1. Load products from PostgreSQL with all relationships
    2. Load categories, toppings, reviews
    3. Build RAG-ready documents from loaded data
    4. Prepare documents for embedding and indexing
    """
    
    def __init__(self):
        """Initialize pipeline."""
        self.logger = logger
        self.documents: List[Dict[str, Any]] = []
        self.categories: List[Dict[str, Any]] = []
        self.toppings: List[Dict[str, Any]] = []
        self.reviews: List[Dict[str, Any]] = []
        self.products: List[Dict[str, Any]] = []
    
    async def load_from_database(self, session: AsyncSession) -> bool:
        """
        Load all data from PostgreSQL.
        
        Args:
            session: AsyncSession for database queries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("\n" + "="*70)
            self.logger.info("STEP 1: Loading data from PostgreSQL")
            self.logger.info("="*70)
            
            # Load categories
            self.categories = await CategoryLoader.load_all(session)
            
            # Load toppings
            self.toppings = await ToppingLoader.load_all(session)
            
            # Load products with relationships (Toppings and Reviews included for Stage B)
            self.products = await ProductLoader.load_all(
                session, 
                include_toppings=True, 
                include_reviews=True
            )
            
            self.logger.info(f"\n✓ Stage B Data loaded successfully:")
            self.logger.info(f"  • Categories: {len(self.categories)}")
            self.logger.info(f"  • Products: {len(self.products)}")
            self.logger.info(f"  • Toppings: {len(self.toppings)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to load data from database: {str(e)}")
            return False
    
    async def build_documents(self) -> bool:
        """
        Build RAG-ready documents from loaded product data.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("\n" + "="*70)
            self.logger.info("STEP 2: Building RAG documents")
            self.logger.info("="*70)
            
            if not self.products:
                self.logger.error("✗ No products loaded")
                return False
            
            # Build product documents
            self.documents = ProductDocumentBuilder.build_documents_batch(self.products)
            
            # Build topping summary document
            if self.toppings:
                topping_doc = ProductDocumentBuilder.build_topping_summary_document(self.toppings)
                if topping_doc:
                    self.documents.append(topping_doc)
                    self.logger.info("✓ Added Topping Summary document")
            
            # Build menu summary document
            if self.products:
                menu_doc = ProductDocumentBuilder.build_menu_summary_document(self.products)
                if menu_doc:
                    self.documents.append(menu_doc)
                    self.logger.info("✓ Added Menu Summary document")
            
            # Get stats
            stats = ProductDocumentBuilder.get_document_stats(self.documents)
            
            self.logger.info(f"\n✓ Documents built successfully:")
            self.logger.info(f"  • Total documents: {stats['total_documents']}")
            self.logger.info(f"  • Avg text length: {stats['avg_text_length']} chars")
            self.logger.info(f"  • Avg rating: {stats['avg_rating']}/5.0")
            self.logger.info(f"  • Total reviews: {stats['total_reviews']}")
            self.logger.info(f"  • Combos: {stats['combos']}")
            self.logger.info(f"  • Best sellers: {stats['best_sellers']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to build documents: {str(e)}")
            return False
    
    async def run(
        self,
        session: AsyncSession,
        skip_embedding: bool = False
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Run full ingestion pipeline.
        
        Args:
            session: AsyncSession for database queries
            skip_embedding: If True, stop after document building (for now)
            
        Returns:
            List of RAG documents, or None if failed
        """
        try:
            self.logger.info("\n" + "🚀"*35)
            self.logger.info("  RAG INGESTION PIPELINE - STARTING")
            self.logger.info("🚀"*35)
            
            # Step 1: Load from database
            if not await self.load_from_database(session):
                return None
            
            # Step 2: Build documents
            if not await self.build_documents():
                return None
            
            # Step 3-5: Placeholder for future implementation
            if skip_embedding:
                self.logger.info("\n" + "="*70)
                self.logger.info("⏭️  Skipping embedding & indexing")
                self.logger.info("="*70)
            else:
                self.logger.info("\n" + "="*70)
                self.logger.info("STEP 3: Embedding and Indexing to Qdrant")
                self.logger.info("="*70)
                from app.ingestion.indexer import QdrantIndexer
                indexer = QdrantIndexer()
                success = await indexer.index_documents(self.documents)
                if not success:
                    return None
            
            self.logger.info("\n" + "✓"*35)
            self.logger.info("  INGESTION PIPELINE - COMPLETED")
            self.logger.info("✓"*35 + "\n")
            
            return self.documents
            
        except Exception as e:
            self.logger.error(f"✗ Ingestion pipeline failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_documents(self) -> List[Dict[str, Any]]:
        """
        Get built documents.
        
        Returns:
            List of RAG documents
        """
        return self.documents
    
    def get_document_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by product ID.
        
        Args:
            product_id: Product ID to search for
            
        Returns:
            Document dictionary or None
        """
        for doc in self.documents:
            if doc['id'] == product_id:
                return doc
        return None


async def run_ingestion(session: AsyncSession, skip_embedding: bool = False):
    """
    Run ingestion from script or API.
    
    Args:
        session: AsyncSession for database queries
        skip_embedding: Whether to skip embedding/indexing
    """
    pipeline = IngestionPipeline()
    documents = await pipeline.run(session, skip_embedding=skip_embedding)
    return documents

