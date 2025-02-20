from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.db import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    status = Column(String(20), default="todo")  # Например: "todo", "in_progress", "done"
    priority = Column(String(10), default="medium")  # Например: "low", "medium", "high"
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Исполнитель

    project = relationship("Project", back_populates="tasks")
    sprint = relationship("Sprint", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")  # Связь с User
