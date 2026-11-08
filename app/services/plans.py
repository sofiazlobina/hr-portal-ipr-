"""Права, бизнес-правила и транзакции ИПР."""
from datetime import date, datetime, timezone
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from app.models import DevelopmentPlan, Goal, User


def fail(message, status=400):
    raise HTTPException(status_code=status, detail=message)


def loaded(query):
    return query.options(
        selectinload(DevelopmentPlan.goals).selectinload(Goal.activities),
        selectinload(DevelopmentPlan.competencies),
    )


def visible_employee_ids(db, user):
    ids = [user.id]
    if user.role == 'manager':
        ids += [row[0] for row in db.query(User.id).filter(
            User.manager_id == user.id, User.is_active.is_(True)
        ).all()]
    return ids


def get_plan(db, plan_id, user, *, edit=False, lock=False):
    query = db.query(DevelopmentPlan).filter(DevelopmentPlan.id == plan_id)
    if lock:
        query = query.with_for_update()
    plan = loaded(query).first()
    if plan is None:
        fail('ИПР не найден', 404)
    if edit:
        if plan.employee_id != user.id:
            fail('Изменять ИПР может только его владелец', 403)
    elif plan.employee_id not in visible_employee_ids(db, user):
        fail('Нет доступа к этому ИПР', 403)
    return plan


def draft(db, plan_id, user):
    plan = get_plan(db, plan_id, user, edit=True, lock=True)
    if plan.status != 'draft':
        fail('Изменять и удалять содержание можно только в статусе draft')
    return plan


def get_goal(plan, goal_id):
    goal = next((g for g in plan.goals if g.id == goal_id), None)
    if goal is None:
        fail('Цель не найдена в этом ИПР', 404)
    return goal


def get_activity(goal, activity_id):
    activity = next((a for a in goal.activities if a.id == activity_id), None)
    if activity is None:
        fail('Мероприятие не найдено у этой цели', 404)
    return activity


def validate_dates(plan):
    if plan.end_date < plan.start_date:
        fail('Дата окончания не может быть раньше даты начала')
    for goal in plan.goals:
        if not plan.start_date <= goal.deadline <= plan.end_date:
            fail('Срок каждой цели должен находиться в периоде ИПР')
        for activity in goal.activities:
            if not plan.start_date <= activity.deadline <= goal.deadline:
                fail('Срок мероприятия должен быть между началом ИПР и сроком цели')


def save(db, plan=None):
    if plan is not None:
        plan.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        fail('Изменение конфликтует с данными в базе', 409)


def submit(db, plan):
    owner = db.get(User, plan.employee_id)
    manager = db.get(User, owner.manager_id) if owner.manager_id else None
    if manager is None or not manager.is_active or manager.role != 'manager' or manager.id == owner.id:
        fail('Нужен действующий непосредственный руководитель с ролью manager')
    if not plan.goals or any(not g.activities for g in plan.goals) or not plan.competencies:
        fail('Нужны хотя бы одна цель, мероприятие у каждой цели и одна компетенция')
    validate_dates(plan)
    plan.status = 'pending'
    save(db, plan)


def decision(db, plan_id, user, status, comment):
    plan = get_plan(db, plan_id, user, lock=True)
    owner = db.get(User, plan.employee_id)
    if user.role != 'manager' or user.id == plan.employee_id or owner.manager_id != user.id:
        fail('Решение принимает непосредственный руководитель, самосогласование запрещено', 403)
    if plan.status != 'pending':
        fail('Решение возможно только для плана в статусе pending')
    plan.status = status
    plan.manager_comment = comment
    save(db, plan)
    return plan


def complete(db, plan_id, user, request):
    plan = get_plan(db, plan_id, user, edit=True, lock=True)
    if plan.status != 'approved':
        fail('Отмечать выполнение можно только в утверждённом плане')
    activity = next((a for g in plan.goals for a in g.activities if a.id == request.activity_id), None)
    if activity is None:
        fail('Мероприятие не найдено в этом ИПР', 404)
    if activity.status == 'completed':
        fail('Мероприятие уже выполнено')
    completed_on = request.completion_date or date.today()
    if not plan.start_date <= completed_on <= date.today():
        fail('Дата выполнения должна быть от начала ИПР до сегодняшнего дня')
    activity.status = 'completed'
    activity.completion_date = completed_on
    activities = [a for g in plan.goals for a in g.activities]
    if activities and all(a.status == 'completed' for a in activities):
        plan.status = 'completed'
    # Отметка мероприятия и завершение ИПР сохраняются одним commit.
    save(db, plan)
    return plan
