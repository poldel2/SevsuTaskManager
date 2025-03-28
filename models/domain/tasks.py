from datetime import datetime
from enum import Enum

from sqlalchemy import Column, Enum as SQLEnum, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.db import Base

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    NEED_REVIEW = "need_review"
    APPROVED_BY_LEADER = "approved_by_leader"
    APPROVED_BY_TEACHER = "approved_by_teacher"
    REJECTED = "rejected"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskGrade(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    grade = Column(SQLEnum(TaskGrade), nullable=True)
    feedback = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    due_date = Column(DateTime(timezone=True))

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True) 
    column_id = Column(Integer, ForeignKey("task_columns.id"), nullable=True)

    project = relationship("Project", back_populates="tasks")
    sprint = relationship("Sprint", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")
    column = relationship("TaskColumn", back_populates="tasks")


class ProjectGradingSettings(Base):
    __tablename__ = "project_grading_settings"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True)

    required_easy_tasks = Column(Integer, default=1)
    required_medium_tasks = Column(Integer, default=1)
    required_hard_tasks = Column(Integer, default=1)


class UserProjectProgress(Base):
    __tablename__ = "user_project_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))

    completed_easy = Column(Integer, default=0)
    completed_medium = Column(Integer, default=0)
    completed_hard = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.now)

    auto_grade = Column(String(20), nullable=True)  # "A", "B", "C", "Pass/Fail"
    manual_grade = Column(String(20), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    project = relationship("Project", back_populates="user_progress")