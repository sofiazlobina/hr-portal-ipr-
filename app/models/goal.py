from sqlalchemy import CheckConstraint, Index
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Goal(Base):
    __tablename__ = "goal"
    __table_args__ = (
        CheckConstraint("(btrim(description) <> '')", name='ck_goal_description'),
        Index('idx_goal_plan', 'plan_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("development_plan.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    deadline = Column(Date, nullable=False)

    # Связи
    plan = relationship("DevelopmentPlan", back_populates="goals")
    activities = relationship("Activity", back_populates="goal", cascade="all, delete-orphan")

    @property
    def is_completed(self):
        return bool(self.activities) and all(a.status == "completed" for a in self.activities)

    def __repr__(self):
        return f"<Goal(id={self.id}, plan_id={self.plan_id})>"