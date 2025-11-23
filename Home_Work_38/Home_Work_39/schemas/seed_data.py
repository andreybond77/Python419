import asyncio
import sys
from pathlib import Path
import shutil
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import AsyncSessionLocal, engine
from models.product import ProductModel
from models.category import CategoryModel
from models.base import Base

# Данные для наполнения базы
CATEGORIES = [
    {"name": "Технологии", "description": "Высокотехнологичные устройства"},
    {"name": "Бытовые приборы", "description": "Для дома и быта"},
    {"name": "Топливо и энергия", "description": "Источники энергии"},
    {"name": "Развлечения", "description": "Игры и симуляторы"},
    {"name": "Продукты питания", "description": "Еда и напитки"},
    {"name": "Медицина", "description": "Лекарства и медтехника"},
    {"name": "Транспорт", "description": "Средства передвижения"},
    {"name": "Оружие", "description": "Боевые устройства"},
]

PRODUCTS = [
    {
        "name": "Стандартный Плюмбус",
        "description": "Каждый дом должен иметь плюмбус. Мы не знаем, что он делает, но он делает это очень хорошо. В комплекте: шлее, грумбо и флиб.",
        "price": 6.5,
        "stock": 10,
        "image_url": "/uploads/products/plumbus.webp",
        "category_name": "Бытовые приборы",
    },
    {
        "name": "Коробка с Мисиксами",
        "description": "Нужна помощь по дому? Нажмите кнопку, и появится Мисикс, готовый выполнить одно ваше поручение. Существование для него — боль, так что не затягивайте!",
        "price": 19.99,
        "stock": 5,
        "image_url": "/uploads/products/meeseeks-box.webp",
        "category_name": "Технологии",
    },
    {
        "name": "Портальная пушка (б/у)",
        "description": "Слегка поцарапана, заряд портальной жидкости на 37%. Возврату не подлежит. Может пахнуть приключениями и чужими измерениями. Осторожно: привлекает внимание Цитадели.",
        "price": 9999.99,
        "stock": 1,
        "image_url": "/uploads/products/portal-gun.webp",
        "category_name": "Транспорт",
    },
    {
        "name": "Концентрированная темная материя",
        "description": "Идеальное топливо для вашего космического корабля. Всего одна капля позволит вам улететь от любых экзистенциальных кризисов. Не употреблять внутрь!",
        "price": 850.0,
        "stock": 3,
        "image_url": "/uploads/products/dark-matter.webp",
        "category_name": "Топливо и энергия",
    },
    {
        "name": "Масло-робот 'Передай масло'",
        "description": "Его единственная цель существования — передавать масло. Он осознает это и впадает в депрессию. Отличный собеседник для завтрака в одиночестве.",
        "price": 25.5,
        "stock": 15,
        "image_url": "/uploads/products/butter-robot.webp",
        "category_name": "Бытовые приборы",
    },
    {
        "name": "Шлем для чтения мыслей собак",
        "description": "Теперь вы наконец-то узнаете, где ваш пёс спрятал тапки и почему он лает на пылесос. Спойлер: он считает вас хорошим мальчиком.",
        "price": 120.0,
        "stock": 8,
        "image_url": "/uploads/products/dog-helmet.webp",
        "category_name": "Технологии",
    },
    {
        "name": "Зерновые 'Глазастики'",
        "description": "Маленькие глазастые человечки, которые живут в коробке и умоляют вас съесть их. Сбалансированный завтрак с нотками отчаяния.",
        "price": 4.20,
        "stock": 50,
        "image_url": "/uploads/products/eyeholes.webp",
        "category_name": "Продукты питания",
    },
    {
        "name": "Микро-вселенная в коробке",
        "description": "Источник энергии для вашего автомобиля. Её жители поклоняются вам как богу, пока вы не заводите машину. Этично? Решать вам.",
        "price": 2500.0,
        "stock": 2,
        "image_url": "/uploads/products/microverse-battery.webp",
        "category_name": "Топливо и энергия",
    },
    {
        "name": "Нейтрализатор памяти",
        "description": "Видели что-то, что не следовало? Сотрите этот момент из своей памяти или памяти друзей. Побочный эффект: возможно, вы забудете, как завязывать шнурки.",
        "price": 350.75,
        "stock": 7,
        "image_url": "/uploads/products/memory-neutralizer.webp",
        "category_name": "Медицина",
    },
    {
        "name": "Семена из Мега-деревьев",
        "description": "Придают временный, но невероятный интеллект. Для провоза необходимо поместить в очень... укромное место. Таможня не одобрит.",
        "price": 55.0,
        "stock": 12,
        "image_url": "/uploads/products/mega-seeds.webp",
        "category_name": "Медицина",
    },
]

async def create_tables():
    """Создание таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def clear_tables(session: AsyncSession):
    """Очистка таблиц"""
    await session.execute(ProductModel.__table__.delete())
    await session.execute(CategoryModel.__table__.delete())
    await session.commit()

async def seed_categories(session: AsyncSession):
    """Заполнение категорий"""
    categories_map = {}
    for category_data in CATEGORIES:
        category = CategoryModel(
            name=category_data["name"],
            description=category_data["description"]
        )
        session.add(category)
        await session.flush()
        categories_map[category_data["name"]] = category.id
    await session.commit()
    return categories_map

async def seed_products(session: AsyncSession, categories_map: dict):
    """Заполнение продуктов"""
    for product_data in PRODUCTS:
        product = ProductModel(
            name=product_data["name"],
            description=product_data["description"],
            price=product_data["price"],
            stock=product_data["stock"],
            image_url=product_data["image_url"],
            category_id=categories_map[product_data["category_name"]]
        )
        session.add(product)
    await session.commit()

async def copy_sample_images():
    """Копирование примеров изображений (заглушки)"""
    uploads_dir = Path("uploads/products")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Создаем простые текстовые файлы как заглушки для изображений
    for product in PRODUCTS:
        filename = Path(product["image_url"]).name
        filepath = uploads_dir / filename
        with open(filepath, "w") as f:
            f.write(f"Sample image for {product['name']}")

async def main(clear: bool = False):
    """Основная функция"""
    print("🚀 Начало наполнения базы данных...")
    
    await create_tables()
    
    async with AsyncSessionLocal() as session:
        if clear:
            print("🧹 Очистка таблиц...")
            await clear_tables(session)
        
        print("📂 Создание категорий...")
        categories_map = await seed_categories(session)
        
        print("📦 Создание товаров...")
        await seed_products(session, categories_map)
        
        print("🖼️ Копирование примеров изображений...")
        await copy_sample_images()
    
    print("✅ Наполнение базы данных завершено!")
    print(f"📊 Создано: {len(CATEGORIES)} категорий, {len(PRODUCTS)} товаров")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Наполнение базы данных")
    parser.add_argument("--clear", action="store_true", help="Очистить таблицы перед наполнением")
    
    args = parser.parse_args()
    
    asyncio.run(main(clear=args.clear))