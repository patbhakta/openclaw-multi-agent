"""
Security Event Model

Stores security events for comprehensive audit trail.
All security-related activities are logged for compliance.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from ..models import Base


class SecurityEvent(Base):
    """Security event logging model for audit trail"""

    __tablename__ = 'security_events'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Event classification
    severity = Column(String(20), nullable=False, index=True)  # "critical", "high", "medium", "low", "info"
    event_type = Column(String(50), nullable=False, index=True)  # e.g., "login_success", "token_issued"

    # Row-level security (optional - some events may not have a user)
    account_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)

    # Event details
    details = Column(Text)

    # Request information
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(Text)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return (f"<SecurityEvent(id={self.id}, severity='{self.severity}', "
                f"event_type='{self.event_type}', user_id={self.user_id})>")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'severity': self.severity,
            'event_type': self.event_type,
            'account_id': self.account_id,
            'user_id': self.user_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
