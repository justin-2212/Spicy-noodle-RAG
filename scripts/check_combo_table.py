import asyncio
import os
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.db import db_pool
from sqlalchemy import text

async def check_db():
    await db_pool.init()
    async for session in db_pool.get_session():
        result = await session.execute(text("SELECT * FROM combo_components"))
        rows = result.all()
        for r in rows:
            print(f"combo_product_id: {r[0]}, component_product_id: {r[1]}, quantity: {r[2]}")
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(check_db())
