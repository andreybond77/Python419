from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from models.user import User

async def get_user_db(session: AsyncSession = Depends(get_db)) -> AsyncGenerator[SQLAlchemyUserDatabase[User, int], None]:
    """
    Dependency для получения доступа к таблице пользователей через SQLAlchemy.
    
    Args:
        session: Асинхронная сессия БД
        
    Yields:
        SQLAlchemyUserDatabase: Объект для работы с таблицей пользователей
    """
    yield SQLAlchemyUserDatabase(session, User)