# scripts/seed_db.py

import sys
import os
import asyncio

# --- Добавляем корень проекта в путь поиска модулей ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# -----------------------------------------------------

# Импорты после изменения sys.path
from core.database import AsyncSessionLocal, init_db
from models.product import Product as ProductModel  # Импортируем ORM-модель
from models.category import Category as CategoryModel  # Импортируем ORM-модель категории


async def seed_database():
    """
    Заполнение базы данных тестовыми категориями и продуктами
    """
    # Инициализируем БД (создаем таблицы)
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Создаем тестовые категории
        categories_data = [
            {"name": "Техника"},
            {"name": "Еда"},
            {"name": "Игрушки"},
            {"name": "Одежда"},
            {"name": "Космические приборы"}
        ]
        
        categories = []
        for cat_data in categories_data:
            category = CategoryModel(**cat_data)
            session.add(category)
            categories.append(category)
        
        await session.commit()
        
        # Обновляем объекты категорий, чтобы получить их ID
        for category in categories:
            await session.refresh(category)
    
    # Теперь создаем тестовые продукты с привязкой к категориям
    products_data = [
        {
            "name": "Стандартный Плюмбус",
            "description": "Каждый дом должен иметь плюмбус. Мы не знаем, что он делает, но он делает это очень хорошо.",
            "image_url": "/images/plumbus.webp",
            "price_shmeckles": 6.5,
            "price_credits": 4.8,
            "price_flurbos": 3.2,
            "category_id": 5,  # Космические приборы
        },
        {
            "name": "Коробка с Мисиксами",
            "description": "Нужна помощь по дому? Нажмите кнопку, и появится Мисикс, готовый выполнить одно ваше поручение.",
            "image_url": "/images/meeseeks-box.webp",
            "price_shmeckles": 19.99,
            "price_credits": 14.5,
            "price_flurbos": 9.8,
            "category_id": 5,  # Космические приборы
        },
        {
            "name": "Портальная пушка (б/у)",
            "description": "Слегка поцарапана, заряд портальной жидкости на 37%. Возврату не подлежит.",
            "image_url": "/images/portal-gun.webp",
            "price_shmeckles": 9999.99,
            "price_credits": 7500.0,
            "price_flurbos": 4999.99,
            "category_id": 1,  # Техника
        },
        {
            "name": "Концентрированная темная материя",
            "description": "Идеальное топливо для вашего космического корабля. Всего одна капля позволит вам улететь от любых экзистенциальных кризисов.",
            "image_url": "/images/dark-matter.webp",
            "price_shmeckles": 850.0,
            "price_credits": 620.0,
            "price_flurbos": 415.0,
            "category_id": 1,  # Техника
        },
        {
            "name": "Масло-робот 'Передай масло'",
            "description": "Его единственная цель существования — передавать масло. Он осознает это и впадает в депрессию.",
            "image_url": "/images/butter-robot.webp",
            "price_shmeckles": 25.5,
            "price_credits": 18.2,
            "price_flurbos": 12.5,
            "category_id": 3,  # Игрушки
        },
        {
            "name": "Шлем для чтения мыслей собак",
            "description": "Теперь вы наконец-то узнаете, где ваш пёс спрятал тапки и почему он лает на пылесос.",
            "image_url": "/images/dog-helmet.webp",
            "price_shmeckles": 120.0,
            "price_credits": 88.0,
            "price_flurbos": 59.0,
            "category_id": 1,  # Техника
        },
        {
            "name": "Зерновые 'Глазастики'",
            "description": "Маленькие глазастые человечки, которые живут в коробке и умоляют вас съесть их.",
            "image_url": "/images/eyeholes.webp",
            "price_shmeckles": 4.20,
            "price_credits": 3.1,
            "price_flurbos": 2.05,
            "category_id": 2,  # Еда
        },
    ]
    
    async with AsyncSessionLocal() as session:
        for product_data in products_data:
            product = ProductModel(**product_data)
            session.add(product)
        
        await session.commit()
        print(f"Добавлено {len(products_data)} продуктов в базу данных")
        print(f"Добавлено {len(categories_data)} категорий в базу данных")


if __name__ == "__main__":
    asyncio.run(seed_database())