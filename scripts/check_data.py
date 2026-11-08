"""Проверка существующих данных. Только SELECT, ничего не изменяет."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import text
from app.database import engine

QUERIES = {
    'hr_users': "SELECT count(*) FROM app_user WHERE role='hr'",
    'invalid_activity_type': "SELECT id FROM activity WHERE type NOT IN ('course','practice','reading')",
    'invalid_activity_status': "SELECT id FROM activity WHERE status NOT IN ('planned','completed')",
    'future_completion': "SELECT id FROM activity WHERE completion_date > CURRENT_DATE",
    'invalid_goal_deadline': "SELECT g.id FROM goal g JOIN development_plan p ON p.id=g.plan_id WHERE g.deadline NOT BETWEEN p.start_date AND p.end_date",
    'invalid_activity_deadline': "SELECT a.id FROM activity a JOIN goal g ON g.id=a.goal_id JOIN development_plan p ON p.id=g.plan_id WHERE a.deadline NOT BETWEEN p.start_date AND g.deadline",
    'incomplete_pending': """SELECT p.id FROM development_plan p WHERE p.status='pending' AND (
        NOT EXISTS(SELECT 1 FROM goal g WHERE g.plan_id=p.id) OR
        EXISTS(SELECT 1 FROM goal g WHERE g.plan_id=p.id AND NOT EXISTS(SELECT 1 FROM activity a WHERE a.goal_id=g.id)) OR
        NOT EXISTS(SELECT 1 FROM plan_competency c WHERE c.plan_id=p.id))""",
    'invalid_completed': """SELECT p.id FROM development_plan p WHERE p.status='completed' AND (
        NOT EXISTS(SELECT 1 FROM activity a JOIN goal g ON g.id=a.goal_id WHERE g.plan_id=p.id) OR
        EXISTS(SELECT 1 FROM activity a JOIN goal g ON g.id=a.goal_id WHERE g.plan_id=p.id AND a.status<>'completed'))""",
    'missing_or_invalid_manager': """SELECT u.id FROM app_user u LEFT JOIN app_user m ON m.id=u.manager_id
        WHERE u.manager_id IS NOT NULL AND (m.id IS NULL OR m.role<>'manager' OR m.id=u.id)""",
    'check_constraint_count': "SELECT count(*) FROM pg_constraint WHERE contype='c' AND connamespace='public'::regnamespace",
}
if __name__ == '__main__':
    with engine.connect() as connection:
        result={key:[row[0] for row in connection.execute(text(sql))] for key,sql in QUERIES.items()}
    print(json.dumps(result,ensure_ascii=False,indent=2))
