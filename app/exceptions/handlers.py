"""Глобальные обработчики исключений"""
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.exceptions.custom_exceptions import BaseAppException
from fastapi import HTTPException

async def base_app_exception_handler(request: Request, exc: BaseAppException):
    """Обработчик кастомных исключений приложения."""
    status_code = 400
    if exc.error_code == "NOT_FOUND":
        status_code = 404
    elif exc.error_code == "FORBIDDEN":
        status_code = 403
    elif exc.error_code == "CONFLICT":
        status_code = 409
    
    response = {
        "detail": exc.detail,
        "error_code": exc.error_code
    }
    
    if exc.field:
        response["field"] = exc.field
    
    return JSONResponse(status_code=status_code, content=response)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации Pydantic (422)."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Ошибка валидации входных данных",
            "error_code": "VALIDATION_ERROR",
            "errors": exc.errors()
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Обработчик непредвиденных ошибок (500)."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Внутренняя ошибка сервера",
            "error_code": "INTERNAL_ERROR"
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик стандартных HTTPException от FastAPI (401, 403, 404 и т.д.)."""
    error_code = "HTTP_ERROR"
    if exc.status_code == 401:
        error_code = "UNAUTHORIZED"
    elif exc.status_code == 403:
        error_code = "FORBIDDEN"
    elif exc.status_code == 404:
        error_code = "NOT_FOUND"
    elif exc.status_code == 409:
        error_code = "CONFLICT"
    elif exc.status_code == 422:
        error_code = "VALIDATION_ERROR"
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": error_code
        }
    )