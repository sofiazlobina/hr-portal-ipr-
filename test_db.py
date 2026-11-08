from app.database import SessionLocal
from app.models.department import Department

def test():
    db = SessionLocal()
    try:
        departments = db.query(Department).all()
        print(f"Найдено отделов: {len(departments)}")
        for d in departments[:3]:
            print(f"  - {d.id}: {d.name}")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test()