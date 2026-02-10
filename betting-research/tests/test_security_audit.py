"""
Unit tests for Audit Logger
"""

import pytest
from datetime import datetime, timezone
from src.security.audit_logger import AuditLogger, Severity, EventType


class TestAuditLogger:
    """Tests for AuditLogger"""

    def test_logger_initialization_without_db(self):
        """Test AuditLogger initialization without database"""
        logger = AuditLogger()

        assert logger.db is None

    def test_log_security_event_basic(self):
        """Test basic security event logging"""
        logger = AuditLogger()

        # Should not raise exception (logs to console)
        logger.log_security_event(
            severity=Severity.INFO,
            event_type=EventType.LOGIN_SUCCESS,
            user_id=12345,
            details="User logged in successfully",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0"
        )

    def test_log_security_event_all_severities(self):
        """Test logging security events with all severity levels"""
        logger = AuditLogger()

        for severity in Severity:
            logger.log_security_event(
                severity=severity,
                event_type=EventType.LOGIN_SUCCESS,
                user_id=12345,
                details=f"Test event with severity: {severity.value}"
            )

    def test_log_security_event_all_types(self):
        """Test logging security events with all event types"""
        logger = AuditLogger()

        for event_type in EventType:
            logger.log_security_event(
                severity=Severity.INFO,
                event_type=event_type,
                user_id=12345,
                details=f"Test event type: {event_type.value}"
            )

    def test_log_security_event_without_user(self):
        """Test logging security event without user ID"""
        logger = AuditLogger()

        logger.log_security_event(
            severity=Severity.HIGH,
            event_type=EventType.LOGIN_FAILURE,
            user_id=None,
            details="Failed login attempt",
            ip_address="192.168.1.200"
        )

    def test_log_security_event_minimal(self):
        """Test logging minimal security event"""
        logger = AuditLogger()

        logger.log_security_event(
            severity=Severity.INFO,
            event_type=EventType.LOGIN_SUCCESS
        )

    def test_log_trade_basic(self):
        """Test basic trade logging"""
        logger = AuditLogger()

        logger.log_trade(
            trade_id="trade_12345",
            action="BUY",
            amount=100.0,
            market_type="nfl_superbowl",
            market_id="market_kc_vs_phi",
            user_id=12345,
            status="PENDING"
        )

    def test_log_trade_minimal(self):
        """Test logging minimal trade"""
        logger = AuditLogger()

        logger.log_trade(
            action="BUY",
            amount=100.0
        )

    def test_log_trade_all_actions(self):
        """Test logging trades with different actions"""
        logger = AuditLogger()

        for action in ["BUY", "SELL", "CANCEL"]:
            logger.log_trade(
                trade_id=f"trade_{action}",
                action=action,
                amount=100.0,
                market_type="nfl_superbowl",
                user_id=12345,
                status="PENDING"
            )

    def test_log_api_call_basic(self):
        """Test basic API call logging"""
        logger = AuditLogger()

        logger.log_api_call(
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

    def test_log_api_call_minimal(self):
        """Test logging minimal API call"""
        logger = AuditLogger()

        logger.log_api_call(
            service="kalshi",
            endpoint="/api/markets"
        )

    def test_log_api_call_slow_request(self):
        """Test logging slow API request (>1s)"""
        logger = AuditLogger()

        logger.log_api_call(
            service="kalshi",
            endpoint="/api/market-history",
            method="GET",
            user_id=12345,
            duration_ms=1250,  # Slow request
            status_code=200,
            success=True
        )

    def test_log_api_call_failed_request(self):
        """Test logging failed API request"""
        logger = AuditLogger()

        logger.log_api_call(
            service="kalshi",
            endpoint="/api/orders",
            method="POST",
            user_id=12345,
            duration_ms=100,
            status_code=401,
            success=False
        )

    def test_log_api_call_all_methods(self):
        """Test logging API calls with different HTTP methods"""
        logger = AuditLogger()

        for method in ["GET", "POST", "PUT", "DELETE"]:
            logger.log_api_call(
                service="kalshi",
                endpoint="/api/test",
                method=method,
                user_id=12345,
                duration_ms=100,
                status_code=200,
                success=True
            )

    def test_get_security_events_without_db(self):
        """Test getting security events without database"""
        logger = AuditLogger()

        events = logger.get_security_events()

        # Should return empty list (no database)
        assert events == []

    def test_get_trade_audit_without_db(self):
        """Test getting trade audit without database"""
        logger = AuditLogger()

        trades = logger.get_trade_audit()

        # Should return empty list (no database)
        assert trades == []

    def test_get_api_logs_without_db(self):
        """Test getting API logs without database"""
        logger = AuditLogger()

        logs = logger.get_api_logs()

        # Should return empty list (no database)
        assert logs == []

    def test_get_security_events_with_filters_without_db(self):
        """Test getting filtered security events without database"""
        logger = AuditLogger()

        # Log some events first
        logger.log_security_event(
            severity=Severity.HIGH,
            event_type=EventType.LOGIN_FAILURE,
            user_id=12345
        )

        logger.log_security_event(
            severity=Severity.INFO,
            event_type=EventType.LOGIN_SUCCESS,
            user_id=67890
        )

        # Get filtered events
        events = logger.get_security_events(user_id=12345)
        assert events == []

        events = logger.get_security_events(severity=Severity.HIGH)
        assert events == []

        events = logger.get_security_events(event_type=EventType.LOGIN_SUCCESS)
        assert events == []


class TestSeverityEnum:
    """Tests for Severity enum"""

    def test_severity_values(self):
        """Test severity enum values"""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
        assert Severity.INFO.value == "info"

    def test_severity_iteration(self):
        """Test iterating over severity levels"""
        severities = list(Severity)

        assert len(severities) == 5
        assert Severity.CRITICAL in severities
        assert Severity.INFO in severities


class TestEventTypeEnum:
    """Tests for EventType enum"""

    def test_event_type_values(self):
        """Test event type enum values"""
        assert EventType.LOGIN_SUCCESS.value == "login_success"
        assert EventType.LOGIN_FAILURE.value == "login_failure"
        assert EventType.TOKEN_ISSUED.value == "token_issued"

    def test_event_type_iteration(self):
        """Test iterating over event types"""
        event_types = list(EventType)

        assert len(event_types) > 10
        assert EventType.LOGIN_SUCCESS in event_types
        assert EventType.SECURITY_ALERT in event_types

    def test_event_type_categories(self):
        """Test event type categories exist"""
        # Login/logout events
        assert EventType.LOGIN_SUCCESS in EventType
        assert EventType.LOGIN_FAILURE in EventType
        assert EventType.LOGOUT in EventType

        # Token events
        assert EventType.TOKEN_ISSUED in EventType
        assert EventType.TOKEN_REFRESHED in EventType
        assert EventType.TOKEN_INVALIDATED in EventType

        # Security events
        assert EventType.RATE_LIMIT_EXCEEDED in EventType
        assert EventType.PERMISSION_DENIED in EventType
        assert EventType.SECURITY_ALERT in EventType
