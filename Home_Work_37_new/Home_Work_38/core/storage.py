import logging
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException

# Настройка логирования
logger = logging.getLogger(__name__)

# Константы
UPLOAD_DIR = Path("uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ

async def save_product_image(file: UploadFile) -> str:
    """
    Сохраняет изображение товара с валидацией и возвращает URL-путь
    """
    logger.info(f"📥 Начало загрузки файла: {file.filename}")
    
    # Проверка расширения файла
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        logger.error(f"❌ Неподдерживаемый формат файла: {ext}")
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Чтение и проверка размера файла
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        logger.error(f"❌ Файл слишком большой: {len(content)} байт")
        raise HTTPException(
            status_code=400,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024*1024)} МБ"
        )
    
    # Генерация уникального имени файла
    filename = f"{uuid.uuid4()}{ext}"
    filepath = UPLOAD_DIR / filename
    
    # Сохранение файла
    try:
        with open(filepath, "wb") as f:
            f.write(content)
        logger.info(f"✅ Файл сохранён: {filepath}")
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения файла: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка при сохранении файла"
        )
    
    # Возвращаем URL-путь
    return f"/uploads/products/{filename}"

def delete_product_image(image_url: str) -> bool:
    """
    Удаляет файл изображения товара
    """
    try:
        filename = Path(image_url).name
        filepath = UPLOAD_DIR / filename
        
        if filepath.exists():
            filepath.unlink()
            logger.info(f"✅ Файл удалён: {filepath}")
            return True
        else:
            logger.warning(f"⚠️ Файл не найден: {filepath}")
            return False
    except Exception as e:
        logger.error(f"❌ Ошибка удаления файла: {e}")
        return False