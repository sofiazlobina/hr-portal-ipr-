from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.utils.security import get_current_user
from app.models.department import Department
from app.schemas.department import DepartmentResponse
from app.schemas.common import PaginatedResponse

router = APIRouter(
    prefix="/departments",
    tags=["departments"],
    dependencies=[Depends(get_current_user)]
)

# Белый список полей для сортировки (защита от инъекций)
ALLOWED_SORT_FIELDS = {"id", "name"}


@router.get(
    "/",
    response_model=PaginatedResponse[DepartmentResponse],
    summary="Получить список отделов с пагинацией и сортировкой",
    description="Возвращает пагинированный список отделов. "
                "Создание и изменение отделов выполняется через начальные данные БД."
)
def get_departments(
    page: int = Query(1, ge=1, description="Номер страницы (начиная с 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Записей на странице (макс. 100)"),
    sort_by: str = Query("id", description="Поле сортировки"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Направление сортировки"),
    db: Session = Depends(get_db)
):
    # Валидация поля сортировки (белый список)
    if sort_by not in ALLOWED_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимое поле сортировки: {sort_by}. Разрешены: {ALLOWED_SORT_FIELDS}"
        )

    # Базовый запрос
    query = db.query(Department)

    # Сортировка
    sort_column = getattr(Department, sort_by)
    if sort_order == "desc":
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    # Метаданные (считаем ПОСЛЕ фильтров, но ДО пагинации)
    total = query.count()
    total_pages = (total + per_page - 1) // per_page

    # Пагинация
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
    summary="Получить отдел по ID",
    description="Возвращает отдел по его идентификатору."
)
def get_department(
    department_id: int,
    db: Session = Depends(get_db)
):
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(
            status_code=404,
            detail=f"Отдел с id={department_id} не найден"
        )
    return department