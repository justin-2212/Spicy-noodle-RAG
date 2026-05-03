import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils.db import db_pool
from app.models.database import Product
from sqlalchemy import select

async def main():
    await db_pool.init()
    async for session in db_pool.get_session():
        result = await session.execute(select(Product).where(Product.products_id == 5))
        p = result.scalar_one_or_none()
        if p:
            print(f"ID: 5, Name: {p.name}, is_combo: {p.is_combo}")
        else:
            print("Product 5 not found")
            
        # check all combos
        result = await session.execute(select(Product).where(Product.is_combo == True))
        combos = result.scalars().all()
        for c in combos:
            print(f"Combo ID: {c.products_id}, Name: {c.name}")
            
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(main())
