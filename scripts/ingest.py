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
    logger.info("--- Starting Ingestion Process ---")
    
    try:
        await db_pool.init()

        async for session in db_pool.get_session():
            logger.info("Running ingestion pipeline...")
            documents = await run_ingestion(session)
            count = len(documents) if documents else 0
            logger.info(f"SUCCESS: Ingestion completed with {count} documents.")
            break
        
        sys.exit(0)

    except Exception as e:
        logger.error(f"FATAL ERROR during ingestion: {str(e)}")
        logger.exception(e)
        sys.exit(1)
    finally:
        await db_pool.close()
        logger.info("--- Ingestion Process Finished ---")



if __name__ == "__main__":
    asyncio.run(main())
