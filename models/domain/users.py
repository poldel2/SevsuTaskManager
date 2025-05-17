from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship, object_session

from core.db import Base
from models.domain.user_project import user_project_table, Role


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
    avatar = Column(String, nullable=True)

    projects_owned = relationship("Project", back_populates="owner")
    tasks = relationship("Task", back_populates="assignee")
    sent_messages = relationship("Message", back_populates="sender")
    projects = relationship("Project", secondary=user_project_table, back_populates="users")
    tokens = relationship("Token", back_populates="user")
    progress = relationship("UserProjectProgress", back_populates="user")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("ProjectActivity", back_populates="user")

    @property
    def is_teacher(self):
        try:
            session = object_session(self)
            if not session:
                return False 
                
            result = session.query(user_project_table).filter(
                user_project_table.c.user_id == self.id,
                user_project_table.c.role == Role.TEACHER
            ).first()
            
            return result is not None
        except Exception:
            return False

    @property
    def project_associations(self):
        session = object_session(self)
        if not session:
            return [] 
        return session.query(user_project_table).filter(
            user_project_table.c.user_id == self.id
        ).all()

    def is_project_leader(self, project_id: int) -> bool:
        try:
            session = object_session(self)
            if not session:
                return False 
                
            result = session.query(user_project_table).filter(
                user_project_table.c.user_id == self.id,
                user_project_table.c.project_id == project_id,
                user_project_table.c.role.in_([Role.ADMIN, Role.OWNER])
            ).first()
            
            return result is not None
        except Exception:
            return False