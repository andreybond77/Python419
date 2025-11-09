# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
# Импортируем роутеры для продуктов и категорий
from routes.products import router as products_router
from routes.categories import router as categories_router
# Импортируем настройки из нового места
from core.config import settings
# Импортируем функцию инициализации БД
from core.database import init_db


# Контекстный менеджер для управления жизненным циклом приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менед器 для управления жизненным циклом приложения
    """
    # Код, который выполняется при запуске приложения
    await init_db()
    print("База данных инициализирована")
    
    yield  # Здесь приложение работает
    
    # Код, который выполняется при остановке приложения
    print("Приложение остановлено")


# Создаем экземпляр FastAPI приложения с lifespan
app = FastAPI(
    title="Бондарчук Андрей — Домашнее задание №37",
    description="Интеграция SQLAlchemy 2.0 и асинхронной работы с базой данных в FastAPI",
    version="1.0.0",
    lifespan=lifespan  # Передаем lifespan
)

# Подключаем роутеры для продуктов и категорий к главному приложению
app.include_router(products_router)
app.include_router(categories_router)

# --- ROOT ---
@app.get("/", status_code=200)
async def root():
    """
    Корневой маршрут — демонстрирует работу конфигурации.
    """
    # Маскируем ключ для безопасности
    masked_key = settings.tg_bot_key[:10] + "***" if len(settings.tg_bot_key) > 10 else "***"
    return {
        "message": "Добро пожаловать в API! Перейдите на /docs для просмотра документации.",
        "config_demo": {
            "tg_bot_key_preview": masked_key  # Показываем только начало ключа
        }
    }

# Все эндпоинты для продуктов и категорий теперь находятся в соответствующих файлах