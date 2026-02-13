# dependencies/database.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db as get_db_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get database session.
    Automatically closes session after request.
    """
    async for session in get_db_session():
        yield session