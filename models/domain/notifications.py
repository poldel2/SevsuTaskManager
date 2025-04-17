from enum import Enum
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from core.db import Base

class NotificationType(str, Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_UPDATED = "task_updated"
    TEAM_INVITATION = "team_invitation"
    SPRINT_STARTED = "sprint_started"
    SPRINT_ENDED = "sprint_ended"
    COMMENT_ADDED = "comment_added"
    PROJECT_UPDATE = "project_update"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    notification_metadata = Column(JSON, nullable=True)
    
    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index('ix_notifications_user_created', user_id, created_at), 
        Index('ix_notifications_created_at', created_at.desc()),    
    )

    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.type}, user_id={self.user_id})>"