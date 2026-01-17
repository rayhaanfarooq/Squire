"""
TeamReview model - stores team member feedback/reviews
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.db.database import Base


class TeamReview(Base):
    __tablename__ = "team_review"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    team_member = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TeamReview(id={self.id}, team_member={self.team_member}, created_at={self.created_at})>"

