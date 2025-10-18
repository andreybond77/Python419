# config.py
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Поле для хранения ключа Telegram бота
    tg_bot_key: str = Field(..., description="Telegram Bot API Key")

    class Config:
        # Указываем Pydantic загрузить значения из файла .env
        env_file = ".env"


# Создаем глобальный экземпляр настроек
settings = Settings()