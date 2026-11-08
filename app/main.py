from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from app.routers import auth, competencies, departments, development_plans
from app.exceptions.custom_exceptions import BaseAppException
from app.exceptions.handlers import (
    base_app_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    http_exception_handler, 
)

app = FastAPI(
    title='HR-портал: Модуль ИПР',
    description='ИПР, согласование руководителем и справочник компетенций. В Authorize введите email в поле username.',
    version='1.1.0',
)

# Регистрируем глобальные обработчики исключений
app.add_exception_handler(BaseAppException, base_app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler) 

app.include_router(auth.router)
app.include_router(departments.router)
app.include_router(competencies.router)
app.include_router(development_plans.router)


@app.get('/')
def root():
    return {'message': 'HR Portal API'}


@app.get('/health')
def health_check():
    return {'status': 'ok'}