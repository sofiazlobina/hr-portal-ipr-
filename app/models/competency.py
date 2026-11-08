from sqlalchemy import CheckConstraint, Index
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Competency(Base):
    __tablename__ = "competency"
    __table_args__ = (
        CheckConstraint("(btrim(name) <> '')", name='ck_competency_name'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # Связь M:N через ассоциативную таблицу
    plans = relationship("PlanCompetency", back_populates="competency")

    def __repr__(self):
        return f"<Competency(id={self.id}, name='{self.name}')>"