"""
Rate Limiter

Implements rate limiting to prevent abuse and protect against DoS attacks.
Supports per-user and per-IP rate limiting with configurable windows.

Reference: Token bucket algorithm
"""

import time
import threading
import logging
from typing import Dict, List, Optional
from collections import defaultdict
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RequestRecord:
    """Record of a single request for rate limiting"""
    timestamp: float
    ip_address: str


class RateLimiter:
    """
    Rate limiter using sliding window algorithm

    Tracks requests per user/IP and enforces configurable limits.
    Thread-safe for concurrent access.
    """

    # Default configuration
    DEFAULT_MAX_REQUESTS = 60  # Requests per window
    DEFAULT_WINDOW_SECONDS = 60  # 1 minute window

    def __init__(self,
                 max_requests_per_window: int = None,
                 window_seconds: int = None):
        """
        Initialize rate limiter

        Args:
            max_requests_per_window: Maximum requests allowed per window (default: 60)
            window_seconds: Time window in seconds (default: 60)
        """
        self.max_requests = max_requests_per_window or self.DEFAULT_MAX_REQUESTS
        self.window = window_seconds or self.DEFAULT_WINDOW_SECONDS

        # Thread-safe storage for request records
        self.requests: Dict[str, List[RequestRecord]] = defaultdict(list)
        self.lock = threading.Lock()

        logger.info(f"RateLimiter initialized (max_requests={self.max_requests}, "
                   f"window={self.window}s)")

    def _cleanup_old_requests(self, identifier: str, now: float):
        """
        Remove requests outside the current time window

        Args:
            identifier: User ID or IP address
            now: Current timestamp
        """
        cutoff_time = now - self.window

        # Keep only requests within window
        self.requests[identifier] = [
            req for req in self.requests[identifier]
            if req.timestamp > cutoff_time
        ]

    def is_allowed(self,
                   user_id: Optional[int] = None,
                   ip_address: Optional[str] = None) -> bool:
        """
        Check if request is allowed (not rate limited)

        Prioritizes user_id over ip_address for tracking.

        Args:
            user_id: User ID (preferred for tracking)
            ip_address: IP address (fallback if user_id not provided)

        Returns:
            True if request is allowed, False if rate limited
        """
        if user_id is None and ip_address is None:
            logger.warning("is_allowed() called without user_id or ip_address")
            return False

        # Use user_id if available, else ip_address
        identifier = str(user_id) if user_id is not None else ip_address
        now = time.time()

        with self.lock:
            # Clean old requests
            self._cleanup_old_requests(identifier, now)

            # Check rate limit
            if len(self.requests[identifier]) < self.max_requests:
                # Request allowed
                logger.debug(f"Request allowed for {identifier} "
                           f"({len(self.requests[identifier])}/{self.max_requests})")
                return True
            else:
                # Rate limited
                logger.warning(f"Rate limit exceeded for {identifier} "
                            f"({len(self.requests[identifier])}/{self.max_requests})")
                return False

    def record_request(self,
                      user_id: Optional[int] = None,
                      ip_address: Optional[str] = None):
        """
        Record a request for rate limiting

        Should be called after is_allowed() returns True.

        Args:
            user_id: User ID (preferred for tracking)
            ip_address: IP address (fallback if user_id not provided)
        """
        if user_id is None and ip_address is None:
            return

        identifier = str(user_id) if user_id is not None else ip_address
        now = time.time()

        with self.lock:
            self.requests[identifier].append(
                RequestRecord(timestamp=now, ip_address=ip_address or "unknown")
            )
            logger.debug(f"Request recorded for {identifier}")

    def get_remaining_requests(self,
                              user_id: Optional[int] = None,
                              ip_address: Optional[str] = None) -> int:
        """
        Get number of remaining requests before rate limit is hit

        Args:
            user_id: User ID (preferred)
            ip_address: IP address (fallback)

        Returns:
            Number of remaining requests (0 if rate limited)
        """
        if user_id is None and ip_address is None:
            return 0

        identifier = str(user_id) if user_id is not None else ip_address
        now = time.time()

        with self.lock:
            self._cleanup_old_requests(identifier, now)
            used = len(self.requests[identifier])
            remaining = max(0, self.max_requests - used)
            return remaining

    def get_reset_time(self,
                     user_id: Optional[int] = None,
                     ip_address: Optional[str] = None) -> Optional[float]:
        """
        Get timestamp when rate limit window will reset

        Args:
            user_id: User ID (preferred)
            ip_address: IP address (fallback)

        Returns:
            Unix timestamp of window reset time, or None if no requests in window
        """
        if user_id is None and ip_address is None:
            return None

        identifier = str(user_id) if user_id is not None else ip_address
        now = time.time()

        with self.lock:
            self._cleanup_old_requests(identifier, now)

            if not self.requests[identifier]:
                return None

            # Reset time is when oldest request + window
            oldest = min(req.timestamp for req in self.requests[identifier])
            return oldest + self.window

    def reset(self,
             user_id: Optional[int] = None,
             ip_address: Optional[str] = None):
        """
        Reset rate limit for a user/IP

        Use with caution - typically only for admin purposes or testing.

        Args:
            user_id: User ID to reset
            ip_address: IP address to reset
        """
        if user_id is None and ip_address is None:
            return

        identifier = str(user_id) if user_id is not None else ip_address

        with self.lock:
            if identifier in self.requests:
                del self.requests[identifier]
                logger.info(f"Rate limit reset for {identifier}")

    def get_stats(self, identifier: str) -> Dict:
        """
        Get rate limiting statistics for a user/IP

        Args:
            identifier: User ID or IP address

        Returns:
            Dictionary with statistics
        """
        now = time.time()

        with self.lock:
            self._cleanup_old_requests(identifier, now)
            requests = self.requests.get(identifier, [])

            if not requests:
                return {
                    'identifier': identifier,
                    'requests_in_window': 0,
                    'max_requests': self.max_requests,
                    'remaining': self.max_requests,
                    'reset_time': None
                }

            oldest = min(req.timestamp for req in requests)
            reset_time = oldest + self.window

            return {
                'identifier': identifier,
                'requests_in_window': len(requests),
                'max_requests': self.max_requests,
                'remaining': max(0, self.max_requests - len(requests)),
                'reset_time': reset_time,
                'reset_in_seconds': max(0, reset_time - now)
            }

    def clear_all(self):
        """
        Clear all rate limiting records

        Use with caution - typically only for testing or emergency situations.
        """
        with self.lock:
            self.requests.clear()
            logger.warning("All rate limiting records cleared")


# Singleton instance for convenient access
_default_rate_limiter = None


def get_rate_limiter(max_requests: int = None, window_seconds: int = None) -> RateLimiter:
    """
    Get the default RateLimiter instance

    Args:
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds

    Returns:
        RateLimiter instance
    """
    global _default_rate_limiter
    if _default_rate_limiter is None:
        _default_rate_limiter = RateLimiter(max_requests, window_seconds)
    return _default_rate_limiter


# Decorator for rate limiting functions
def rate_limit(max_requests: int = None, window_seconds: int = None):
    """
    Decorator to rate limit a function based on first argument (user_id)

    Args:
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds
    """
    limiter = RateLimiter(max_requests, window_seconds)

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Assume first argument is user_id or can be derived
            user_id = kwargs.get('user_id') or (args[0] if args else None)

            if not limiter.is_allowed(user_id=user_id):
                logger.warning(f"Rate limit exceeded for function {func.__name__}")
                raise Exception(f"Rate limit exceeded (try again later)")

            limiter.record_request(user_id=user_id)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Rate Limiter Example")
    print("=" * 60)

    # Initialize rate limiter: 5 requests per 10 seconds
    limiter = RateLimiter(max_requests_per_window=5, window_seconds=10)

    print(f"\n✓ RateLimiter initialized (max_requests=5, window=10s)")

    # Test rate limiting
    user_id = 12345
    ip_address = "192.168.1.100"

    print(f"\n{'─' * 60}")
    print(f"Testing rate limiting for user_id={user_id}:")

    # Make requests
    for i in range(8):
        is_allowed = limiter.is_allowed(user_id=user_id, ip_address=ip_address)

        if is_allowed:
            limiter.record_request(user_id=user_id, ip_address=ip_address)
            print(f"  Request {i+1}: ✅ ALLOWED")
        else:
            print(f"  Request {i+1}: ❌ RATE LIMITED")

        remaining = limiter.get_remaining_requests(user_id=user_id)
        print(f"    Remaining: {remaining}/{limiter.max_requests}")

    # Get statistics
    print(f"\n{'─' * 60}")
    print(f"Rate limit statistics:")
    stats = limiter.get_stats(str(user_id))
    print(f"  Requests in window: {stats['requests_in_window']}")
    print(f"  Max requests: {stats['max_requests']}")
    print(f"  Remaining: {stats['remaining']}")
    print(f"  Reset in: {stats['reset_in_seconds']:.1f}s")

    # Test per-IP rate limiting
    print(f"\n{'─' * 60}")
    print(f"Testing per-IP rate limiting for {ip_address}:")

    ip_limiter = RateLimiter(max_requests_per_window=3, window_seconds=10)

    for i in range(5):
        is_allowed = ip_limiter.is_allowed(ip_address=ip_address)

        if is_allowed:
            ip_limiter.record_request(ip_address=ip_address)
            print(f"  Request {i+1}: ✅ ALLOWED")
        else:
            print(f"  Request {i+1}: ❌ RATE LIMITED")

    # Test rate limit decorator
    print(f"\n{'─' * 60}")
    print(f"Testing rate_limit decorator:")

    @rate_limit(max_requests=3, window_seconds=10)
    def my_function(user_id: int):
        return f"Function executed for user {user_id}"

    for i in range(5):
        try:
            result = my_function(user_id=99999)
            print(f"  Call {i+1}: ✅ {result}")
        except Exception as e:
            print(f"  Call {i+1}: ❌ {e}")

    # Wait for window to reset
    print(f"\n{'─' * 60}")
    print(f"Waiting 11s for rate limit to reset...")

    import time as t
    t.sleep(11)

    # Test after window reset
    print(f"\n{'─' * 60}")
    print(f"Testing after window reset:")

    is_allowed = limiter.is_allowed(user_id=user_id)
    if is_allowed:
        limiter.record_request(user_id=user_id)
        print(f"  Request: ✅ ALLOWED (window reset)")
    else:
        print(f"  Request: ❌ RATE LIMITED")

    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
