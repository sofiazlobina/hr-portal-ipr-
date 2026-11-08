"""Кастомные бизнес-исключения"""


class BaseAppException(Exception):
    """Базовое исключение приложения."""
    error_code: str = "APP_ERROR"
    
    def __init__(self, detail: str, field: str = None):
        self.detail = detail
        self.field = field
        super().__init__(detail)


class NotFoundError(BaseAppException):
    """Сущность не найдена (404)."""
    error_code = "NOT_FOUND"
    
    def __init__(self, entity: str, id: int = None):
        if id is not None:
            detail = f"{entity} с id={id} не найден"
        else:
            detail = f"{entity} не найден"
        super().__init__(detail=detail)


class ConflictError(BaseAppException):
    """Конфликт данных — дубликат, нарушение уникальности (409)."""
    error_code = "CONFLICT"
    
    def __init__(self, detail: str, field: str = None):
        super().__init__(detail=detail, field=field)


class ForbiddenError(BaseAppException):
    """Доступ запрещён (403)."""
    error_code = "FORBIDDEN"
    
    def __init__(self, detail: str):
        super().__init__(detail=detail)


class BusinessLogicError(BaseAppException):
    """Нарушение бизнес-правил (400)."""
    error_code = "BUSINESS_LOGIC_ERROR"
    
    def __init__(self, detail: str):
        super().__init__(detail=detail)


class ValidationError(BaseAppException):
    """Ошибка валидации входных данных (400)."""
    error_code = "VALIDATION_ERROR"
    
    def __init__(self, detail: str, field: str = None):
        super().__init__(detail=detail, field=field)