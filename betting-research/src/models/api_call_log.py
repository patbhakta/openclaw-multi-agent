"""
API Call Log Model

Stores API call logs for performance monitoring and analysis.
All external API calls are logged for debugging and optimization.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from ..models import Base


class APICallLog(Base):
    """API call logging model for performance monitoring"""

    __tablename__ = 'api_call_logs'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Row-level security (optional - some calls may not be user-specific)
    account_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)

    # API call information
    service = Column(String(50), nullable=False, index=True)  # e.g., "kalshi", "dashboard"
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), default='GET')  # "GET", "POST", "PUT", "DELETE"

    # Performance metrics
    duration_ms = Column(Integer)  # Request duration in milliseconds
    status_code = Column(Integer)  # HTTP status code
    success = Column(Boolean, nullable=False, index=True)

    # Request/Response sizes
    request_size = Column(Integer)  # Request size in bytes
    response_size = Column(Integer)  # Response size in bytes

    # Request metadata
    ip_address = Column(String(45))  # Client IP address
    error_message = Column(Text)  # Error details (if failed)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return (f"<APICallLog(id={self.id}, service='{self.service}', "
                f"endpoint='{self.endpoint}', method='{self.method}', "
                f"duration_ms={self.duration_ms}, success={self.success})>")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'account_id': self.account_id,
            'user_id': self.user_id,
            'service': self.service,
            'endpoint': self.endpoint,
            'method': self.method,
            'duration_ms': self.duration_ms,
            'status_code': self.status_code,
            'success': self.success,
            'request_size': self.request_size,
            'response_size': self.response_size,
            'ip_address': self.ip_address,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
