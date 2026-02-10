"""
Audit Logger

Comprehensive audit trail system for security events, trades, and API calls.
Provides complete logging for compliance and security monitoring.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Severity(Enum):
    """Security event severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class EventType(Enum):
    """Security event types"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    TOKEN_ISSUED = "token_issued"
    TOKEN_REFRESHED = "token_refreshed"
    TOKEN_INVALIDATED = "token_invalidated"
    API_ACCESS = "api_access"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    PERMISSION_DENIED = "permission_denied"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SECURITY_ALERT = "security_alert"
    SYSTEM_ERROR = "system_error"


class AuditLogger:
    """
    Comprehensive audit trail logger

    Logs security events, trades, and API calls to database
    for compliance monitoring and security analysis.
    """

    def __init__(self, db_manager=None):
        """
        Initialize audit logger

        Args:
            db_manager: DatabaseManager instance for storing audit logs
                        If None, logs to console only
        """
        self.db = db_manager

        if self.db:
            logger.info("AuditLogger initialized with database storage")
            self._ensure_audit_tables()
        else:
            logger.warning("AuditLogger initialized without database (console logging only)")

    def _ensure_audit_tables(self):
        """
        Ensure audit log tables exist in database

        Creates tables if they don't exist.
        """
        try:
            # Security events table
            create_security_events = """
                CREATE TABLE IF NOT EXISTS security_events (
                    id SERIAL PRIMARY KEY,
                    severity VARCHAR(20) NOT NULL,
                    event_type VARCHAR(50) NOT NULL,
                    user_id INTEGER,
                    details TEXT,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_security_events_user_id ON security_events(user_id);
                CREATE INDEX IF NOT EXISTS idx_security_events_severity ON security_events(severity);
                CREATE INDEX IF NOT EXISTS idx_security_events_event_type ON security_events(event_type);
                CREATE INDEX IF NOT EXISTS idx_security_events_created_at ON security_events(created_at);
            """

            # Trade audit table
            create_trade_audit = """
                CREATE TABLE IF NOT EXISTS trade_audit (
                    id SERIAL PRIMARY KEY,
                    trade_id VARCHAR(255),
                    action VARCHAR(20) NOT NULL,
                    amount FLOAT,
                    market_type VARCHAR(50),
                    market_id VARCHAR(255),
                    user_id INTEGER,
                    status VARCHAR(20),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_trade_audit_trade_id ON trade_audit(trade_id);
                CREATE INDEX IF NOT EXISTS idx_trade_audit_user_id ON trade_audit(user_id);
                CREATE INDEX IF NOT EXISTS idx_trade_audit_created_at ON trade_audit(created_at);
            """

            # API call logs table
            create_api_logs = """
                CREATE TABLE IF NOT EXISTS api_call_logs (
                    id SERIAL PRIMARY KEY,
                    service VARCHAR(50) NOT NULL,
                    endpoint VARCHAR(255) NOT NULL,
                    method VARCHAR(10),
                    user_id INTEGER,
                    duration_ms INTEGER,
                    status_code INTEGER,
                    success BOOLEAN,
                    request_size INTEGER,
                    response_size INTEGER,
                    ip_address VARCHAR(45),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_api_logs_service ON api_call_logs(service);
                CREATE INDEX IF NOT EXISTS idx_api_logs_user_id ON api_call_logs(user_id);
                CREATE INDEX IF NOT EXISTS idx_api_logs_created_at ON api_call_logs(created_at);
            """

            with self.db.connection.cursor() as cursor:
                cursor.execute(create_security_events)
                cursor.execute(create_trade_audit)
                cursor.execute(create_api_logs)
                self.db.connection.commit()

            logger.info("✅ Audit tables verified/created")

        except Exception as e:
            logger.error(f"❌ Failed to create audit tables: {e}")

    def log_security_event(self,
                           severity: Severity,
                           event_type: EventType,
                           user_id: Optional[int] = None,
                           details: Optional[str] = None,
                           ip_address: Optional[str] = None,
                           user_agent: Optional[str] = None):
        """
        Log a security event

        Args:
            severity: Event severity (CRITICAL, HIGH, MEDIUM, LOW, INFO)
            event_type: Type of security event
            user_id: User ID involved (if applicable)
            details: Additional event details
            ip_address: Client IP address
            user_agent: Client user agent string
        """
        timestamp = datetime.now(timezone.utc)

        # Log to console
        log_level = {
            Severity.CRITICAL: logging.CRITICAL,
            Severity.HIGH: logging.ERROR,
            Severity.MEDIUM: logging.WARNING,
            Severity.LOW: logging.INFO,
            Severity.INFO: logging.INFO
        }.get(severity, logging.INFO)

        extra_info = f"user_id={user_id}" if user_id else ""
        logger.log(log_level,
                  f"[SECURITY] {event_type.value} - {details} {extra_info}",
                  extra={
                      'severity': severity.value,
                      'event_type': event_type.value,
                      'user_id': user_id,
                      'ip_address': ip_address
                  })

        # Log to database
        if self.db:
            try:
                query = """
                    INSERT INTO security_events
                    (severity, event_type, user_id, details, ip_address, user_agent, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                with self.db.connection.cursor() as cursor:
                    cursor.execute(query, (
                        severity.value,
                        event_type.value,
                        user_id,
                        details,
                        ip_address,
                        user_agent,
                        timestamp
                    ))
                    self.db.connection.commit()

            except Exception as e:
                logger.error(f"Failed to log security event to database: {e}")

    def log_trade(self,
                 trade_id: Optional[str] = None,
                 action: Optional[str] = None,
                 amount: Optional[float] = None,
                 market_type: Optional[str] = None,
                 market_id: Optional[str] = None,
                 user_id: Optional[int] = None,
                 status: Optional[str] = None):
        """
        Log a trade event

        Args:
            trade_id: Unique trade identifier
            action: Trade action (BUY, SELL, CANCEL, etc.)
            amount: Trade amount
            market_type: Type of market (e.g., "nfl_superbowl")
            market_id: Market identifier
            user_id: User ID who initiated trade
            status: Trade status (PENDING, FILLED, CANCELLED, etc.)
        """
        timestamp = datetime.now(timezone.utc)

        # Log to console
        logger.info(f"[TRADE] {action} {amount} on {market_type} (market_id={market_id}, "
                   f"user_id={user_id}, status={status})")

        # Log to database
        if self.db:
            try:
                query = """
                    INSERT INTO trade_audit
                    (trade_id, action, amount, market_type, market_id, user_id, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                with self.db.connection.cursor() as cursor:
                    cursor.execute(query, (
                        trade_id,
                        action,
                        amount,
                        market_type,
                        market_id,
                        user_id,
                        status,
                        timestamp
                    ))
                    self.db.connection.commit()

            except Exception as e:
                logger.error(f"Failed to log trade to database: {e}")

    def log_api_call(self,
                    service: str,
                    endpoint: str,
                    method: str = "GET",
                    user_id: Optional[int] = None,
                    duration_ms: Optional[int] = None,
                    status_code: Optional[int] = None,
                    success: Optional[bool] = None,
                    request_size: Optional[int] = None,
                    response_size: Optional[int] = None,
                    ip_address: Optional[str] = None):
        """
        Log an API call

        Args:
            service: Service name (e.g., "kalshi", "dashboard")
            endpoint: API endpoint path
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            user_id: User ID making the request
            duration_ms: Request duration in milliseconds
            status_code: HTTP status code
            success: Whether request was successful
            request_size: Request size in bytes
            response_size: Response size in bytes
            ip_address: Client IP address
        """
        timestamp = datetime.now(timezone.utc)

        # Log to console (only slow or failed requests)
        if (duration_ms and duration_ms > 1000) or (success is False):
            logger.warning(f"[API] {method} {service}{endpoint} - "
                         f"status={status_code}, duration={duration_ms}ms, "
                         f"success={success}, user_id={user_id}")

        # Log to database
        if self.db:
            try:
                query = """
                    INSERT INTO api_call_logs
                    (service, endpoint, method, user_id, duration_ms, status_code,
                     success, request_size, response_size, ip_address, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                with self.db.connection.cursor() as cursor:
                    cursor.execute(query, (
                        service,
                        endpoint,
                        method,
                        user_id,
                        duration_ms,
                        status_code,
                        success,
                        request_size,
                        response_size,
                        ip_address,
                        timestamp
                    ))
                    self.db.connection.commit()

            except Exception as e:
                logger.error(f"Failed to log API call to database: {e}")

    def get_security_events(self,
                           user_id: Optional[int] = None,
                           severity: Optional[Severity] = None,
                           event_type: Optional[EventType] = None,
                           limit: int = 100) -> list:
        """
        Get security events from audit log

        Args:
            user_id: Filter by user ID
            severity: Filter by severity
            event_type: Filter by event type
            limit: Maximum number of events to return

        Returns:
            List of security events
        """
        if not self.db:
            logger.warning("Cannot retrieve events: no database connection")
            return []

        try:
            query = "SELECT * FROM security_events WHERE 1=1"
            params = []

            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)

            if severity:
                query += " AND severity = %s"
                params.append(severity.value)

            if event_type:
                query += " AND event_type = %s"
                params.append(event_type.value)

            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)

            results = self.db.execute_query(query, tuple(params))
            return results

        except Exception as e:
            logger.error(f"Failed to retrieve security events: {e}")
            return []

    def get_trade_audit(self,
                       user_id: Optional[int] = None,
                       market_type: Optional[str] = None,
                       limit: int = 100) -> list:
        """
        Get trade audit logs

        Args:
            user_id: Filter by user ID
            market_type: Filter by market type
            limit: Maximum number of records to return

        Returns:
            List of trade records
        """
        if not self.db:
            logger.warning("Cannot retrieve trade logs: no database connection")
            return []

        try:
            query = "SELECT * FROM trade_audit WHERE 1=1"
            params = []

            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)

            if market_type:
                query += " AND market_type = %s"
                params.append(market_type)

            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)

            results = self.db.execute_query(query, tuple(params))
            return results

        except Exception as e:
            logger.error(f"Failed to retrieve trade logs: {e}")
            return []

    def get_api_logs(self,
                    service: Optional[str] = None,
                    user_id: Optional[int] = None,
                    limit: int = 100) -> list:
        """
        Get API call logs

        Args:
            service: Filter by service name
            user_id: Filter by user ID
            limit: Maximum number of records to return

        Returns:
            List of API call records
        """
        if not self.db:
            logger.warning("Cannot retrieve API logs: no database connection")
            return []

        try:
            query = "SELECT * FROM api_call_logs WHERE 1=1"
            params = []

            if service:
                query += " AND service = %s"
                params.append(service)

            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)

            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)

            results = self.db.execute_query(query, tuple(params))
            return results

        except Exception as e:
            logger.error(f"Failed to retrieve API logs: {e}")
            return []


# Singleton instance for convenient access
_default_audit_logger = None


def get_audit_logger(db_manager=None) -> AuditLogger:
    """
    Get the default AuditLogger instance

    Args:
        db_manager: DatabaseManager instance (only used on first call)

    Returns:
        AuditLogger instance
    """
    global _default_audit_logger
    if _default_audit_logger is None:
        _default_audit_logger = AuditLogger(db_manager)
    return _default_audit_logger


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Audit Logger Example")
    print("=" * 60)

    # Note: This example uses console logging only
    # In production, pass a DatabaseManager instance
    audit_logger = AuditLogger()

    print(f"\n✓ AuditLogger initialized")

    # Test security event logging
    print(f"\n{'─' * 60}")
    print(f"Testing security event logging:")

    audit_logger.log_security_event(
        severity=Severity.INFO,
        event_type=EventType.LOGIN_SUCCESS,
        user_id=12345,
        details="User logged in successfully",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0"
    )

    audit_logger.log_security_event(
        severity=Severity.HIGH,
        event_type=EventType.LOGIN_FAILURE,
        user_id=None,
        details="Failed login attempt for user admin",
        ip_address="192.168.1.200",
        user_agent="curl/7.68.0"
    )

    audit_logger.log_security_event(
        severity=Severity.MEDIUM,
        event_type=EventType.RATE_LIMIT_EXCEEDED,
        user_id=67890,
        details="User exceeded rate limit (60 req/min)",
        ip_address="192.168.1.150",
        user_agent="python-requests/2.28.0"
    )

    # Test trade logging
    print(f"\n{'─' * 60}")
    print(f"Testing trade logging:")

    audit_logger.log_trade(
        trade_id="trade_12345",
        action="BUY",
        amount=100.0,
        market_type="nfl_superbowl",
        market_id="market_kc_vs_phi_qb_yards",
        user_id=12345,
        status="PENDING"
    )

    audit_logger.log_trade(
        trade_id="trade_12346",
        action="SELL",
        amount=50.0,
        market_type="nfl_superbowl",
        market_id="market_kc_vs_phi_first_score",
        user_id=12345,
        status="FILLED"
    )

    # Test API call logging
    print(f"\n{'─' * 60}")
    print(f"Testing API call logging:")

    audit_logger.log_api_call(
        service="kalshi",
        endpoint="/api/markets",
        method="GET",
        user_id=12345,
        duration_ms=150,
        status_code=200,
        success=True,
        request_size=256,
        response_size=4096,
        ip_address="192.168.1.100"
    )

    audit_logger.log_api_call(
        service="kalshi",
        endpoint="/api/orders",
        method="POST",
        user_id=12345,
        duration_ms=250,
        status_code=201,
        success=True,
        request_size=512,
        response_size=1024,
        ip_address="192.168.1.100"
    )

    # Log slow request
    audit_logger.log_api_call(
        service="kalshi",
        endpoint="/api/market-history",
        method="GET",
        user_id=12345,
        duration_ms=1250,  # Slow request (>1s)
        status_code=200,
        success=True,
        ip_address="192.168.1.100"
    )

    # Log failed request
    audit_logger.log_api_call(
        service="kalshi",
        endpoint="/api/orders",
        method="POST",
        user_id=12345,
        duration_ms=100,
        status_code=401,
        success=False,
        ip_address="192.168.1.100"
    )

    print("\n" + "=" * 60)
    print("All audit logs recorded successfully!")
    print("=" * 60)
    print(f"\n💡 In production, pass a DatabaseManager to store logs:")
    print(f"   audit_logger = AuditLogger(db_manager)")
    print(f"   This enables querying and analysis of audit trails.")
