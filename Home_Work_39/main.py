# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import logging

# Импорты FastAPI Users
from fastapi_users import FastAPIUsers
from auth.backend import auth_backend
from auth.manager import get_user_manager
from models.user import User
from schemas.user import UserRead, UserCreate, UserUpdate

from core.config import settings
from routes import categories, products

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description=settings.app_description
)

# --- FastAPI Users (Auth) ---
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Подключаем роутеры аутентификации
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Подключаем существующие роутеры
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(categories.router, prefix="/api/v1", tags=["categories"])

# Монтирование статических файлов
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
logger.info("✅ Статические файлы (uploads) подключены")

logger.info("✅ Система аутентификации FastAPI Users подключена")

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в FastAPI Shop!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)