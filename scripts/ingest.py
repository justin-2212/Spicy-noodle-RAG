"""Run data ingestion pipeline."""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ingestion.pipeline import run_ingestion
from app.utils.logger import logger


async def main():
    """Main ingestion entry point."""
    logger.info("Starting ingestion script...")
    
    try:
        await run_ingestion()
        logger.info("Ingestion completed successfully")
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
