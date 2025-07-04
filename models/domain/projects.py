from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from core.db import Base
from models.domain.user_project import user_project_table

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    logo = Column(String(500))
    start_date = Column(DateTime(timezone=True), default=func.now())
    end_date = Column(DateTime(timezone=True))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_private = Column(Integer, default=0) 

    owner = relationship("User", back_populates="projects_owned")
    sprints = relationship("Sprint", back_populates="project")
    tasks = relationship("Task", back_populates="project")
    messages = relationship("Message", back_populates="project")
    users = relationship("User", secondary=user_project_table, back_populates="projects")
    columns = relationship("TaskColumn", back_populates="project")
    user_progress = relationship("UserProjectProgress", back_populates="project")
    activities = relationship("ProjectActivity", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project")