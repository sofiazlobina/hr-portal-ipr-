from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import Competency, PlanCompetency, User
from app.schemas.competency import CompetencyCreate, CompetencyUpdate, CompetencyResponse
from app.schemas.common import PaginatedResponse 
from app.utils.security import get_current_user
from app.services.plans import fail, save

router = APIRouter(prefix='/competencies', tags=['Competencies'])

# Белый список полей для сортировки
ALLOWED_SORT_FIELDS = {"id", "name"}


def require_hr(user):
    if user.role != 'hr':
        fail('Справочником компетенций управляет HR-специалист', 403)


def find(db, competency_id):
    row = db.get(Competency, competency_id)
    if row is None:
        fail('Компетенция не найдена', 404)
    return row


def unique_name(db, name, excluding=None):
    if db.query(Competency).filter(Competency.name == name, Competency.id != excluding).first():
        fail('Компетенция с таким названием уже существует')


@router.get(
    '/',
    response_model=PaginatedResponse[CompetencyResponse], 
    summary='Список компетенций с пагинацией, сортировкой и поиском',
    description='Возвращает пагинированный список компетенций с возможностью поиска по названию и описанию.'
)
def get_competencies(
    page: int = Query(1, ge=1, description="Номер страницы (начиная с 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Записей на странице (макс. 100)"),
    sort_by: str = Query("id", description="Поле сортировки"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Направление сортировки"),
    search: Optional[str] = Query(None, min_length=2, description="Поиск по названию и описанию"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Валидация поля сортировки
    if sort_by not in ALLOWED_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимое поле сортировки: {sort_by}. Разрешены: {ALLOWED_SORT_FIELDS}"
        )

    # 2. Базовый запрос
    query = db.query(Competency)

    # 3. Поиск ILIKE (регистр не важен)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Competency.name.ilike(search_pattern)) |
            (Competency.description.ilike(search_pattern))
        )

    # 4. Сортировка
    sort_column = getattr(Competency, sort_by)
    if sort_order == "desc":
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    # 5. Метаданные (считаем ПОСЛЕ фильтров и поиска!)
    total = query.count()
    total_pages = (total + per_page - 1) // per_page

    # 6. Пагинация
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }


@router.get('/{competency_id}', response_model=CompetencyResponse, summary='Компетенция по ID')
def get_competency(competency_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    return find(db, competency_id)


@router.post('/', response_model=CompetencyResponse, status_code=201, summary='Создать компетенцию (HR)')
def create_competency(competency: CompetencyCreate, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    require_hr(current_user)
    unique_name(db, competency.name)
    row = Competency(**competency.model_dump())
    db.add(row)
    save(db)
    return row


@router.put('/{competency_id}', response_model=CompetencyResponse, summary='Заменить компетенцию (HR)')
def update_competency(competency_id: int, competency: CompetencyCreate, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    require_hr(current_user)
    row = find(db, competency_id)
    unique_name(db, competency.name, competency_id)
    for key, value in competency.model_dump().items():
        setattr(row, key, value)
    save(db)
    return row


@router.patch('/{competency_id}', response_model=CompetencyResponse, summary='Изменить компетенцию (HR)')
def patch_competency(competency_id: int, competency: CompetencyUpdate, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    require_hr(current_user)
    row = find(db, competency_id)
    values = competency.model_dump(exclude_unset=True)
    if 'name' in values:
        unique_name(db, values['name'], competency_id)
    for key, value in values.items():
        setattr(row, key, value)
    save(db)
    return row


@router.delete('/{competency_id}', status_code=204, summary='Удалить неиспользуемую компетенцию (HR)')
def delete_competency(competency_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    require_hr(current_user)
    row = find(db, competency_id)
    if db.query(PlanCompetency).filter(PlanCompetency.competency_id == competency_id).first():
        fail('Компетенция используется в ИПР')
    db.delete(row)
    save(db)
    return Response(status_code=204)