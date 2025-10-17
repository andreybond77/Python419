from fastapi import FastAPI, HTTPException, Path, Query
from typing import List, Optional, Dict
from data import products
from schemas.product import Product
from schemas.product_create import ProductCreate
from utils.helpers import get_next_id

app = FastAPI(
    title="Бондарчук Андрей — Домашнее задание №32",
    description="REST API для интернет-магазина товаров из вселенной Рика и Морти",
    version="1.0.0"
)

# --- READ (List) ---
@app.get(
    path="/products/",
    response_model=List[Product],
    status_code=200,
    summary="Получить все продукты",
    tags=["Products"]
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
@app.get(
    path="/products/{product_id}",
    response_model=Product,
    status_code=200,
    summary="Получить продукт по ID",
    tags=["Products"]
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
@app.post(
    path="/products/",
    response_model=Product,
    status_code=201,
    summary="Создать новый продукт",
    tags=["Products"]
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
        **product_data.model_dump()
    }
    products.append(new_product)
    return new_product


# --- UPDATE ---
@app.put(
    path="/products/{product_id}",
    response_model=Product,
    status_code=200,
    summary="Обновить продукт",
    tags=["Products"]
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
                **product_data.model_dump()
            }
            products[i] = updated_product
            return updated_product

    raise HTTPException(status_code=404, detail="Продукт не найден")


# --- DELETE ---
@app.delete(
    path="/products/{product_id}",
    status_code=204,
    summary="Удалить продукт",
    tags=["Products"]
)
async def delete_product(
    product_id: int = Path(..., ge=1, description="ID продукта")
):
    """
    Удаляет продукт по ID.
    """
    for i, product in enumerate(products):
        if product["id"] == product_id:
            products.pop(i)
            return # 204 No Content
    raise HTTPException(status_code=404, detail="Продукт не найден")


# --- ROOT ---
@app.get("/", status_code=200)
async def root():
    """
    Корневой маршрут — перенаправление в Swagger UI.
    """
    return {"message": "Добро пожаловать в API! Перейдите на /docs для просмотра документации."}
