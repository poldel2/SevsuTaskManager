from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.db import Base

class TaskColumn(Base):
    __tablename__ = "task_columns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    position = Column(Integer, default=0)
    color = Column(String, default="#808080")

    project = relationship("Project", back_populates="columns")
    tasks = relationship("Task", back_populates="column")