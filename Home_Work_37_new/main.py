# main.py
from fastapi import FastAPI
from core.config import settings
from routes import categories, products

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description=settings.app_description
)

# Подключаем роутеры
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(categories.router, prefix="/api/v1", tags=["categories"])

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в FastAPI Shop!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)