"""
User Model

Stores user account information with Argon2 password hashing.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from ..models import Base


class User(Base):
    """User account model with password hashing support"""

    __tablename__ = 'users'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Row-level security: all user data must include account_id
    account_id = Column(Integer, nullable=False, index=True)

    # User information
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)

    # Password (Argon2 hashed)
    password_hash = Column(String(255), nullable=False)

    # User status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))
    last_login_ip = Column(String(45))

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', account_id={self.account_id})>"

    def to_dict(self):
        """Convert model to dictionary (exclude password_hash)"""
        return {
            'id': self.id,
            'account_id': self.account_id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'last_login_ip': self.last_login_ip,
        }
