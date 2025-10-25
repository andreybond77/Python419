

# routes/products.py
from fastapi import APIRouter, HTTPException, Path, Query, BackgroundTasks
from typing import List, Optional, Dict # Добавлен Dict
# Импорты схем (исправлено)
from schemas.product import Product
from schemas.product_create import ProductCreate
# Импорты данных и вспомогательных функций
from data.products import products
from utils.helpers import get_next_id
# Импорт функции для отправки уведомлений
from utils.telegram import send_telegram_message

# Создаем экземпляр APIRouter с префиксом и тегами
router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# --- READ (List) ---
@router.get(
    path="/",
    response_model=List[Product],
    status_code=200,
    summary="Получить все продукты",
)
async def get_products(
    search: Optional[str] = Query(None, description="Поиск по названию или описанию"),
    currency: Optional[str] = Query(None, description="Валюта для сортировки (shmeckles, credits, flurbos)"),
    sort_order: Optional[str] = Query(None, description="Направление сортировки (asc, desc)")
):
    """
    Возвращает список всех продуктов из датасета.
    Поддерживает фильтрацию по тексту и сортировку по цене.
    """
    result = products

    # Фильтрация поиска
    if search:
        result = [
            product for product in result
            if search.lower() in product["name"].lower()
            or search.lower() in product["description"].lower()
        ]

    # Сортировка
    if currency and sort_order:
        # Проверяем, что валюта существует хотя бы в одном продукте
        if any(currency in product["prices"] for product in result):
            reverse = sort_order.lower() == "desc"
            try:
                result = sorted(
                    result,
                    key=lambda p: p["prices"].get(currency, float('-inf')), # Используем -inf, если цены нет
                    reverse=reverse
                )
            except TypeError:
                # На случай, если цены не числовые
                raise HTTPException(status_code=500, detail="Ошибка сортировки: неверный формат цены")
        else:
            # Если валюта не найдена ни в одном продукте
            result = []

    return result


# --- READ (One) ---
@router.get(
    path="/{product_id}",
    response_model=Product,
    status_code=200,
    summary="Получить продукт по ID",
)
async def get_product(
    product_id: int = Path(..., ge=1, description="ID продукта")
):
    """
    Возвращает один продукт по его ID.
    """
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Продукт не найден")


# --- CREATE ---
@router.post(
    path="/",
    response_model=Product,
    status_code=201,
    summary="Создать новый продукт",
)
async def create_product(
    product_ ProductCreate, # Исправлено: имя_параметра: Тип
    background_tasks: BackgroundTasks # Добавлен параметр для фоновых задач
):
    """
    Создаёт новый продукт и добавляет его в список.
    Также добавляет фоновую задачу для отправки уведомления в Telegram.
    """
    new_id = get_next_id()
    new_product = {
        "id": new_id,
        **product_data.model_dump() # Распаковываем данные из схемы в словарь
    }
    products.append(new_product)

    # Формируем сообщение для Telegram
    message = f"""🆕 *Создан новый продукт*

📦 *Название:* {new_product['name']}
🆔 *ID:* {new_product['id']}
📝 *Описание:* {new_product['description'][:150]}...

💰 *Цены:*
  • Шмекели: {new_product['prices'].get('shmeckles', 'N/A')}
  • Кредиты: {new_product['prices'].get('credits', 'N/A')}
  • Флурбо: {new_product['prices'].get('flurbos', 'N/A')}
"""
    # Добавляем фоновую задачу для отправки уведомления
    background_tasks.add_task(send_telegram_message, message)

    return new_product


# --- UPDATE ---
@router.put(
    path="/{product_id}",
    response_model=Product,
    status_code=200,
    summary="Обновить продукт",
)
async def update_product(
    background_tasks: BackgroundTasks, # Добавлен параметр для фоновых задач (перед path параметрами)
    product_id: int = Path(..., ge=1, description="ID продукта"),
    product_ ProductCreate = None # FastAPI автоматически валидирует через ProductCreate, исправлено: имя_параметра: Тип = значение_по_умолчанию
):
    """
    Обновляет существующий продукт по ID.
    Также добавляет фоновую задачу для отправки уведомления в Telegram.
    """
    for i, product in enumerate(products):
        if product["id"] == product_id:
            # Обновляем, сохранив ID
            updated_product = {
                "id": product_id,
                **product_data.model_dump() # Распаковываем новые данные
            }
            products[i] = updated_product

            # Формируем сообщение для Telegram
            message = f"""🔄 *Обновлён продукт*

📦 *Название:* {updated_product['name']}
🆔 *ID:* {updated_product['id']}
📝 *Описание:* {updated_product['description'][:150]}...

💰 *Цены:*
  • Шмекели: {updated_product['prices'].get('shmeckles', 'N/A')}
  • Кредиты: {updated_product['prices'].get('credits', 'N/A')}
  • Флурбо: {updated_product['prices'].get('flurbos', 'N/A')}
"""
            # Добавляем фоновую задачу для отправки уведомления
            background_tasks.add_task(send_telegram_message, message)

            return updated_product

    raise HTTPException(status_code=404, detail="Продукт не найден")


# --- DELETE ---
@router.delete(
    path="/{product_id}",
    status_code=204,
    summary="Удалить продукт",
)
async def delete_product(
    product_id: int = Path(..., ge=1, description="ID продукта")
):
    """
    Удаляет продукт по ID.
    """
    for i, product in enumerate(products):
        if product["id"] == product_id:
            products.pop(i) # Удаляем из списка
            return # 204 No Content
    raise HTTPException(status_code=404, detail="Продукт не найден")
