#routes/products.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select

# from core.database import AsyncSessionLocal
# from models.product import ProductModel  # ← используем ProductModel
# from models.category import CategoryModel  # ← используем CategoryModel
# from schemas.product import ProductCreate, ProductResponse




# # Создаем экземпляр APIRouter с префиксом и тегами
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
#     Возвращает список всех продуктов из базы данных.
#     Поддерживает фильтрацию по тексту и сортировку по цене.
#     """
#     async with AsyncSessionLocal() as session:
#         # Начинаем с базового запроса на выборку всех продуктов с загрузкой категории
#         query = select(ProductModel).options(selectinload(ProductModel.category))

#         # Фильтрация поиска
#         if search:
#             query = query.where(
#                 or_(
#                     ProductModel.name.ilike(f"%{search}%"),
#                     ProductModel.description.ilike(f"%{search}%")
#                 )
#             )

#         # Сортировка
#         if currency and sort_order:
#             # Проверяем, что валюта существует в модели (проверка на уровне БД)
#             # SQLAlchemy сам проверит, существует ли поле, если использовать getattr
#             try:
#                 price_column = getattr(ProductModel, f"price_{currency}")
#                 if sort_order.lower() == "desc":
#                     query = query.order_by(price_column.desc())
#                 else:
#                     query = query.order_by(price_column.asc())
#             except AttributeError:
#                 # Если валюта не найдена в модели (например, price_undefined)
#                 raise HTTPException(status_code=400, detail=f"Неподдерживаемая валюта для сортировки: {currency}")

#         # Выполняем запрос
#         result = await session.execute(query)
#         products = result.scalars().all()

#         # Преобразуем ORM-объекты в Pydantic-модели для возврата
#         return [Product.model_validate(p) for p in products]


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
#     Возвращает один продукт по его ID из базы данных.
#     """
#     async with AsyncSessionLocal() as session:
#         # Получаем продукт по ID с загрузкой категории
#         product = await session.execute(
#             select(ProductModel)
#             .options(selectinload(ProductModel.category))
#             .where(ProductModel.id == product_id)
#         )
#         product = product.scalar_one_or_none()
#         if product is None:
#             raise HTTPException(status_code=404, detail="Продукт не найден")
#         # Преобразуем ORM-объект в Pydantic-модель для возврата
#         return Product.model_validate(product)


# # --- CREATE ---
# @router.post(
#     path="/",
#     response_model=Product,
#     status_code=201,
#     summary="Создать новый продукт",
# )
# async def create_product(
#     product_data: ProductCreate,
#     background_tasks: BackgroundTasks
# ):
#     """
#     Создаёт новый продукт и добавляет его в базу данных.
#     Также добавляет фоновую задачу для отправки уведомления в Telegram.
#     """
#     async with AsyncSessionLocal() as session:
#         # Проверяем, существует ли категория с переданным category_id
#         category = await session.get(CategoryModel, product_data.category_id)
#         if category is None:
#             raise HTTPException(status_code=404, detail="Категория не найдена")
        
#         # Создаем ORM-объект из Pydantic-схемы
#         new_product = ProductModel(**product_data.model_dump())
#         session.add(new_product)
#         await session.commit()  # Сохраняем изменения
#         await session.refresh(new_product)  # Обновляем объект, чтобы получить ID от БД

#         # Формируем сообщение для Telegram
#         message = f"""🆕 *Создан новый продукт*

# 📦 *Название:* {new_product.name}
# 🆔 *ID:* {new_product.id}
# 📝 *Описание:* {new_product.description[:150]}...
# 🏷️ *Категория:* {new_product.category.name}

# 💰 *Цены:*
#   • Шмекели: {new_product.price_shmeckles}
#   • Флурбо: {new_product.price_flurbos}
#   • Кредиты: {new_product.price_credits}
# """
#         # Добавляем фоновую задачу для отправки уведомления
#         background_tasks.add_task(send_telegram_message, message)

#         # Преобразуем ORM-объект в Pydantic-модель для возврата
#         # Загружаем категорию для полного ответа
#         full_product = await session.execute(
#             select(ProductModel)
#             .options(selectinload(ProductModel.category))
#             .where(ProductModel.id == new_product.id)
#         )
#         full_product = full_product.scalar_one()
#         return Product.model_validate(full_product)


# # --- UPDATE ---
# @router.put(
#     path="/{product_id}",
#     response_model=Product,
#     status_code=200,
#     summary="Обновить продукт",
# )
# async def update_product(
#     background_tasks: BackgroundTasks,
#     product_id: int = Path(..., ge=1, description="ID продукта"),
#     product_data: ProductCreate = None
# ):
#     """
#     Обновляет существующий продукт по ID в базе данных.
#     Также добавляет фоновую задачу для отправки уведомления в Telegram.
#     """
#     async with AsyncSessionLocal() as session:
#         # Получаем продукт по ID
#         product = await session.get(ProductModel, product_id)
#         if product is None:
#             raise HTTPException(status_code=404, detail="Продукт не найден")

#         # Проверяем, существует ли категория с переданным category_id
#         category = await session.get(CategoryModel, product_data.category_id)
#         if category is None:
#             raise HTTPException(status_code=404, detail="Категория не найдена")

#         # Обновляем поля продукта данными из схемы
#         for field, value in product_data.model_dump().items():
#             setattr(product, field, value)

#         await session.commit()  # Сохраняем изменения
#         await session.refresh(product)  # Обновляем объект

#         # Формируем сообщение для Telegram
#         message = f"""🔄 *Обновлён продукт*

# 📦 *Название:* {product.name}
# 🆔 *ID:* {product.id}
# 📝 *Описание:* {product.description[:150]}...
# 🏷️ *Категория:* {product.category.name}

# 💰 *Цены:*
#   • Шмекели: {product.price_shmeckles}
#   • Флурбо: {product.price_flurbos}
#   • Кредиты: {product.price_credits}
# """
#         # Добавляем фоновую задачу для отправки уведомления
#         background_tasks.add_task(send_telegram_message, message)

#         # Загружаем продукт с категорией для полного ответа
#         full_product = await session.execute(
#             select(ProductModel)
#             .options(selectinload(ProductModel.category))
#             .where(ProductModel.id == product.id)
#         )
#         full_product = full_product.scalar_one()
#         # Преобразуем ORM-объект в Pydantic-модель для возврата
#         return Product.model_validate(full_product)


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
#     Удаляет продукт по ID из базы данных.
#     """
#     async with AsyncSessionLocal() as session:
#         # Получаем продукт по ID
#         product = await session.get(ProductModel, product_id)
#         if product is None:
#             raise HTTPException(status_code=404, detail="Продукт не найден")

#         await session.delete(product)  # Удаляем объект
#         await session.commit()  # Сохраняем изменения

#         # Возвращаем 204 No Content
#         return  # FastAPI автоматически установит статус 204, если функция возвращает None

###########################################################

# routes/products.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models.product import ProductModel
from models.category import CategoryModel
from schemas.product import ProductCreate, ProductResponse

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate, 
    db: AsyncSession = Depends(get_db)
):
    # Проверяем, существует ли категория
    result = await db.execute(
        select(CategoryModel).where(CategoryModel.id == product.category_id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    db_product = ProductModel(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category_id=product.category_id
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: int, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ProductModel).where(ProductModel.id == product_id)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/", response_model=list[ProductResponse])
async def read_products(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ProductModel).offset(skip).limit(limit)
    )
    products = result.scalars().all()
    return products

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int, 
    product: ProductCreate, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ProductModel).where(ProductModel.id == product_id)
    )
    db_product = result.scalar_one_or_none()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Проверяем категорию
    result = await db.execute(
        select(CategoryModel).where(CategoryModel.id == product.category_id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    # Обновляем поля
    db_product.name = product.name
    db_product.description = product.description
    db_product.price = product.price
    db_product.stock = product.stock
    db_product.category_id = product.category_id

    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ProductModel).where(ProductModel.id == product_id)
    )
    db_product = result.scalar_one_or_none()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(db_product)
    await db.commit()
    return {"message": "Product deleted successfully"}
