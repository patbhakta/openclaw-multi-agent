"""
Security Module - Production-Grade Security Features

This module provides comprehensive security features for the betting system:

1. Argon2Manager - Password hashing using Argon2-CFFI (PHC winner)
2. TokenManager - Token encryption using Fernet
3. RateLimiter - Request rate limiting to prevent abuse
4. AuditLogger - Comprehensive audit trail logging

Usage:
    from src.security import (
        Argon2Manager,
        TokenManager,
        RateLimiter,
        AuditLogger,
        Severity,
        EventType
    )

    # Password hashing
    argon2 = Argon2Manager()
    hashed = argon2.hash_password("password123")
    is_valid = argon2.verify_password(hashed, "password123")

    # Token encryption
    token_mgr = TokenManager()
    token = token_mgr.generate_token(user_id=123, expires_in_hours=24)
    result = token_mgr.decrypt_token(token)

    # Rate limiting
    rate_limiter = RateLimiter(max_requests_per_window=60, window_seconds=60)
    if rate_limiter.is_allowed(user_id=123):
        rate_limiter.record_request(user_id=123)

    # Audit logging
    audit_logger = AuditLogger(db_manager)
    audit_logger.log_security_event(
        severity=Severity.INFO,
        event_type=EventType.LOGIN_SUCCESS,
        user_id=123,
        details="User logged in"
    )
"""

from .argon2_manager import (
    Argon2Manager,
    get_argon2_manager,
    hash_password,
    verify_password
)

from .token_manager import (
    TokenManager,
    get_token_manager,
    generate_token,
    decrypt_token
)

from .rate_limiter import (
    RateLimiter,
    get_rate_limiter,
    rate_limit
)

from .audit_logger import (
    AuditLogger,
    get_audit_logger,
    Severity,
    EventType
)

__all__ = [
    'Argon2Manager',
    'get_argon2_manager',
    'hash_password',
    'verify_password',
    'TokenManager',
    'get_token_manager',
    'generate_token',
    'decrypt_token',
    'RateLimiter',
    'get_rate_limiter',
    'rate_limit',
    'AuditLogger',
    'get_audit_logger',
    'Severity',
    'EventType'
]
