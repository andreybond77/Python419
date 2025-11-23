# core/config.py
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Settings:
    """Настройки приложения без использования Pydantic"""
    
    def __init__(self):
        # Настройки базы данных
        self.database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
        
        # Настройки Telegram бота
        self.telegram_bot_api_key = os.getenv("TELEGRAM_BOT_API_KEY")
        self.telegram_user_id = os.getenv("TELEGRAM_USER_ID")
        
        # Настройки приложения
        self.app_title = "Бондарчук Андрей домашнее задание № 37"
        self.app_version = "1.0.0"
        self.app_description = "API для интернет-магазина"
        
        # Настройки безопасности
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")

# Создаем экземпляр настроек
settings = Settings()