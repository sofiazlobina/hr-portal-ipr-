from sqlalchemy import CheckConstraint, Index
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "app_user"
    __table_args__ = (
        CheckConstraint("(btrim(full_name) <> '')", name='ck_app_user_full_name'),
        CheckConstraint("(email = lower(btrim(email)) AND email <> '')", name='ck_app_user_email'),
        CheckConstraint("(btrim(password_hash) <> '')", name='ck_app_user_password_hash'),
        CheckConstraint("(role IN ('employee', 'manager', 'hr'))", name='ck_app_user_role'),
        CheckConstraint('(manager_id IS NULL OR manager_id <> id)', name='ck_app_user_manager'),
        Index('idx_app_user_active', 'is_active'),
        Index('idx_app_user_department', 'department_id'),
        Index('idx_app_user_manager', 'manager_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(254), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    department_id = Column(Integer, ForeignKey("department.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("app_user.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    deactivated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Связи
    department = relationship("Department", back_populates="users")
    manager = relationship("User", remote_side=[id], backref="subordinates")
    development_plans = relationship("DevelopmentPlan", back_populates="employee")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"