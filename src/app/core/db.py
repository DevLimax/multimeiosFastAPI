from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.core.configs import settings

engine: AsyncEngine = create_async_engine(
    settings.DB_URL, 
)

Session: AsyncSession = sessionmaker(
    autoflush=False,
    expire_on_commit=False,
    autocommit=False,
    class_=AsyncSession,
    bind=engine
)

