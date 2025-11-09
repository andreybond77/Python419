# core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Класс для хранения настроек приложения.
    Pydantic автоматически загружает значения из переменных окружения или файла .env.
    """
    # Поля для Telegram Bot (из предыдущих заданий)
    tg_bot_key: str = Field(..., description="Telegram Bot API Key (from previous HW)")
    telegram_bot_api_key: str = Field(..., description="Telegram Bot API Token")
    telegram_user_id: str = Field(..., description="Telegram Chat ID for notifications")
    # Новое поле для подключения к БД
    database_url: str = Field(
        ..., 
        description="URL для подключения к базе данных"
    )


    class Config:
        # Указываем Pydantic загрузить значения из файла .env
        env_file = ".env"


# Создаем глобальный экземпляр настроек
settings = Settings()