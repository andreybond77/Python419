from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
import logging
from core.database import get_db
from models.product import ProductModel
from models.category import CategoryModel
from schemas.product import ProductCreate, ProductResponse
from core.storage import save_product_image, delete_product_image

# Настройка логирования
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

async def product_get_by_id(session: AsyncSession, product_id: int) -> ProductModel:
    """
    Вспомогательная функция для получения товара по ID
    """
    result = await session.execute(
        select(ProductModel).where(ProductModel.id == product_id)
    )
    product = result.scalar_one_or_none()
    return product

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

    # Удаляем связанное изображение, если есть
    if db_product.image_url:
        delete_product_image(db_product.image_url)

    await db.delete(db_product)
    await db.commit()
    return {"message": "Product deleted successfully"}

@router.post("/{product_id}/upload-image", summary="Загрузить изображение для товара")
async def upload_product_image(
    product_id: int,
    file: UploadFile,
    db: AsyncSession = Depends(get_db)
):
    """
    Загружает изображение для товара и привязывает его. 
    Если старое изображение было — оно удаляется.
    """
    logger.info(f"📥 Запрос на загрузку изображения для товара ID={product_id}")
    
    # Проверяем существование товара
    product = await product_get_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Удаляем старое изображение, если оно есть
    if product.image_url:
        logger.info(f"🗑️ Удаление старого изображения: {product.image_url}")
        delete_product_image(product.image_url)
    
    # Сохраняем новое изображение
    try:
        image_url = await save_product_image(file)
    except HTTPException as e:
        logger.error(f"❌ Ошибка загрузки изображения: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        raise HTTPException(status_code=500, detail="Ошибка загрузки изображения")
    
    # Обновляем URL в базе данных
    try:
        await db.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(image_url=image_url)
        )
        await db.commit()
        logger.info(f"✅ Изображение привязано к товару ID={product_id}: {image_url}")
    except Exception as e:
        logger.error(f"❌ Ошибка обновления БД: {e}")
        # Пытаемся удалить загруженный файл, если обновление БД не удалось
        delete_product_image(image_url)
        raise HTTPException(status_code=500, detail="Ошибка обновления базы данных")
    
    return {"product_id": product_id, "image_url": image_url}

@router.delete("/{product_id}/image", summary="Удалить изображение товара")
async def delete_product_image_endpoint(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Удаляет изображение товара (с диска и из БД).
    """
    logger.info(f"🗑️ Запрос на удаление изображения для товара ID={product_id}")
    
    # Получаем товар
    product = await product_get_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Проверяем наличие изображения
    if not product.image_url:
        raise HTTPException(status_code=400, detail="У товара нет изображения")
    
    # Удаляем файл с диска
    delete_success = delete_product_image(product.image_url)
    
    # Обновляем БД
    try:
        await db.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(image_url=None)
        )
        await db.commit()
        logger.info(f"✅ Изображение удалено из БД для товара ID={product_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка обновления БД: {e}")
        raise HTTPException(status_code=500, detail="Ошибка обновления базы данных")
    
    return {"message": "Изображение удалено", "product_id": product_id}
