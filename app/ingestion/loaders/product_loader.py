"""Product loader for ingestion pipeline."""

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.database import Product, ProductCategory
from app.ingestion.loaders.topping_loader import ToppingLoader
from app.ingestion.loaders.review_loader import ReviewLoader
from app.ingestion.loaders.combo_loader import ComboLoader
from app.utils.logger import logger


class ProductLoader:
    """Load products with all relationships from PostgreSQL."""
    
    @staticmethod
    async def load_all(
        session: AsyncSession,
        include_toppings: bool = True,
        include_reviews: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Load all active products with relationships from database.
        
        Args:
            session: AsyncSession for database queries
            include_toppings: Whether to load toppings
            include_reviews: Whether to load reviews
            
        Returns:
            List of product dictionaries with all relationships
        """
        try:
            logger.info("Loading products from database...")
            
            # Query all active products with eager loading of relationships
            query = select(Product).where(
                Product.is_active == True
            ).options(
                selectinload(Product.category),
            ).order_by(Product.products_id)
            
            result = await session.execute(query)
            products = result.scalars().unique().all()
            
            logger.info(f"Found {len(products)} active products")
            
            # Load complete product data
            products_data = []
            for product in products:
                product_data = await ProductLoader._build_product_data(
                    session, product,
                    include_toppings=include_toppings,
                    include_reviews=include_reviews
                )
                products_data.append(product_data)
            
            logger.info(f"✓ Loaded {len(products_data)} products with relationships")
            return products_data
            
        except Exception as e:
            logger.error(f"✗ Failed to load products: {str(e)}")
            raise
    
    @staticmethod
    async def load_by_category(
        session: AsyncSession,
        category_id: int
    ) -> List[Dict[str, Any]]:
        """
        Load products by category.
        
        Args:
            session: AsyncSession for database queries
            category_id: Category ID to filter by
            
        Returns:
            List of product dictionaries
        """
        try:
            query = select(Product).where(
                (Product.product_categories_id == category_id) &
                (Product.is_active == True)
            ).options(
                selectinload(Product.category),
            ).order_by(Product.products_id)
            
            result = await session.execute(query)
            products = result.scalars().unique().all()
            
            products_data = []
            for product in products:
                product_data = await ProductLoader._build_product_data(
                    session, product
                )
                products_data.append(product_data)
            
            logger.info(f"Loaded {len(products_data)} products from category {category_id}")
            return products_data
            
        except Exception as e:
            logger.error(f"✗ Failed to load products for category {category_id}: {str(e)}")
            raise
    
    @staticmethod
    async def load_by_id(
        session: AsyncSession,
        product_id: int
    ) -> Dict[str, Any]:
        """
        Load a single product by ID with all relationships.
        
        Args:
            session: AsyncSession for database queries
            product_id: Product ID to load
            
        Returns:
            Product dictionary with all relationships
        """
        try:
            query = select(Product).where(
                Product.products_id == product_id
            ).options(
                selectinload(Product.category),
            )
            
            result = await session.execute(query)
            product = result.scalar_one_or_none()
            
            if not product:
                logger.warning(f"Product {product_id} not found")
                return None
            
            product_data = await ProductLoader._build_product_data(
                session, product
            )
            
            return product_data
            
        except Exception as e:
            logger.error(f"✗ Failed to load product {product_id}: {str(e)}")
            raise
    
    @staticmethod
    async def _build_product_data(
        session: AsyncSession,
        product: Product,
        include_toppings: bool = True,
        include_reviews: bool = False
    ) -> Dict[str, Any]:
        """
        Build complete product data dictionary with all relationships.
        
        Args:
            session: AsyncSession for database queries
            product: Product ORM object
            include_toppings: Whether to load toppings
            include_reviews: Whether to load reviews
            
        Returns:
            Complete product data dictionary
        """
        # Load toppings
        toppings = []
        if include_toppings:
            toppings = await ToppingLoader.load_by_product_id(
                session, product.products_id
            )
        
        # Load reviews
        reviews = []
        if include_reviews:
            reviews = await ReviewLoader.load_by_product_id(
                session, product.products_id
            )
        
        # Load combo components
        combo_components = []
        if product.is_combo:
            combo_components = await ComboLoader.load_by_combo_id(
                session, product.products_id
            )
        
        # Build product data
        product_data = {
            'id': product.products_id,
            'name': product.name,
            'price': product.price,
            'category': {
                'id': product.category.product_categories_id,
                'name': product.category.name,
            } if product.category else None,
            'max_spicy_level': product.max_spicy_level,
            'stock_quantity': product.stock_quantity,
            'is_active': product.is_active,
            'short_description': product.short_description or '',
            'is_best_seller': product.is_best_seller,
            'is_combo': product.is_combo,
            'average_rating': product.average_rating,
            'rating_count': product.rating_count,
            'toppings': toppings,
            'reviews': reviews,
            'combo_components': combo_components,
        }
        
        return product_data
    
    @staticmethod
    async def load_best_sellers(
        session: AsyncSession,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Load best-seller products.
        
        Args:
            session: AsyncSession for database queries
            limit: Maximum number of products to return
            
        Returns:
            List of best-seller product dictionaries
        """
        try:
            query = select(Product).where(
                (Product.is_active == True) &
                (Product.is_best_seller == True)
            ).options(
                selectinload(Product.category),
            ).order_by(
                Product.average_rating.desc(),
                Product.rating_count.desc()
            ).limit(limit)
            
            result = await session.execute(query)
            products = result.scalars().unique().all()
            
            products_data = []
            for product in products:
                product_data = await ProductLoader._build_product_data(
                    session, product
                )
                products_data.append(product_data)
            
            logger.info(f"Loaded {len(products_data)} best-seller products")
            return products_data
            
        except Exception as e:
            logger.error(f"✗ Failed to load best-seller products: {str(e)}")
            raise
