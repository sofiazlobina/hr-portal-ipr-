from sqlalchemy import CheckConstraint, Index
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Department(Base):
    __tablename__ = "department"
    __table_args__ = (
        CheckConstraint("(btrim(name) <> '')", name='ck_department_name'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    # Связь: один отдел — много пользователей
    users = relationship("User", back_populates="department")

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}')>"