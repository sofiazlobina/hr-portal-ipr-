from sqlalchemy import CheckConstraint, Index
from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class PlanCompetency(Base):
    __tablename__ = "plan_competency"

    plan_id = Column(Integer, ForeignKey("development_plan.id", ondelete="CASCADE"), nullable=False)
    competency_id = Column(Integer, ForeignKey("competency.id"), nullable=False)
    current_level = Column(Integer, nullable=False)
    target_level = Column(Integer, nullable=False)

    # Связи
    plan = relationship("DevelopmentPlan", back_populates="competencies")
    competency = relationship("Competency", back_populates="plans")

    # Составной первичный ключ
    __table_args__ = (
        PrimaryKeyConstraint("plan_id", "competency_id"),
        CheckConstraint('(current_level BETWEEN 1 AND 5)', name='ck_plan_competency_current'),
        CheckConstraint('(target_level BETWEEN 1 AND 5)', name='ck_plan_competency_target'),
        CheckConstraint('(target_level >= current_level)', name='ck_plan_competency_growth'),
        Index('idx_plan_competency_competency', 'competency_id'),
    )

    def __repr__(self):
        return f"<PlanCompetency(plan_id={self.plan_id}, competency_id={self.competency_id})>"