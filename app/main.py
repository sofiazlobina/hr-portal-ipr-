from fastapi import FastAPI
from app.routers import auth, competencies, departments, development_plans

app = FastAPI(
    title='HR-портал: Модуль ИПР',
    description='ИПР, согласование руководителем и справочник компетенций. В Authorize введите email в поле username.',
    version='1.1.0',
)
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
