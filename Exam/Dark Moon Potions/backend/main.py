# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Добавляем текущую директорию в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

app = FastAPI(
    title="Dark Moon Potions API",
    description="API для магазина зелий Dark Moon Potions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Сначала импортируем модели чтобы избежать циклических зависимостей
try:
    # Импортируем модели
    from models import User, Cart, Order, Potion, Review, Wishlist, Payment
    
    print("✅ Модели успешно импортированы")
except Exception as e:
    print(f"⚠️  Ошибка импорта моделей: {e}")

# Затем импортируем роутеры
try:
    from routers.auth import router as auth_router
    from routers.users import router as users_router
    from routers.potions import router as potions_router
    from routers.categories import router as categories_router
    from routers.cart import router as cart_router
    from routers.orders import router as orders_router
    from routers.reviews import router as reviews_router
    from routers.wishlist import router as wishlist_router
    from routers.payments import router as payments_router
    from routers.admin import router as admin_router
    
    # Подключаем роутеры с префиксом /api
    app.include_router(auth_router, prefix="/api")
    app.include_router(users_router, prefix="/api")
    app.include_router(potions_router, prefix="/api")
    app.include_router(categories_router, prefix="/api")
    app.include_router(cart_router, prefix="/api")
    app.include_router(orders_router, prefix="/api")
    app.include_router(reviews_router, prefix="/api")
    app.include_router(wishlist_router, prefix="/api")
    app.include_router(payments_router, prefix="/api")
    app.include_router(admin_router, prefix="/api")
    
    print("✅ Все роутеры успешно подключены с префиксом /api")
    
except ImportError as e:
    print(f"❌ Ошибка импорта роутеров: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"⚠️  Ошибка подключения роутеров: {e}")
    import traceback
    traceback.print_exc()

@app.get("/")
async def root():
    return {
        "message": "Welcome to Dark Moon Potions API",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Dark Moon Potions API"}

@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "service": "Dark Moon Potions API"}

# Отладочный эндпоинт для проверки маршрутов
@app.get("/debug/routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods) if hasattr(route, 'methods') else []
        })
    return routes

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("🚀 Dark Moon Potions API запускается...")
    print("="*50)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  # Изменено с 8000 на 8001
        reload=True
    )