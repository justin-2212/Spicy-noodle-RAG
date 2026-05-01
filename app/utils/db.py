"""Database utilities and connection management."""

from typing import Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings
from app.utils.exceptions import DatabaseError
from app.utils.logger import logger


class DatabasePool:
    """PostgreSQL connection pool manager."""
    
    def __init__(self):
        """Initialize database pool."""
        self.engine = None
        self.session_maker = None
        
    async def init(self):
        """Initialize connection pool."""
        try:
            # Convert postgresql:// to postgresql+asyncpg://
            db_url = settings.database.url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )
            
            self.engine = create_async_engine(
                db_url,
                echo=settings.database.echo,
                pool_size=settings.database.pool_size,
                max_overflow=10,
            )
            
            self.session_maker = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            
            logger.info("Database pool initialized")
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database: {str(e)}")
    
    async def close(self):
        """Close all connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database pool closed")
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session.
        
        Yields:
            AsyncSession
        """
        if not self.session_maker:
            raise DatabaseError("Database not initialized")
        
        async with self.session_maker() as session:
            yield session


# Global database pool
db_pool = DatabasePool()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection for database session."""
    async for session in db_pool.get_session():
        yield session
