# config.py
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Обновленный класс настроек с новыми полями
    # tg_bot_key: str = Field(..., description="Telegram Bot API Key") # Старое имя, оставлено для совместимости
    telegram_bot_api_key: str = Field(..., description="Telegram Bot API Key")
    telegram_user_id: str = Field(..., description="Telegram Chat ID для получения уведомлений")

    class Config:
        env_file = ".env"


settings = Settings()