"""Combo loader for ingestion pipeline."""

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import combo_components_association, Product
from app.utils.logger import logger


class ComboLoader:
    """Load combo components from PostgreSQL."""
    
    @staticmethod
    async def load_by_combo_id(
        session: AsyncSession,
        combo_id: int
    ) -> List[Dict[str, Any]]:
        """
        Load component products for a specific combo.
        
        Args:
            session: AsyncSession for database queries
            combo_id: Product ID of the combo
            
        Returns:
            List of component product dictionaries
        """
        try:
            # Join with Product table to get component details
            query = select(
                Product.products_id,
                Product.name,
                combo_components_association.c.quantity
            ).join(
                combo_components_association,
                Product.products_id == combo_components_association.c.component_product_id
            ).where(
                combo_components_association.c.combo_product_id == combo_id
            )
            
            result = await session.execute(query)
            components = result.all()
            
            components_data = [
                {
                    'id': row.products_id,
                    'name': row.name,
                    'quantity': row.quantity,
                }
                for row in components
            ]
            
            if components_data:
                logger.debug(f"Loaded {len(components_data)} components for combo {combo_id}")
            return components_data
            
        except Exception as e:
            logger.error(f"✗ Failed to load combo components for combo {combo_id}: {str(e)}")
            raise
