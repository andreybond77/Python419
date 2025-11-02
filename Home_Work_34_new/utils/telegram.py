# utils/telegram.py
import logging
import telegram
from config import settings

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)


async def send_telegram_message(message: str, parse_mode: str = "Markdown") -> None:
    """Отправка сообщения в Telegram через бота"""
    try:
        bot = telegram.Bot(token=settings.telegram_bot_api_key)
        await bot.send_message(
            chat_id=settings.telegram_user_id,
            text=message,
            parse_mode=parse_mode
        )
        # Логируем успешную отправку
        logging.info(
            f'Сообщение "{message}" отправлено в чат {settings.telegram_user_id}'
        )
    except Exception as e:
        # Логируем ошибку, если она произошла
        logging.error(
            f"Ошибка отправки сообщения в чат {settings.telegram_user_id}: {e}"
        )
        # Пробрасываем исключение дальше
        raise
    else:
        # Логируем успешную отправку (альтернативно или дополнительно)
        logging.debug(f"Сообщение успешно отправлено: {message}")