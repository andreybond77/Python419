# utils/helpers.py
# Обновлен импорт, чтобы указывать на новый путь к файлу products.py
from data.products import products

def get_next_id():
    """
    Возвращает следующий доступный ID.
    """
    if not products:
        return 1
    return max(product["id"] for product in products) + 1