import asyncio
import os
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.db import db_pool
from sqlalchemy import text

async def fix_reviews():
    await db_pool.init()
    async for session in db_pool.get_session():
        # Review 1: "Mì hải sản siêu ngon..." -> attach to Mì Kim Chi Hải Sản (ID 1)
        # Review 2: "Tokbokki béo ngậy..." -> attach to Tokbokki Phô Mai (ID 13)
        # Review 3: "Lẩu bò ngon..." -> attach to Lẩu Tomyum Bò (ID 8)
        
        await session.execute(text("UPDATE product_reviews SET products_id = 1 WHERE product_reviews_id = 1"))
        await session.execute(text("UPDATE product_reviews SET products_id = 13 WHERE product_reviews_id = 2"))
        await session.execute(text("UPDATE product_reviews SET products_id = 8 WHERE product_reviews_id = 3"))
        
        await session.commit()
        print("Updated reviews mapping successfully!")
        
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(fix_reviews())
