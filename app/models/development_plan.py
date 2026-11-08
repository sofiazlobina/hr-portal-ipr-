from sqlalchemy import CheckConstraint, Index
from sqlalchemy import Column, Integer, String, Date, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class DevelopmentPlan(Base):
    __tablename__ = "development_plan"
    __table_args__ = (
        CheckConstraint("(status IN ('draft', 'pending', 'approved', 'rejected', 'completed'))", name='ck_development_plan_status'),
        CheckConstraint('(end_date >= start_date)', name='ck_development_plan_dates'),
        CheckConstraint("(status <> 'rejected' OR (manager_comment IS NOT NULL AND btrim(manager_comment) <> ''))", name='ck_development_plan_rejection'),
        Index('idx_development_plan_employee', 'employee_id'),
        Index('idx_development_plan_status', 'status'),
    )

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("app_user.id"), nullable=False)
    status = Column(String(20), nullable=False, default="draft")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    manager_comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Связи
    employee = relationship("User", back_populates="development_plans")
    goals = relationship("Goal", back_populates="plan", cascade="all, delete-orphan")
    competencies = relationship("PlanCompetency", back_populates="plan", cascade="all, delete-orphan")

    @property
    def progress(self):
        activities = [a for g in self.goals for a in g.activities]
        return round(100 * sum(a.status == "completed" for a in activities) / len(activities), 2) if activities else 0.0

    def __repr__(self):
        return f"<DevelopmentPlan(id={self.id}, employee_id={self.employee_id}, status='{self.status}')>"