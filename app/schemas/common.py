from pydantic import BaseModel
from typing import List, Any, Optional, Generic, TypeVar

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Единая схема пагинированного ответа."""
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int


class ErrorResponse(BaseModel):
    """Единая схема ошибки"""
    detail: str
    error_code: str
    field: Optional[str] = None