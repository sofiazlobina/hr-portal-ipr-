"""Создать согласованные демонстрационные данные. Существующие данные сохраняются."""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import Base, engine, SessionLocal
from app.models import Activity, Competency, Department, DevelopmentPlan, Goal, PlanCompetency, User
from app.utils.security import get_password_hash


def seed(reset=False):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.query(User).first() and not reset:
            print('В базе уже есть пользователи. Данные сохранены. Для намеренного пересоздания: --reset')
            return
        try:
            if reset:
                for model in (Activity, PlanCompetency, Goal, DevelopmentPlan):
                    db.query(model).delete(synchronize_session=False)
                db.query(User).update({User.manager_id: None}, synchronize_session=False)
                for model in (User, Competency, Department):
                    db.query(model).delete(synchronize_session=False)
            departments = [Department(name=name) for name in (
                'Разработка', 'Тестирование', 'Аналитика', 'Управление проектами',
                'Техническая поддержка', 'Инфраструктура', 'DevOps', 'HR', 'Финансы', 'Продажи')]
            db.add_all(departments)
            db.flush()
            specs = [
                ('Иванов Иван', 'ivanov', 0, 'manager'),
                ('Петрова Анна', 'petrova', 0, 'employee'),
                ('Сидоров Алексей', 'sidorov', 0, 'employee'),
                ('Козлова Мария', 'kozlova', 1, 'manager'),
                ('Новиков Дмитрий', 'novikov', 1, 'employee'),
                ('Морозова Елена', 'morozova', 2, 'manager'),
                ('Волков Сергей', 'volkov', 2, 'employee'),
                ('Соловьева Ольга', 'soloveva', 3, 'manager'),
                ('Лебедев Андрей', 'lebedev', 3, 'employee'),
                ('Кузнецова Татьяна', 'kuznetsova', 4, 'manager'),
                ('Попов Максим', 'popov', 4, 'employee'),
                ('Васильева Наталья', 'vasileva', 5, 'manager'),
                ('Зайцев Павел', 'zaytsev', 6, 'manager'),
                ('Павлова Ирина', 'pavlova', 7, 'hr'),
                ('Семенов Виктор', 'semenov', 8, 'manager'),
            ]
            users = []
            for name, login, department, role in specs:
                user = User(full_name=name, email=login+'@company.com', role=role,
                            department_id=departments[department].id, is_active=True,
                            password_hash=get_password_hash('password123'))
                users.append(user)
                db.add(user)
            db.flush()
            managers = {u.department_id: u for u in users if u.role == 'manager'}
            for user in users[1:]:
                user.manager_id = managers.get(user.department_id, users[0]).id if user.role == 'employee' else users[0].id
            competencies = [Competency(name=name) for name in (
                'Python', 'SQL', 'Анализ данных', 'Автотестирование', 'Управление проектами',
                'Коммуникация', 'Лидерство', 'Тайм-менеджмент', 'Аналитическое мышление', 'Английский язык')]
            db.add_all(competencies)
            db.flush()
            today = date.today()
            statuses = ['approved', 'draft', 'pending', 'approved', 'completed',
                        'approved', 'draft', 'rejected', 'draft', 'pending']
            for index, status in enumerate(statuses):
                plan = DevelopmentPlan(employee_id=users[index].id, status=status,
                                       start_date=today-timedelta(days=30), end_date=today+timedelta(days=60),
                                       manager_comment='Уточните ожидаемый результат' if status == 'rejected' else None)
                db.add(plan)
                db.flush()
                if index == 8:  # Пустой черновик допустим.
                    continue
                goal = Goal(plan_id=plan.id, description='Развить практические навыки '+competencies[index].name,
                            deadline=plan.end_date)
                db.add(goal)
                db.flush()
                completed = status == 'completed'
                db.add(Activity(goal_id=goal.id, type='practice', description='Выполнить учебный проект',
                                deadline=today+timedelta(days=20), status='completed' if completed else 'planned',
                                completion_date=today-timedelta(days=1) if completed else None))
                db.add(PlanCompetency(plan_id=plan.id, competency_id=competencies[index].id,
                                      current_level=2, target_level=4))
            db.commit()
            print('Готово: 10 отделов, 15 пользователей, 10 компетенций, 10 ИПР. Пароль: password123')
            print('HR: pavlova@company.com. Руководитель: ivanov@company.com. Сотрудник: petrova@company.com.')
        except Exception:
            db.rollback()
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reset', action='store_true', help='Удалить все данные модуля и заполнить заново')
    seed(parser.parse_args().reset)
