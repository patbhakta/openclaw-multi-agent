"""
Unit tests for Rate Limiter
"""

import pytest
import time
from src.security.rate_limiter import (
    RateLimiter,
    get_rate_limiter,
    rate_limit,
    RequestRecord
)


class TestRateLimiter:
    """Tests for rate limiting functionality"""

    def test_initialization(self):
        """Test RateLimiter initializes with default values"""
        limiter = RateLimiter()

        assert limiter.max_requests == 60
        assert limiter.window == 60
        assert len(limiter.requests) == 0

    def test_custom_parameters(self):
        """Test RateLimiter with custom parameters"""
        limiter = RateLimiter(max_requests_per_window=10, window_seconds=30)

        assert limiter.max_requests == 10
        assert limiter.window == 30

    def test_is_allowed_first_request(self):
        """Test first request is always allowed"""
        limiter = RateLimiter(max_requests_per_window=5, window_seconds=10)

        is_allowed = limiter.is_allowed(user_id=12345)

        assert is_allowed is True

    def test_is_allowed_within_limit(self):
        """Test requests within limit are allowed"""
        limiter = RateLimiter(max_requests_per_window=5, window_seconds=10)
        user_id = 12345

        for i in range(5):
            is_allowed = limiter.is_allowed(user_id=user_id)
            assert is_allowed is True, f"Request {i+1} should be allowed"
            limiter.record_request(user_id=user_id)

    def test_is_allowed_exceeds_limit(self):
        """Test requests exceeding limit are denied"""
        limiter = RateLimiter(max_requests_per_window=3, window_seconds=10)
        user_id = 12345

        # Allow first 3 requests
        for i in range(3):
            limiter.is_allowed(user_id=user_id)
            limiter.record_request(user_id=user_id)

        # 4th request should be denied
        is_allowed = limiter.is_allowed(user_id=user_id)
        assert is_allowed is False

    def test_per_user_rate_limiting(self):
        """Test rate limiting works per user"""
        limiter = RateLimiter(max_requests_per_window=2, window_seconds=10)

        # User 1 makes 2 requests
        limiter.is_allowed(user_id=1)
        limiter.record_request(user_id=1)
        limiter.is_allowed(user_id=1)
        limiter.record_request(user_id=1)

        # User 1 should be rate limited
        assert limiter.is_allowed(user_id=1) is False

        # User 2 should still be allowed (separate limit)
        assert limiter.is_allowed(user_id=2) is True

    def test_per_ip_rate_limiting(self):
        """Test rate limiting works per IP address"""
        limiter = RateLimiter(max_requests_per_window=2, window_seconds=10)

        # IP 1 makes 2 requests
        limiter.is_allowed(ip_address="192.168.1.1")
        limiter.record_request(ip_address="192.168.1.1")
        limiter.is_allowed(ip_address="192.168.1.1")
        limiter.record_request(ip_address="192.168.1.1")

        # IP 1 should be rate limited
        assert limiter.is_allowed(ip_address="192.168.1.1") is False

        # IP 2 should still be allowed (separate limit)
        assert limiter.is_allowed(ip_address="192.168.1.2") is True

    def test_user_id_priority_over_ip(self):
        """Test that user_id takes priority over ip_address"""
        limiter = RateLimiter(max_requests_per_window=2, window_seconds=10)

        # User 1 from IP 1 makes 2 requests
        limiter.is_allowed(user_id=1, ip_address="192.168.1.1")
        limiter.record_request(user_id=1, ip_address="192.168.1.1")
        limiter.is_allowed(user_id=1, ip_address="192.168.1.1")
        limiter.record_request(user_id=1, ip_address="192.168.1.1")

        # User 1 should be rate limited (tracked by user_id)
        assert limiter.is_allowed(user_id=1, ip_address="192.168.1.1") is False

        # IP 1 with user_id=2 should be allowed (different user)
        assert limiter.is_allowed(user_id=2, ip_address="192.168.1.1") is True

    def test_get_remaining_requests(self):
        """Test getting remaining requests"""
        limiter = RateLimiter(max_requests_per_window=5, window_seconds=10)
        user_id = 12345

        # Initially should have all requests available
        remaining = limiter.get_remaining_requests(user_id=user_id)
        assert remaining == 5

        # After 2 requests, should have 3 remaining
        limiter.is_allowed(user_id=user_id)
        limiter.record_request(user_id=user_id)
        limiter.is_allowed(user_id=user_id)
        limiter.record_request(user_id=user_id)

        remaining = limiter.get_remaining_requests(user_id=user_id)
        assert remaining == 3

        # After using all, should have 0 remaining
        for i in range(3):
            limiter.is_allowed(user_id=user_id)
            limiter.record_request(user_id=user_id)

        remaining = limiter.get_remaining_requests(user_id=user_id)
        assert remaining == 0

    def test_get_reset_time(self):
        """Test getting reset time for rate limit window"""
        limiter = RateLimiter(max_requests_per_window=3, window_seconds=10)
        user_id = 12345

        # No requests yet, reset time should be None
        reset_time = limiter.get_reset_time(user_id=user_id)
        assert reset_time is None

        # After making requests, reset time should be set
        limiter.is_allowed(user_id=user_id)
        limiter.record_request(user_id=user_id)
        now = time.time()
        reset_time = limiter.get_reset_time(user_id=user_id)

        # Reset time should be ~10 seconds from now
        assert reset_time is not None
        assert reset_time > now
        assert reset_time <= now + limiter.window

    def test_window_reset_after_expiry(self):
        """Test that rate limit resets after window expires"""
        limiter = RateLimiter(max_requests_per_window=3, window_seconds=2)
        user_id = 12345

        # Use all requests
        for i in range(3):
            limiter.is_allowed(user_id=user_id)
            limiter.record_request(user_id=user_id)

        # Should be rate limited
        assert limiter.is_allowed(user_id=user_id) is False

        # Wait for window to expire
        time.sleep(3)

        # Should be allowed again
        assert limiter.is_allowed(user_id=user_id) is True

    def test_reset_user_limit(self):
        """Test resetting rate limit for a specific user"""
        limiter = RateLimiter(max_requests_per_window=3, window_seconds=10)

        # User 1 makes 3 requests
        limiter.is_allowed(user_id=1)
        limiter.record_request(user_id=1)
        limiter.is_allowed(user_id=1)
        limiter.record_request(user_id=1)
        limiter.is_allowed(user_id=1)
        limiter.record_request(user_id=1)

        # User 1 should be rate limited
        assert limiter.is_allowed(user_id=1) is False

        # Reset user 1's limit
        limiter.reset(user_id=1)

        # User 1 should now be allowed again
        assert limiter.is_allowed(user_id=1) is True

    def test_reset_ip_limit(self):
        """Test resetting rate limit for a specific IP"""
        limiter = RateLimiter(max_requests_per_window=3, window_seconds=10)
        ip = "192.168.1.1"

        # IP makes 3 requests
        limiter.is_allowed(ip_address=ip)
        limiter.record_request(ip_address=ip)
        limiter.is_allowed(ip_address=ip)
        limiter.record_request(ip_address=ip)
        limiter.is_allowed(ip_address=ip)
        limiter.record_request(ip_address=ip)

        # IP should be rate limited
        assert limiter.is_allowed(ip_address=ip) is False

        # Reset IP's limit
        limiter.reset(ip_address=ip)

        # IP should now be allowed again
        assert limiter.is_allowed(ip_address=ip) is True

    def test_get_stats(self):
        """Test getting rate limiting statistics"""
        limiter = RateLimiter(max_requests_per_window=5, window_seconds=10)
        user_id = 12345

        # Get initial stats
        stats = limiter.get_stats(str(user_id))
        assert stats['identifier'] == str(user_id)
        assert stats['requests_in_window'] == 0
        assert stats['max_requests'] == 5
        assert stats['remaining'] == 5
        assert stats['reset_time'] is None

        # Make 2 requests
        limiter.is_allowed(user_id=user_id)
        limiter.record_request(user_id=user_id)
        limiter.is_allowed(user_id=user_id)
        limiter.record_request(user_id=user_id)

        # Get updated stats
        stats = limiter.get_stats(str(user_id))
        assert stats['requests_in_window'] == 2
        assert stats['remaining'] == 3
        assert stats['reset_time'] is not None
        assert stats['reset_in_seconds'] > 0

    def test_clear_all(self):
        """Test clearing all rate limiting records"""
        limiter = RateLimiter(max_requests_per_window=3, window_seconds=10)

        # Make requests for multiple users
        for user_id in [1, 2, 3]:
            limiter.is_allowed(user_id=user_id)
            limiter.record_request(user_id=user_id)

        # All should have requests
        assert len(limiter.requests) == 3

        # Clear all
        limiter.clear_all()

        # All records should be gone
        assert len(limiter.requests) == 0

        # All users should be allowed again
        for user_id in [1, 2, 3]:
            assert limiter.is_allowed(user_id=user_id) is True

    def test_record_request_without_check(self):
        """Test that recording without check works"""
        limiter = RateLimiter(max_requests_per_window=3, window_seconds=10)
        user_id = 12345

        # Record request without checking first
        limiter.record_request(user_id=user_id)

        # Should show as having 1 request
        remaining = limiter.get_remaining_requests(user_id=user_id)
        assert remaining == 2

    def test_request_without_identifier(self):
        """Test that request without user_id or ip_address returns False"""
        limiter = RateLimiter()

        is_allowed = limiter.is_allowed()
        assert is_allowed is False

    def test_cleanup_old_requests(self):
        """Test that old requests are cleaned up"""
        limiter = RateLimiter(max_requests_per_window=3, window_seconds=2)
        user_id = 12345

        # Make 3 requests
        for i in range(3):
            limiter.is_allowed(user_id=user_id)
            limiter.record_request(user_id=user_id)

        # Should be rate limited
        assert limiter.is_allowed(user_id=user_id) is False

        # Wait for window to expire
        time.sleep(3)

        # Should be allowed again (old requests cleaned up)
        assert limiter.is_allowed(user_id=user_id) is True


class TestRateLimiterDecorator:
    """Tests for rate_limit decorator"""

    def test_decorator_allows_requests(self):
        """Test decorator allows requests within limit"""
        calls = []

        @rate_limit(max_requests=3, window_seconds=10)
        def my_function(user_id: int):
            calls.append(user_id)
            return f"Function executed for user {user_id}"

        # Should allow 3 calls
        for i in range(3):
            result = my_function(user_id=12345)
            assert result == "Function executed for user 12345"

        assert len(calls) == 3

    def test_decorator_rate_limits(self):
        """Test decorator denies requests exceeding limit"""
        @rate_limit(max_requests=2, window_seconds=10)
        def my_function(user_id: int):
            return f"Function executed for user {user_id}"

        # Should allow 2 calls
        my_function(user_id=12345)
        my_function(user_id=12345)

        # 3rd call should raise exception
        with pytest.raises(Exception, match="Rate limit exceeded"):
            my_function(user_id=12345)

    def test_decorator_separate_per_user(self):
        """Test decorator limits separately per user"""
        @rate_limit(max_requests=2, window_seconds=10)
        def my_function(user_id: int):
            return f"Function executed for user {user_id}"

        # User 1 makes 2 calls
        my_function(user_id=1)
        my_function(user_id=1)

        # User 1 should be rate limited
        with pytest.raises(Exception):
            my_function(user_id=1)

        # User 2 should still be allowed
        result = my_function(user_id=2)
        assert "Function executed for user 2" in result


class TestSingleton:
    """Tests for singleton pattern"""

    def test_get_rate_limiter_singleton(self):
        """Test that get_rate_limiter returns same instance"""
        limiter1 = get_rate_limiter(max_requests=10, window_seconds=30)
        limiter2 = get_rate_limiter()

        # Should be same instance (parameters only used on first call)
        assert limiter1 is limiter2
        assert limiter1.max_requests == 10
        assert limiter1.window == 30


class TestRequestRecord:
    """Tests for RequestRecord dataclass"""

    def test_request_record_creation(self):
        """Test RequestRecord creation"""
        now = time.time()
        record = RequestRecord(timestamp=now, ip_address="192.168.1.1")

        assert record.timestamp == now
        assert record.ip_address == "192.168.1.1"
