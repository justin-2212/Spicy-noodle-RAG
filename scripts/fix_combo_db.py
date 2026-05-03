import asyncio
import os
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.db import db_pool
from sqlalchemy import text

async def fix_db():
    await db_pool.init()
    async for session in db_pool.get_session():
        # Clear existing combo components
        await session.execute(text("DELETE FROM combo_components"))
        
        # Add Combo Cặp Đôi Hoàn Hảo (ID: 20)
        # 1 Mì Kim Chi Hải Sản (ID 1), 1 Mì Kim Chi Bò Mỹ (ID 2), 1 Tokbokki Phô Mai (ID 13), 2 Pepsi (ID 17)
        combo_20 = [
            (20, 1, 1),
            (20, 2, 1),
            (20, 13, 1),
            (20, 17, 2),
        ]
        
        # Add Combo Sinh Viên (ID: 19)
        # 1 Mì Kim Chi Bò Mỹ (ID 2), 1 Pepsi (ID 17)
        combo_19 = [
            (19, 2, 1),
            (19, 17, 1),
        ]
        
        for combo_id, comp_id, qty in combo_20 + combo_19:
            await session.execute(
                text("INSERT INTO combo_components (combo_product_id, component_product_id, quantity) VALUES (:c_id, :comp_id, :qty)"),
                {"c_id": combo_id, "comp_id": comp_id, "qty": qty}
            )
        
        await session.commit()
        print("Updated combo_components successfully!")
        
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(fix_db())
