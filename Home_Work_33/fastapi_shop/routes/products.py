# routes/products.py
from fastapi import APIRouter, HTTPException, Path, Query
from typing import List, Optional, Dict
# Импорты схем
from schemas.product import Product
from schemas.product_create import ProductCreate
# Импорты данных и вспомогательных функций
from data.products import products
from utils.helpers import get_next_id

# Создаем экземпляр APIRouter с префиксом и тегами
router = APIRouter(
    prefix="/products", # Все маршруты в этом файле будут начинаться с /products
    tags=["Products"]    # Группируем в Swagger UI под тегом "Products"
)

# --- READ (List) ---
@router.get(
    path="/", # Путь внутри роутера, становится /products/
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
    path="/{product_id}", # Путь внутри роутера, становится /products/{product_id}
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
    path="/", # Путь внутри роутера, становится /products/
    response_model=Product,
    status_code=201,
    summary="Создать новый продукт",
)
async def create_product(
    product_data: ProductCreate
):
    """
    Создаёт новый продукт и добавляет его в список.
    """
    new_id = get_next_id()
    new_product = {
        "id": new_id,
        **product_data.model_dump() # Распаковываем данные из схемы в словарь
    }
    products.append(new_product)
    return new_product


# --- UPDATE ---
@router.put(
    path="/{product_id}", # Путь внутри роутера, становится /products/{product_id}
    response_model=Product,
    status_code=200,
    summary="Обновить продукт",
)
async def update_product(
    product_id: int = Path(..., ge=1, description="ID продукта"),
    product_data: ProductCreate = None # FastAPI автоматически валидирует через ProductCreate
):
    """
    Обновляет существующий продукт по ID.
    """
    for i, product in enumerate(products):
        if product["id"] == product_id:
            # Обновляем, сохранив ID
            updated_product = {
                "id": product_id,
                **product_data.model_dump() # Распаковываем новые данные
            }
            products[i] = updated_product
            return updated_product

    raise HTTPException(status_code=404, detail="Продукт не найден")


# --- DELETE ---
@router.delete(
    path="/{product_id}", # Путь внутри роутера, становится /products/{product_id}
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

