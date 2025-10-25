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
        logging.info(
            f'Сообщение "{message}" отправлено в чат {settings.telegram_user_id}'
        )
    except Exception as e:
        logging.error(
            f"Ошибка отправки сообщения в чат {settings.telegram_user_id}: {e}"
        )
        raise
    else:
        logging.debug(f"Сообщение успешно отправлено: {message}")

#############################################

# import logging
# import telegram
# from config import settings

# # Настройка логирования
# logging.basicConfig(level=logging.DEBUG)


# async def send_telegram_message(message: str, parse_mode: str = "Markdown") -> None:
#     """
#     Отправка сообщения в Telegram через бота.

#     Args:
#         message (str): Текст сообщения для отправки.
#         parse_mode (str, optional): Режим форматирования текста. Defaults to "Markdown".
#     """
#     try:
#         bot = telegram.Bot(token=settings.telegram_bot_api_key)
#         await bot.send_message(
#             chat_id=settings.telegram_user_id,
#             text=message,
#             parse_mode=parse_mode
#         )
#         logging.info(
#             f'Сообщение "{message[:50]}..." отправлено в чат {settings.telegram_user_id}' # Логируем начало сообщения
#         )
#     except Exception as e:
#         logging.error(
#             f"Ошибка отправки сообщения в чат {settings.telegram_user_id}: {e}"
#         )
#         raise # Пробрасываем исключение дальше, чтобы FastAPI мог его обработать, если нужно
#     else:
#         logging.debug(f"Сообщение успешно отправлено в чат {settings.telegram_user_id}")