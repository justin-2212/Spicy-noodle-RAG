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
from sqlalchemy import text

async def check_db():
    await db_pool.init()
    async for session in db_pool.get_session():
        # Check products 1, 2, 3
        res = await session.execute(text("SELECT products_id, name FROM products WHERE products_id IN (1, 2, 3)"))
        print("Products:")
        for r in res.all():
            print(r)
            
        # Check reviews
        res = await session.execute(text("SELECT product_reviews_id, products_id, comment FROM product_reviews"))
        print("\nReviews:")
        for r in res.all():
            print(r)
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(check_db())
