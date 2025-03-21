from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from core.db import Base
from models.domain.user_project import user_project_table


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    sub = Column(String, unique=True, index=True)  # ID из SEVSU
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    group = Column(String)
    hashed_password = Column(String, nullable=True)

    projects_owned = relationship("Project", back_populates="owner")
    tasks = relationship("Task", back_populates="assignee")
    sent_messages = relationship("Message", back_populates="sender")
    projects = relationship("Project", secondary=user_project_table, back_populates="users")
    tokens = relationship("Token", back_populates="user")