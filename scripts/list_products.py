import asyncio
import os
import sys
import io

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.utils.db import db_pool
from app.models.database import Product
from sqlalchemy import select

async def list_products():
    await db_pool.init()
    async for session in db_pool.get_session():
        result = await session.execute(select(Product))
        products = result.scalars().all()
        for p in products:
            print(f"ID: {p.products_id} | Name: {p.name} | Price: {p.price}")
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(list_products())
