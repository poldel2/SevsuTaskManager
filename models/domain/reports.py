from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Date, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from core.db import Base


class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    data = Column(JSONB)
    period_start = Column(Date)
    period_end = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now)

    project_id = Column(Integer, ForeignKey('projects.id'))

    project = relationship("Project", back_populates="reports")