from typing import Any, ClassVar, Dict, Tuple
from fastapi_users import schemas
from pydantic import ConfigDict, model_validator

class UserRead(schemas.BaseUser[int]):
    """
    Схема для чтения данных пользователя (без пароля).
    
    Attributes:
        id: ID пользователя
        email: Email пользователя
        is_active: Активен ли пользователь
        is_superuser: Является ли суперпользователем
        is_verified: Подтвержден ли email
    """
    pass

class UserCreate(schemas.BaseUserCreate):
    """
    Схема для регистрации нового пользователя без критичных флагов.
    
    Защищает от установки клиентом флагов is_active, is_superuser, is_verified.
    Эти флаги могут устанавливаться только на сервере.
    
    Attributes:
        email: Email пользователя
        password: Пароль пользователя
    """
    
    model_config = ConfigDict(extra="forbid")  # Запрещает дополнительные поля
    
    # Критичные флаги, которые нельзя передавать при регистрации
    _admin_flags: ClassVar[Tuple[str, ...]] = ("is_active", "is_superuser", "is_verified")

    @model_validator(mode="before")
    @classmethod
    def _reject_admin_flags(cls, data: Any) -> Any:
        """
        Валидатор, который запрещает передачу критичных флагов при регистрации.
        
        Args:
            data: Входные данные для валидации
            
        Returns:
            Any: Валидированные данные
            
        Raises:
            ValueError: Если обнаружены критические флаги
        """
        if isinstance(data, dict):
            invalid_fields = []
            for field in cls._admin_flags:
                if field in data:
                    invalid_fields.append(field)
            
            if invalid_fields:
                raise ValueError(
                    f"Недопустимые поля в регистрации: {', '.join(invalid_fields)}. "
                    "Управляющие флаги задаются только на сервере."
                )
        return data

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        """
        Удаляет критические поля из JSON схемы OpenAPI.
        
        Args:
            core_schema: Базовая схема
            handler: Обработчик схем
            
        Returns:
            dict: Модифицированная JSON схема
        """
        json_schema = super().__get_pydantic_json_schema__(core_schema, handler)
        if "properties" in json_schema:
            # Удаляем критические поля из свойств схемы
            for field in cls._admin_flags:
                json_schema["properties"].pop(field, None)
        
        if "required" in json_schema:
            # Удаляем критические поля из списка обязательных полей
            for field in cls._admin_flags:
                if field in json_schema["required"]:
                    json_schema["required"].remove(field)
        
        return json_schema

class UserUpdate(schemas.BaseUserUpdate):
    """
    Схема для обновления данных пользователя.
    
    Attributes:
        password: Новый пароль (опционально)
        email: Новый email (опционально)
    """
    pass