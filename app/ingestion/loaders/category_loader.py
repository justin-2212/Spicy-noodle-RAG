"""Category loader for ingestion pipeline."""

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import ProductCategory
from app.utils.logger import logger


class CategoryLoader:
    """Load product categories from PostgreSQL."""
    
    @staticmethod
    async def load_all(session: AsyncSession) -> List[Dict[str, Any]]:
        """
        Load all product categories from database.
        
        Args:
            session: AsyncSession for database queries
            
        Returns:
            List of category dictionaries
        """
        try:
            logger.info("Loading product categories from database...")
            
            # Query all active categories
            query = select(ProductCategory).where(
                ProductCategory.is_active == True
            ).order_by(ProductCategory.product_categories_id)
            
            result = await session.execute(query)
            categories = result.scalars().all()
            
            categories_data = [
                {
                    'id': cat.product_categories_id,
                    'name': cat.name,
                    'created_at': cat.created_at,
                    'is_active': cat.is_active,
                }
                for cat in categories
            ]
            
            logger.info(f"✓ Loaded {len(categories_data)} categories")
            return categories_data
            
        except Exception as e:
            logger.error(f"✗ Failed to load categories: {str(e)}")
            raise
    
    @staticmethod
    async def load_by_id(session: AsyncSession, category_id: int) -> Dict[str, Any]:
        """
        Load a specific category by ID.
        
        Args:
            session: AsyncSession for database queries
            category_id: Category ID to load
            
        Returns:
            Category dictionary
        """
        try:
            query = select(ProductCategory).where(
                ProductCategory.product_categories_id == category_id
            )
            
            result = await session.execute(query)
            category = result.scalar_one_or_none()
            
            if not category:
                logger.warning(f"Category {category_id} not found")
                return None
            
            return {
                'id': category.product_categories_id,
                'name': category.name,
                'created_at': category.created_at,
                'is_active': category.is_active,
            }
            
        except Exception as e:
            logger.error(f"✗ Failed to load category {category_id}: {str(e)}")
            raise
