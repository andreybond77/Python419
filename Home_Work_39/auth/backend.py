from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from core.config import settings

# Секретный ключ для подписи JWT токенов
SECRET = settings.secret_key

# Транспорт Bearer для передачи токена в заголовке Authorization
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    """
    Создает и возвращает стратегию JWT для аутентификации.
    
    Returns:
        JWTStrategy: Стратегия с указанным секретным ключом и временем жизни токена
    """
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)  # Токен живет 1 час

# Бэкенд аутентификации, объединяющий транспорт и стратегию
auth_backend = AuthenticationBackend(
    name="jwt",  # Имя бэкенда
    transport=bearer_transport,  # Транспорт для передачи токена
    get_strategy=get_jwt_strategy,  # Функция для получения стратегии
)