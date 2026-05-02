"""Topping loader for ingestion pipeline."""

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import Topping
from app.utils.logger import logger


class ToppingLoader:
    """Load toppings from PostgreSQL."""
    
    @staticmethod
    async def load_all(session: AsyncSession) -> List[Dict[str, Any]]:
        """
        Load all active toppings from database.
        
        Args:
            session: AsyncSession for database queries
            
        Returns:
            List of topping dictionaries
        """
        try:
            logger.info("Loading toppings from database...")
            
            # Query all active toppings
            query = select(Topping).where(
                Topping.is_active == True
            ).order_by(Topping.toppings_id)
            
            result = await session.execute(query)
            toppings = result.scalars().all()
            
            toppings_data = [
                {
                    'id': topping.toppings_id,
                    'name': topping.name,
                    'price': topping.price,
                    'product_id': topping.products_id,
                    'is_active': topping.is_active,
                }
                for topping in toppings
            ]
            
            logger.info(f"✓ Loaded {len(toppings_data)} toppings")
            return toppings_data
            
        except Exception as e:
            logger.error(f"✗ Failed to load toppings: {str(e)}")
            raise
    
    @staticmethod
    async def load_by_product_id(
        session: AsyncSession,
        product_id: int
    ) -> List[Dict[str, Any]]:
        """
        Load toppings for a specific product.
        
        Args:
            session: AsyncSession for database queries
            product_id: Product ID to load toppings for
            
        Returns:
            List of topping dictionaries for the product
        """
        try:
            query = select(Topping).where(
                (Topping.products_id == product_id) &
                (Topping.is_active == True)
            ).order_by(Topping.toppings_id)
            
            result = await session.execute(query)
            toppings = result.scalars().all()
            
            toppings_data = [
                {
                    'id': topping.toppings_id,
                    'name': topping.name,
                    'price': topping.price,
                }
                for topping in toppings
            ]
            
            logger.debug(f"Loaded {len(toppings_data)} toppings for product {product_id}")
            return toppings_data
            
        except Exception as e:
            logger.error(f"✗ Failed to load toppings for product {product_id}: {str(e)}")
            raise
