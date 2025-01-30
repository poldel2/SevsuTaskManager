from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from core.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    sub = Column(String, unique=True, index=True)  # ID из SEVSU
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    group = Column(String)

    projects = relationship("Project", back_populates="owner")
