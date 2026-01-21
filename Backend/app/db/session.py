from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator, Annotated
from app.core.config import get_db_settings, get_settings
from fastapi import Depends

# Get database and general settings
db_settings = get_db_settings()
settings = get_settings()

engine = create_async_engine(
    db_settings.POSTGRES_URL(),
    pool_pre_ping=True,
    echo=settings.debug,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session with proper cleanup"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Type annotation for dependency injection
SessionDep = Annotated[AsyncSession, Depends(get_db)]