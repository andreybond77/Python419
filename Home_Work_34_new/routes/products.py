# # routes/products.py
# from fastapi import APIRouter, HTTPException, Path, Query, BackgroundTasks
# from typing import List, Optional, Dict
# from schemas.product import Product
# from schemas.product_create import ProductCreate
# from data.products import products
# from utils.helpers import get_next_id
# from utils.telegram import send_telegram_message

# router = APIRouter(
#     prefix="/products",
#     tags=["Products"]
# )

# # --- READ (List) ---
# @router.get(
#     path="/",
#     response_model=List[Product],
#     status_code=200,
#     summary="Получить все продукты",
# )
# async def get_products(
#     search: Optional[str] = Query(None, description="Поиск по названию или описанию"),
#     currency: Optional[str] = Query(None, description="Валюта для сортировки (shmeckles, credits, flurbos)"),
#     sort_order: Optional[str] = Query(None, description="Направление сортировки (asc, desc)")
# ):
#     """
#     Возвращает список всех продуктов из датасета.
#     Поддерживает фильтрацию по тексту и сортировку по цене.
#     """
#     result = products

#     if search:
#         result = [
#             product for product in result
#             if search.lower() in product["name"].lower()
#             or search.lower() in product["description"].lower()
#         ]

#     if currency and sort_order:
#         if any(currency in product["prices"] for product in result):
#             reverse = sort_order.lower() == "desc"
#             try:
#                 result = sorted(
#                     result,
#                     key=lambda p: p["prices"].get(currency, float('-inf')),
#                     reverse=reverse
#                 )
#             except TypeError:
#                 raise HTTPException(status_code=500, detail="Ошибка сортировки: неверный формат цены")
#         else:
#             result = []

#     return result


# # --- READ (One) ---
# @router.get(
#     path="/{product_id}",
#     response_model=Product,
#     status_code=200,
#     summary="Получить продукт по ID",
# )
# async def get_product(
#     product_id: int = Path(..., ge=1, description="ID продукта")
# ):
#     """
#     Возвращает один продукт по его ID.
#     """
#     for product in products:
#         if product["id"] == product_id:
#             return product
#     raise HTTPException(status_code=404, detail="Продукт не найден")


# # --- CREATE ---
# @router.post(
#     path="/",
#     response_model=Product,
#     status_code=201,
#     summary="Создать новый продукт",
# )
# async def create_product(
#     product_data: ProductCreate,  # <-- ИСПРАВЛЕНО: двоеточие между именем и типом
#     background_tasks: BackgroundTasks
# ):
#     """
#     Создаёт новый продукт и добавляет его в список.
#     Отправляет уведомление в Telegram.
#     """
#     new_id = get_next_id()
#     new_product = {
#         "id": new_id,
#         **product_data.model_dump()
#     }
#     products.append(new_product)

#     # Формируем сообщение для Telegram
#     message = f"""🆕 *Создан новый продукт*

# 📦 *Название:* {new_product['name']}
# 🆔 *ID:* {new_product['id']}
# 📝 *Описание:* {new_product['description'][:100]}...
# 💰 *Цены:* `{new_product['prices']}`
#     """

#     # Добавляем отправку уведомления в фоновую очередь
#     background_tasks.add_task(send_telegram_message, message)

#     return new_product


# # --- UPDATE ---
# @router.put(
#     path="/{product_id}",
#     response_model=Product,
#     status_code=200,
#     summary="Обновить продукт",
# )
# async def update_product(
#     product_id: int = Path(..., ge=1, description="ID продукта"),
#     product_data: ProductCreate = None,  # <-- ИСПРАВЛЕНО: обязательный параметр без значения по умолчанию
#     background_tasks: BackgroundTasks  # <-- Зависимость FastAPI
# ):
#     """
#     Обновляет существующий продукт по ID.
#     Отправляет уведомление в Telegram.
#     """
#     for i, product in enumerate(products):
#         if product["id"] == product_id:
#             updated_product = {
#                 "id": product_id,
#                 **product_data.model_dump()
#             }
#             products[i] = updated_product

#             # Формируем сообщение для Telegram об обновлении
#             message = f"""🔄 *Обновлён продукт*

# 📦 *Название:* {updated_product['name']}
# 🆔 *ID:* {updated_product['id']}
# 📝 *Описание:* {updated_product['description'][:100]}...
# 💰 *Цены:* `{updated_product['prices']}`
#     """

#             # Добавляем отправку уведомления в фоновую очередь
#             background_tasks.add_task(send_telegram_message, message)

#             return updated_product

#     raise HTTPException(status_code=404, detail="Продукт не найден")


# # --- DELETE ---
# @router.delete(
#     path="/{product_id}",
#     status_code=204,
#     summary="Удалить продукт",
# )
# async def delete_product(
#     product_id: int = Path(..., ge=1, description="ID продукта")
# ):
#     """
#     Удаляет продукт по ID.
#     """
#     for i, product in enumerate(products):
#         if product["id"] == product_id:
#             products.pop(i)
#             return
#     raise HTTPException(status_code=404, detail="Продукт не найден")

#######################################################################################

from fastapi import APIRouter, HTTPException, Path, Query, BackgroundTasks
from typing import List, Optional
from schemas.product import Product
from schemas.product_create import ProductCreate
from data.products import products
from utils.helpers import get_next_id
from utils.telegram import send_telegram_message

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
    result = products

    if search:
        result = [
            product for product in result
            if search.lower() in product["name"].lower() or search.lower() in product["description"].lower()
        ]

    if currency and sort_order:
        if any(currency in product["prices"] for product in result):
            reverse = sort_order.lower() == "desc"
            try:
                result = sorted(
                    result,
                    key=lambda p: p["prices"].get(currency, float('inf')),  # изменения здесь
                    reverse=reverse
                )
            except TypeError:
                raise HTTPException(status_code=500, detail="Ошибка сортировки: неверный формат цены")
        else:
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
    product_data: ProductCreate,  # Параметр без умолчания
    background_tasks: BackgroundTasks = None  # Параметр с умолчанием
):
    new_id = get_next_id()
    new_product = {
        "id": new_id,
        **product_data.dict()  # Здесь используйте dict()
    }
    products.append(new_product)

    message = f"""🆕 *Создан новый продукт*

📦 *Название:* {new_product['name']}
🆔 *ID:* {new_product['id']}
📝 *Описание:* {new_product['description'][:100]}...
💰 *Цены:* `{new_product['prices']}`
    """

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
    product_data: ProductCreate,  # Параметр без умолчания
    product_id: int = Path(..., ge=1, description="ID продукта"),  # Обязательный параметр
    background_tasks: BackgroundTasks = None  # Параметр с умолчанием
):
    for i, product in enumerate(products):
        if product["id"] == product_id:
            updated_product = {
                "id": product_id,
                **product_data.dict()  # Здесь используйте dict()
            }
            products[i] = updated_product

            message = f"""🔄 *Обновлён продукт*

📦 *Название:* {updated_product['name']}
🆔 *ID:* {updated_product['id']}
📝 *Описание:* {updated_product['description'][:100]}...
💰 *Цены:* `{updated_product['prices']}`
            """

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
    product_id: int = Path(..., ge=1, description="ID продукта")  # Обязательный параметр
):
    for i, product in enumerate(products):
        if product["id"] == product_id:
            products.pop(i)
            return  # Удаляем успешно, возвращаем 204 без содержимого
    raise HTTPException(status_code=404, detail="Продукт не найден")












