# config.py
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Класс для хранения настроек приложения.
    Pydantic автоматически загружает значения из переменных окружения или файла .env.
    """
    # Поле для хранения ключа Telegram бота (из ДЗ №33)
    tg_bot_key: str = Field(..., description="Telegram Bot API Key (from previous HW)")
    # Новые поля для ДЗ №34
    telegram_bot_api_key: str = Field(..., description="Telegram Bot API Token")
    telegram_user_id: str = Field(..., description="Telegram Chat ID for notifications")


    class Config:
        # Указываем Pydantic загрузить значения из файла .env
        env_file = ".env"


# Создаем глобальный экземпляр настроек
settings = Settings()