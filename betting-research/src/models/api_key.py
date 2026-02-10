"""
API Key Model

Stores API keys for third-party service integrations (Kalshi, etc.).
Keys are hashed before storage for security.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from ..models import Base


class APIKey(Base):
    """API key storage model for external services"""

    __tablename__ = 'api_keys'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Row-level security
    account_id = Column(Integer, nullable=False, index=True)

    # User who owns this API key
    user_id = Column(Integer, nullable=False, index=True)

    # Service information
    service_name = Column(String(50), nullable=False, index=True)  # e.g., "kalshi", "dashboard"
    service_environment = Column(String(20), default='production')  # e.g., "production", "sandbox"

    # API key (hashed for security)
    key_hash = Column(String(255), nullable=False)  # Hash of the actual key
    key_prefix = Column(String(10), nullable=False)  # First few chars for identification

    # Key metadata
    description = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)
    last_used_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return (f"<APIKey(id={self.id}, service='{self.service_name}', "
                f"key_prefix='{self.key_prefix}', account_id={self.account_id})>")

    def to_dict(self):
        """Convert model to dictionary (exclude full key_hash)"""
        return {
            'id': self.id,
            'account_id': self.account_id,
            'user_id': self.user_id,
            'service_name': self.service_name,
            'service_environment': self.service_environment,
            'key_prefix': self.key_prefix,
            'description': self.description,
            'is_active': self.is_active,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
        }
