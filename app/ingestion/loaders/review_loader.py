"""Review loader for ingestion pipeline."""

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import ProductReview
from app.utils.logger import logger


class ReviewLoader:
    """Load product reviews from PostgreSQL."""
    
    @staticmethod
    async def load_all(session: AsyncSession) -> List[Dict[str, Any]]:
        """
        Load all approved reviews from database.
        
        Args:
            session: AsyncSession for database queries
            
        Returns:
            List of review dictionaries
        """
        try:
            logger.info("Loading product reviews from database...")
            
            # Query all approved reviews
            query = select(ProductReview).where(
                ProductReview.is_approved == True
            ).order_by(ProductReview.product_reviews_id)
            
            result = await session.execute(query)
            reviews = result.scalars().all()
            
            reviews_data = [
                {
                    'id': review.product_reviews_id,
                    'product_id': review.products_id,
                    'rating': review.rating,
                    'comment': review.comment,
                }
                for review in reviews
            ]
            
            logger.info(f"✓ Loaded {len(reviews_data)} reviews")
            return reviews_data
            
        except Exception as e:
            logger.error(f"✗ Failed to load reviews: {str(e)}")
            raise
    
    @staticmethod
    async def load_by_product_id(
        session: AsyncSession,
        product_id: int
    ) -> List[Dict[str, Any]]:
        """
        Load reviews for a specific product.
        
        Args:
            session: AsyncSession for database queries
            product_id: Product ID to load reviews for
            
        Returns:
            List of review dictionaries for the product
        """
        try:
            query = select(ProductReview).where(
                (ProductReview.products_id == product_id) &
                (ProductReview.is_approved == True)
            ).order_by(ProductReview.created_at.desc())
            
            result = await session.execute(query)
            reviews = result.scalars().all()
            
            reviews_data = [
                {
                    'id': review.product_reviews_id,
                    'rating': review.rating,
                    'comment': review.comment,
                }
                for review in reviews
            ]
            
            logger.debug(f"Loaded {len(reviews_data)} reviews for product {product_id}")
            return reviews_data
            
        except Exception as e:
            logger.error(f"✗ Failed to load reviews for product {product_id}: {str(e)}")
            raise
