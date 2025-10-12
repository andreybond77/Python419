from fastapi import FastAPI
from typing import List
from data import products
from schemas.product import Product

app = FastAPI(
    title="Бондарчук Андрей — Домашнее задание №31",
    description="REST API для интернет-магазина товаров из вселенной Рика и Морти",
    version="1.0.0"
)


@app.get(
    path="/products/",
    response_model=List[Product],
    status_code=200,
    summary="Получить все продукты",
    tags=["Products"]
)
async def get_products():
    """
    Возвращает список всех продуктов из датасета.
    """
    return products


@app.get("/", status_code=200)
async def root():
    """
    Корневой маршрут — перенаправление в Swagger UI.
    """
    return {"message": "Добро пожаловать в API! Перейдите на /docs для просмотра документации."}