# main.py
from fastapi import FastAPI
# Импортируем роутер для продуктов
from routes.products import router as products_router
# Импортируем настройки
from config import settings

# Создаем экземпляр FastAPI приложения
app = FastAPI(
    title="Бондарчук Андрей — Домашнее задание №34",
    description="Интеграция Telegram Bot уведомлений через BackgroundTasks",
    version="1.0.0"
)

# Подключаем роутер для продуктов к главному приложению
app.include_router(products_router)

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
            "tg_bot_key_preview": masked_key # Показываем только начало ключа
        }
    }

# Все эндпоинты для продуктов теперь находятся в routes/products.py
# Импорты для data, schemas, utils больше не нужны здесь,
# так как они теперь находятся в соответствующих файлах, где используются.

