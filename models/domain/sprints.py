from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.db import Base


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    start_date = Column(DateTime(timezone=True), default=datetime.now)
    end_date = Column(DateTime(timezone=True))
    status = Column(String(20), default="planned")  # planned, active, completed

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="sprints")
    tasks = relationship("Task", back_populates="sprint")