"""Тесты создают отдельную временную PostgreSQL-БД, не трогая hr_ipr."""
import os
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

# Приложение должно импортироваться после настройки URL.
os.environ.setdefault('DATABASE_URL', os.environ.get('TEST_DATABASE_URL', 'postgresql://postgres@localhost/hr_ipr'))
from app.database import Base, get_db
from app.main import app
from app.models import Department, User
from app.utils.security import create_access_token, get_password_hash
from fastapi.testclient import TestClient

PASSWORD_HASH = get_password_hash('password123')


@pytest.fixture(scope='session')
def test_engine():
    raw = os.environ.get('TEST_DATABASE_URL')
    if not raw:
        pytest.skip('Укажите TEST_DATABASE_URL для отдельного тестового PostgreSQL-сервера')
    url = make_url(raw)
    name = 'hr_ipr_test_' + uuid.uuid4().hex[:12]
    admin = create_engine(url, isolation_level='AUTOCOMMIT')
    with admin.connect() as conn:
        conn.exec_driver_sql(f'CREATE DATABASE "{name}"')
    engine = create_engine(url.set(database=name))
    try:
        Base.metadata.create_all(engine)
        yield engine
    finally:
        engine.dispose()
        with admin.connect() as conn:
            conn.exec_driver_sql(f'DROP DATABASE "{name}" WITH (FORCE)')
        admin.dispose()


@pytest.fixture
def db(test_engine):
    with test_engine.connect() as connection:
        transaction = connection.begin()
        session = Session(bind=connection, join_transaction_mode='create_savepoint', autoflush=False)
        try:
            yield session
        finally:
            session.close()
            transaction.rollback()


@pytest.fixture
def people(db):
    dept = Department(name='Test department')
    db.add(dept)
    db.flush()
    result = {}
    for key, role in [('manager', 'manager'), ('other_manager', 'manager'), ('employee', 'employee'),
                      ('other', 'employee'), ('hr', 'hr'), ('inactive', 'employee')]:
        result[key] = User(full_name=key, email=key+'@example.com', role=role,
                           department_id=dept.id, password_hash=PASSWORD_HASH, is_active=key != 'inactive')
        db.add(result[key])
    db.flush()
    result['employee'].manager_id = result['manager'].id
    result['inactive'].manager_id = result['manager'].id
    result['other'].manager_id = result['other_manager'].id
    db.commit()
    return result


@pytest.fixture
def client(db):
    def override():
        yield db
    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def headers(people):
    return {key: {'Authorization': 'Bearer '+create_access_token({'sub': user.id})}
            for key, user in people.items()}
