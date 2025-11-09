# core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import settings

import asyncio

# Импортируем модели для регистрации в Base.metadata
from models.base import Base  # Импортируем Base из пакета models
from models.product import Product  # noqa: F401 (импортируем, чтобы зарегистрировать модель)
from models.category import Category  # noqa: F401 (импортируем, чтобы зарегистрировать модель)

# URL для подключения к асинхронной SQLite
DATABASE_URL = settings.database_url


# Создание асинхронного движка базы данных
# echo=True — включает логирование SQL-запросов в консоль (полезно для отладки)
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание фабрики асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    # bind - это движок, с которым будут работать сессии
    # expire_on_commit=False - отключает автоматическое обновление объектов после коммита
    bind=engine,
    expire_on_commit=False,
)


# Стартовая инициализация базы данных
# ВАЖНО. Это не система миграций! Функция просто создает таблицы, если их нет.
# При изменении моделей таблицы НЕ изменятся автоматически.
async def init_db():
    """
    Инициализация базы данных:
    - Удаляет все существующие таблицы (для чистоты эксперимента)
    - Создает таблицы заново на основе зарегистрированных моделей
    """
    async with engine.begin() as conn:
        # Для чистоты эксперимента будем удалять таблицы и пересоздавать их
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)