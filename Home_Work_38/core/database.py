
# core/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from core.config import settings

# Создаем асинхронный движок для SQLite
engine = create_async_engine(
    settings.database_url,
    echo=True,
    future=True
)

# Создаем фабрику сессий
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncSession:
    """
    Dependency для получения асинхронной сессии БД.
    Используется в роутерах FastAPI.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """
    Создает таблицы в базе данных (для разработки).
    В продакшене используйте миграции Alembic.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)