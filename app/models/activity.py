from sqlalchemy import CheckConstraint, Index
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Activity(Base):
    __tablename__ = "activity"
    __table_args__ = (
        CheckConstraint("(type IN ('course', 'practice', 'reading'))", name='ck_activity_type'),
        CheckConstraint("(btrim(description) <> '')", name='ck_activity_description'),
        CheckConstraint("(status IN ('planned', 'completed'))", name='ck_activity_status'),
        CheckConstraint("((status = 'completed' AND completion_date IS NOT NULL) OR (status = 'planned' AND completion_date IS NULL))", name='ck_activity_completion'),
        Index('idx_activity_goal', 'goal_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goal.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    deadline = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="planned")
    completion_date = Column(Date, nullable=True)

    # Связь
    goal = relationship("Goal", back_populates="activities")

    def __repr__(self):
        return f"<Activity(id={self.id}, goal_id={self.goal_id}, status='{self.status}')>"