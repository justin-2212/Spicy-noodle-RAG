import asyncio
import asyncpg
import json

async def main():
    conn = await asyncpg.connect("postgresql://postgres:justinthang2005@localhost:5432/mi-cay")
    
    print('--- CATEGORY PANCHAN ---')
    rows = await conn.fetch("SELECT * FROM product_categories WHERE name ILIKE '%panchan%'")
    for r in rows:
        print(dict(r).get('name'))
    
    await conn.close()

asyncio.run(main())
