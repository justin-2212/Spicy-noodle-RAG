"""Run data ingestion pipeline."""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.db import db_pool
from app.ingestion.pipeline import run_ingestion
from app.utils.logger import logger


async def main():
    """Main ingestion entry point."""
    logger.info("Starting ingestion script...")
    
    try:
        await db_pool.init()

        async for session in db_pool.get_session():
            documents = await run_ingestion(session)
            logger.info(
                f"Ingestion completed successfully with {len(documents) if documents else 0} documents"
            )
            break

    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        raise
    finally:
        await db_pool.close()


if __name__ == "__main__":
    asyncio.run(main())
