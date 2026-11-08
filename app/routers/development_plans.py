from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Activity, Competency, DevelopmentPlan, Goal, PlanCompetency, User
from app.schemas.development_plan import (
    ActivityCompleteRequest, ActivityCreate, ActivityResponse, ActivityUpdate,
    DevelopmentPlanCreate, DevelopmentPlanReplace, DevelopmentPlanResponse, DevelopmentPlanUpdate,
    GoalCreate, GoalUpdate, GoalWithActivities, PlanApproveRequest, PlanRejectRequest,
    PlanCompetencyCreate, PlanCompetencyUpdate, PlanCompetencyResponse, PlanStatus,
)
from app.services import plans as service
from app.utils.security import get_current_user

router = APIRouter(prefix='/development-plans', tags=['Development Plans'])


@router.get('/', response_model=list[DevelopmentPlanResponse], summary='Свои ИПР и ИПР прямых подчинённых')
def get_plans(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100),
              status_filter: PlanStatus | None = None, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    query = db.query(DevelopmentPlan).filter(
        DevelopmentPlan.employee_id.in_(service.visible_employee_ids(db, current_user)))
    if status_filter:
        query = query.filter(DevelopmentPlan.status == status_filter)
    return service.loaded(query).order_by(DevelopmentPlan.id).offset(skip).limit(limit).all()


# Статический путь должен быть зарегистрирован до /{plan_id}.
@router.get('/pending-count', summary='Количество ИПР на согласование')
def get_pending_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != 'manager':
        return {'count': 0}
    ids = service.visible_employee_ids(db, current_user)
    ids.remove(current_user.id)
    return {'count': db.query(DevelopmentPlan).filter(
        DevelopmentPlan.employee_id.in_(ids), DevelopmentPlan.status == 'pending').count()}


@router.get('/{plan_id}', response_model=DevelopmentPlanResponse, summary='Открыть ИПР с содержимым и прогрессом')
def get_plan(plan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_plan(db, plan_id, current_user)


@router.post('/', response_model=DevelopmentPlanResponse, status_code=201, summary='Создать свой черновик ИПР')
def create_plan(plan: DevelopmentPlanCreate, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    if plan.employee_id != current_user.id:
        service.fail('Можно создать ИПР только для себя', 403)
    row = DevelopmentPlan(**plan.model_dump(), status='draft')
    db.add(row)
    service.save(db)
    return row


@router.patch('/{plan_id}', response_model=DevelopmentPlanResponse, summary='Изменить период своего черновика')
def update_plan(plan_id: int, plan_update: DevelopmentPlanUpdate, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    plan = service.draft(db, plan_id, current_user)
    for key, value in plan_update.model_dump(exclude_unset=True).items():
        setattr(plan, key, value)
    service.validate_dates(plan)
    service.save(db, plan)
    return plan


@router.put('/{plan_id}', response_model=DevelopmentPlanResponse, summary='Заменить период своего черновика')
def replace_plan(plan_id: int, plan_update: DevelopmentPlanReplace, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    return update_plan(plan_id, DevelopmentPlanUpdate(**plan_update.model_dump()), db, current_user)


@router.delete('/{plan_id}', status_code=204, summary='Удалить свой черновик вместе с содержимым')
def delete_plan(plan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = service.draft(db, plan_id, current_user)
    db.delete(plan)
    service.save(db)
    return Response(status_code=204)


@router.get('/{plan_id}/goals', response_model=list[GoalWithActivities], summary='Список целей ИПР')
def get_goals(plan_id: int, skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100),
               db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = service.get_plan(db, plan_id, current_user)
    return sorted(plan.goals, key=lambda row: row.id)[skip:skip + limit]


@router.get('/{plan_id}/goals/{goal_id}', response_model=GoalWithActivities, summary='Открыть цель')
def get_goal(plan_id: int, goal_id: int, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    return service.get_goal(service.get_plan(db, plan_id, current_user), goal_id)


@router.post('/{plan_id}/goals', response_model=GoalWithActivities, status_code=201, summary='Добавить цель')
def add_goal(plan_id: int, goal: GoalCreate, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    plan = service.draft(db, plan_id, current_user)
    if not plan.start_date <= goal.deadline <= plan.end_date:
        service.fail('Срок цели должен находиться в периоде ИПР')
    row = Goal(plan_id=plan_id, **goal.model_dump())
    db.add(row)
    service.save(db, plan)
    return row


@router.patch('/{plan_id}/goals/{goal_id}', response_model=GoalWithActivities, summary='Изменить цель')
def update_goal(plan_id: int, goal_id: int, goal_update: GoalUpdate, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    plan = service.draft(db, plan_id, current_user)
    goal = service.get_goal(plan, goal_id)
    for key, value in goal_update.model_dump(exclude_unset=True).items():
        setattr(goal, key, value)
    service.validate_dates(plan)
    service.save(db, plan)
    return goal


@router.put('/{plan_id}/goals/{goal_id}', response_model=GoalWithActivities, summary='Заменить цель')
def replace_goal(plan_id: int, goal_id: int, goal: GoalCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    return update_goal(plan_id, goal_id, GoalUpdate(**goal.model_dump()), db, current_user)


@router.delete('/{plan_id}/goals/{goal_id}', status_code=204, summary='Удалить цель с мероприятиями')
def delete_goal(plan_id: int, goal_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    plan = service.draft(db, plan_id, current_user)
    db.delete(service.get_goal(plan, goal_id))
    service.save(db, plan)
    return Response(status_code=204)


@router.get('/{plan_id}/goals/{goal_id}/activities', response_model=list[ActivityResponse], summary='Список мероприятий')
def get_activities(plan_id: int, goal_id: int, skip: int = Query(0, ge=0),
                    limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    goal = service.get_goal(service.get_plan(db, plan_id, current_user), goal_id)
    return sorted(goal.activities, key=lambda row: row.id)[skip:skip + limit]


@router.get('/{plan_id}/goals/{goal_id}/activities/{activity_id}', response_model=ActivityResponse, summary='Открыть мероприятие')
def get_activity(plan_id: int, goal_id: int, activity_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    goal = service.get_goal(service.get_plan(db, plan_id, current_user), goal_id)
    return service.get_activity(goal, activity_id)


@router.post('/{plan_id}/goals/{goal_id}/activities', response_model=ActivityResponse, status_code=201, summary='Добавить мероприятие')
def add_activity(plan_id: int, goal_id: int, activity: ActivityCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    plan = service.draft(db, plan_id, current_user)
    goal = service.get_goal(plan, goal_id)
    if not plan.start_date <= activity.deadline <= goal.deadline:
        service.fail('Срок мероприятия должен быть между началом ИПР и сроком цели')
    row = Activity(goal_id=goal.id, **activity.model_dump(), status='planned')
    db.add(row)
    service.save(db, plan)
    return row


@router.patch('/{plan_id}/goals/{goal_id}/activities/{activity_id}', response_model=ActivityResponse, summary='Изменить мероприятие')
def update_activity(plan_id: int, goal_id: int, activity_id: int, activity_update: ActivityUpdate,
                      db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = service.draft(db, plan_id, current_user)
    goal = service.get_goal(plan, goal_id)
    row = service.get_activity(goal, activity_id)
    for key, value in activity_update.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    service.validate_dates(plan)
    service.save(db, plan)
    return row


@router.put('/{plan_id}/goals/{goal_id}/activities/{activity_id}', response_model=ActivityResponse, summary='Заменить мероприятие')
def replace_activity(plan_id: int, goal_id: int, activity_id: int, activity: ActivityCreate,
                       db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_activity(plan_id, goal_id, activity_id, ActivityUpdate(**activity.model_dump()), db, current_user)


@router.delete('/{plan_id}/goals/{goal_id}/activities/{activity_id}', status_code=204, summary='Удалить мероприятие')
def delete_activity(plan_id: int, goal_id: int, activity_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    plan = service.draft(db, plan_id, current_user)
    goal = service.get_goal(plan, goal_id)
    db.delete(service.get_activity(goal, activity_id))
    service.save(db, plan)
    return Response(status_code=204)


@router.post('/{plan_id}/competencies', response_model=PlanCompetencyResponse, status_code=201, summary='Добавить компетенцию и уровни в ИПР')
def add_plan_competency(plan_id: int, plan_comp: PlanCompetencyCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    plan = service.draft(db, plan_id, current_user)
    if db.get(Competency, plan_comp.competency_id) is None:
        service.fail('Компетенция не найдена', 404)
    if db.get(PlanCompetency, (plan_id, plan_comp.competency_id)):
        service.fail('Эта компетенция уже добавлена в ИПР')
    row = PlanCompetency(plan_id=plan_id, **plan_comp.model_dump())
    db.add(row)
    service.save(db, plan)
    return row


@router.patch('/{plan_id}/competencies/{competency_id}', response_model=PlanCompetencyResponse, summary='Изменить уровни компетенции в черновике')
def update_plan_competency(plan_id: int, competency_id: int, values: PlanCompetencyUpdate,
                            db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = service.draft(db, plan_id, current_user)
    row = db.get(PlanCompetency, (plan_id, competency_id))
    if row is None:
        service.fail('Компетенция не найдена в ИПР', 404)
    for key, value in values.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    if row.target_level < row.current_level:
        service.fail('Целевой уровень не может быть ниже текущего')
    service.save(db, plan)
    return row


@router.delete('/{plan_id}/competencies/{competency_id}', status_code=204, summary='Удалить компетенцию из черновика')
def delete_plan_competency(plan_id: int, competency_id: int, db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    plan = service.draft(db, plan_id, current_user)
    row = db.get(PlanCompetency, (plan_id, competency_id))
    if row is None:
        service.fail('Компетенция не найдена в ИПР', 404)
    db.delete(row)
    service.save(db, plan)
    return Response(status_code=204)


@router.patch('/{plan_id}/submit', response_model=DevelopmentPlanResponse, summary='Отправить заполненный черновик руководителю')
def submit_plan(plan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = service.draft(db, plan_id, current_user)
    service.submit(db, plan)
    return plan


@router.patch('/{plan_id}/approve', response_model=DevelopmentPlanResponse, summary='Утвердить ИПР прямого подчинённого')
def approve_plan(plan_id: int, request: PlanApproveRequest, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    return service.decision(db, plan_id, current_user, 'approved', request.manager_comment)


@router.patch('/{plan_id}/reject', response_model=DevelopmentPlanResponse, summary='Отклонить ИПР с комментарием')
def reject_plan(plan_id: int, request: PlanRejectRequest, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    return service.decision(db, plan_id, current_user, 'rejected', request.manager_comment)


@router.patch('/{plan_id}/return', response_model=DevelopmentPlanResponse, summary='Вернуть свой отклонённый ИПР в черновик')
def return_plan(plan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = service.get_plan(db, plan_id, current_user, edit=True, lock=True)
    if plan.status != 'rejected':
        service.fail('Вернуть в черновик можно только отклонённый ИПР')
    plan.status = 'draft'
    service.save(db, plan)
    return plan


@router.patch('/{plan_id}/complete-activity', response_model=DevelopmentPlanResponse, summary='Отметить выполнение и пересчитать прогресс')
def complete_activity(plan_id: int, request: ActivityCompleteRequest, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    return service.complete(db, plan_id, current_user, request)
