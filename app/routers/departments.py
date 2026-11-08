from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.utils.security import get_current_user
from app.models.department import Department
from app.schemas.department import DepartmentResponse

router = APIRouter(prefix="/departments", tags=["departments"], dependencies=[Depends(get_current_user)])


@router.get(
    "/",
    response_model=List[DepartmentResponse],
    summary="Получить список отделов",
    description="Возвращает список всех отделов. Согласно ТЗ, создание и изменение отделов выполняется через начальные данные БД."
)
def get_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    departments = (
        db.query(Department)
        .order_by(Department.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return departments


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
    department = (
        db.query(Department)
        .filter(Department.id == department_id)
        .first()
    )
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Отдел с id={department_id} не найден"
        )
    return department