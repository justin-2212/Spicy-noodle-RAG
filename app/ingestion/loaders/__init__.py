"""Loaders package for ingestion pipeline."""

from app.ingestion.loaders.category_loader import CategoryLoader
from app.ingestion.loaders.topping_loader import ToppingLoader
from app.ingestion.loaders.review_loader import ReviewLoader
from app.ingestion.loaders.product_loader import ProductLoader
from app.ingestion.loaders.combo_loader import ComboLoader

__all__ = [
    'CategoryLoader',
    'ToppingLoader',
    'ReviewLoader',
    'ProductLoader',
    'ComboLoader',
]
