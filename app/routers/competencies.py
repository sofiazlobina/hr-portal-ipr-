from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Competency, PlanCompetency, User
from app.schemas.competency import CompetencyCreate, CompetencyUpdate, CompetencyResponse
from app.utils.security import get_current_user
from app.services.plans import fail, save

router = APIRouter(prefix='/competencies', tags=['Competencies'])


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


@router.get('/', response_model=list[CompetencyResponse], summary='Список компетенций')
def get_competencies(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100),
                     db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Competency).order_by(Competency.id).offset(skip).limit(limit).all()


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
