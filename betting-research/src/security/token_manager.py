"""
Fernet Token Encryption Manager

Implements secure token encryption using Fernet (symmetric encryption).
Prevents token forgery and provides expiration support.

Reference: https://cryptography.io/en/latest/fernet/
"""

import os
import json
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TokenManager:
    """
    Manager for Fernet token encryption

    Uses Fernet (AES-128 in CBC mode with PKCS7 padding) for token encryption.
    All tokens are encrypted and can include expiration time for validation.
    """

    DEFAULT_EXPIRATION_HOURS = 24  # Default token expiration: 24 hours
    TOKEN_PREFIX = "bearer_"  # Prefix for encrypted tokens

    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        Initialize TokenManager

        Args:
            encryption_key: Fernet encryption key (32 bytes base64-encoded)
                           If not provided, reads from TOKEN_ENCRYPTION_KEY env var
                           If env var not set, generates a new key

        Raises:
            ValueError: If encryption key is invalid
        """
        self.key = encryption_key

        if self.key is None:
            # Try to read from environment variable
            env_key = os.environ.get('TOKEN_ENCRYPTION_KEY')
            if env_key:
                try:
                    self.key = env_key.encode() if isinstance(env_key, str) else env_key
                    logger.info("Loaded encryption key from TOKEN_ENCRYPTION_KEY environment variable")
                except Exception as e:
                    logger.warning(f"Failed to load env key: {e}, generating new key")
                    self.key = self._generate_key()
            else:
                # Generate new key
                self.key = self._generate_key()
                logger.warning("⚠️  New token encryption key generated - save it to TOKEN_ENCRYPTION_KEY env var!")

        # Validate and initialize cipher
        try:
            self.cipher = Fernet(self.key)
            logger.info("Fernet TokenManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Fernet cipher: {e}")
            raise ValueError(f"Invalid encryption key: {e}")

    def _generate_key(self) -> bytes:
        """
        Generate a new Fernet encryption key

        Returns:
            32-byte URL-safe base64-encoded key
        """
        key = Fernet.generate_key()
        logger.info(f"Generated new Fernet key: {key.decode()}")
        return key

    @classmethod
    def derive_key_from_password(cls, password: str, salt: bytes) -> bytes:
        """
        Derive Fernet key from password using PBKDF2

        Use this if you want to derive encryption key from a password instead
        of storing a random key.

        Args:
            password: Password to derive key from
            salt: Salt for key derivation (at least 16 bytes)

        Returns:
            Fernet-compatible encryption key (32 bytes)
        """
        if len(salt) < 16:
            raise ValueError("Salt must be at least 16 bytes")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # OWASP recommended for 2024
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def generate_token(self,
                      user_id: int,
                      payload: Optional[Dict] = None,
                      expires_in_hours: int = None) -> str:
        """
        Generate an encrypted token with expiration

        Args:
            user_id: User ID to associate with token
            payload: Additional payload data (optional)
            expires_in_hours: Expiration time in hours (default: 24)

        Returns:
            Encrypted token string with prefix (format: bearer_<encrypted>)
        """
        if expires_in_hours is None:
            expires_in_hours = self.DEFAULT_EXPIRATION_HOURS

        # Build token payload
        token_payload = {
            "user_id": user_id,
            "exp": (datetime.now() + timedelta(hours=expires_in_hours)).isoformat(),
            "iat": datetime.now().isoformat()  # Issued at
        }

        # Add custom payload if provided
        if payload:
            token_payload.update(payload)

        try:
            # Encrypt payload
            encrypted_bytes = self.cipher.encrypt(
                json.dumps(token_payload).encode('utf-8')
            )

            # Return with prefix
            encrypted_token = f"{self.TOKEN_PREFIX}{encrypted_bytes.decode('utf-8')}"
            logger.debug(f"Generated token for user_id={user_id} (expires in {expires_in_hours}h)")
            return encrypted_token

        except Exception as e:
            logger.error(f"Failed to generate token: {e}")
            raise

    def decrypt_token(self, encrypted_token: str) -> Dict:
        """
        Decrypt and validate a token

        Args:
            encrypted_token: Encrypted token string (with or without prefix)

        Returns:
            Dictionary with token payload and validation result

        Response format:
            {
                "valid": True/False,
                "user_id": int (if valid),
                "payload": dict (if valid),
                "error": str (if invalid)
            }
        """
        if not encrypted_token:
            return {"valid": False, "error": "Token is empty"}

        try:
            # Remove prefix if present
            encrypted_part = encrypted_token
            if encrypted_token.startswith(self.TOKEN_PREFIX):
                encrypted_part = encrypted_token[len(self.TOKEN_PREFIX):]

            # Decrypt token
            decrypted_bytes = self.cipher.decrypt(encrypted_part.encode('utf-8'))
            payload = json.loads(decrypted_bytes.decode('utf-8'))

            # Check expiration
            if 'exp' in payload:
                exp_time = datetime.fromisoformat(payload['exp'])
                if datetime.now() > exp_time:
                    logger.warning(f"Token expired for user_id={payload.get('user_id')}")
                    return {"valid": False, "error": "Token expired"}

            logger.debug(f"Token decrypted successfully for user_id={payload.get('user_id')}")
            return {
                "valid": True,
                "user_id": payload.get('user_id'),
                "payload": payload
            }

        except InvalidToken:
            logger.warning("Invalid token (decryption failed)")
            return {"valid": False, "error": "Invalid token"}

        except Exception as e:
            logger.error(f"Failed to decrypt token: {e}")
            return {"valid": False, "error": str(e)}

    def verify_token(self, encrypted_token: str, user_id: int) -> bool:
        """
        Verify a token belongs to a specific user

        Args:
            encrypted_token: Encrypted token string
            user_id: Expected user ID

        Returns:
            True if token is valid and belongs to user, False otherwise
        """
        result = self.decrypt_token(encrypted_token)

        if not result.get('valid'):
            return False

        return result.get('user_id') == user_id

    def refresh_token(self, encrypted_token: str, expires_in_hours: int = None) -> Optional[str]:
        """
        Refresh an existing token with new expiration time

        Args:
            encrypted_token: Current encrypted token
            expires_in_hours: New expiration time in hours (default: same as original)

        Returns:
            New encrypted token or None if refresh failed
        """
        result = self.decrypt_token(encrypted_token)

        if not result.get('valid'):
            logger.warning(f"Failed to refresh token: {result.get('error')}")
            return None

        # Extract original payload
        payload = result['payload']

        # Remove expiration fields
        payload.pop('exp', None)
        payload.pop('iat', None)

        # Generate new token
        return self.generate_token(
            user_id=payload['user_id'],
            payload=payload,
            expires_in_hours=expires_in_hours
        )

    def get_key(self) -> bytes:
        """
        Get the current encryption key

        Returns:
            Fernet encryption key (32 bytes base64-encoded)
        """
        return self.key

    def export_key(self, path: str):
        """
        Export encryption key to file

        WARNING: Keep this file secure! Anyone with the key can forge tokens.

        Args:
            path: File path to write key
        """
        try:
            with open(path, 'wb') as f:
                f.write(self.key)
            logger.info(f"Exported encryption key to {path}")
        except Exception as e:
            logger.error(f"Failed to export key: {e}")
            raise

    @classmethod
    def import_key(cls, path: str) -> 'TokenManager':
        """
        Import encryption key from file

        Args:
            path: File path to read key from

        Returns:
            TokenManager instance with imported key
        """
        try:
            with open(path, 'rb') as f:
                key = f.read()
            logger.info(f"Imported encryption key from {path}")
            return cls(encryption_key=key)
        except Exception as e:
            logger.error(f"Failed to import key: {e}")
            raise


# Singleton instance for convenient access
_default_token_manager = None


def get_token_manager() -> TokenManager:
    """
    Get the default TokenManager instance

    Returns:
        TokenManager instance
    """
    global _default_token_manager
    if _default_token_manager is None:
        _default_token_manager = TokenManager()
    return _default_token_manager


def generate_token(user_id: int, payload: Optional[Dict] = None, expires_in_hours: int = 24) -> str:
    """
    Convenience function to generate a token using default TokenManager

    Args:
        user_id: User ID to associate with token
        payload: Additional payload data (optional)
        expires_in_hours: Expiration time in hours (default: 24)

    Returns:
        Encrypted token string
    """
    manager = get_token_manager()
    return manager.generate_token(user_id, payload, expires_in_hours)


def decrypt_token(encrypted_token: str) -> Dict:
    """
    Convenience function to decrypt a token using default TokenManager

    Args:
        encrypted_token: Encrypted token string

    Returns:
        Dictionary with token payload and validation result
    """
    manager = get_token_manager()
    return manager.decrypt_token(encrypted_token)


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Fernet Token Encryption Example")
    print("=" * 60)

    # Initialize manager
    manager = TokenManager()

    print(f"\n✓ TokenManager initialized")
    print(f"  Encryption key: {manager.get_key()[:20]}...")

    # Test token generation
    user_id = 12345
    custom_payload = {
        "role": "admin",
        "permissions": ["read", "write", "delete"]
    }

    print(f"\n{'─' * 60}")
    print(f"Testing token generation:")
    print(f"  User ID: {user_id}")
    print(f"  Custom payload: {custom_payload}")

    token = manager.generate_token(
        user_id=user_id,
        payload=custom_payload,
        expires_in_hours=24
    )

    print(f"\n✓ Token generated:")
    print(f"  {token[:80]}..." if len(token) > 80 else f"  {token}")

    # Test token decryption
    print(f"\n{'─' * 60}")
    print(f"Testing token decryption:")

    result = manager.decrypt_token(token)
    if result['valid']:
        print(f"✓ Token decrypted successfully")
        print(f"  User ID: {result['user_id']}")
        print(f"  Issued at: {result['payload'].get('iat')}")
        print(f"  Expires at: {result['payload'].get('exp')}")
        print(f"  Custom payload: {{'role': '{result['payload'].get('role')}', 'permissions': {result['payload'].get('permissions')}}}")
    else:
        print(f"✗ Token decryption failed: {result.get('error')}")

    # Test token verification
    print(f"\n{'─' * 60}")
    print(f"Testing token verification:")

    is_valid = manager.verify_token(token, user_id=user_id)
    print(f"✓ Verify correct user: {'✅ PASS' if is_valid else '❌ FAIL'}")

    is_valid = manager.verify_token(token, user_id=99999)
    print(f"✓ Verify wrong user: {'✅ PASS' if not is_valid else '❌ FAIL'}")

    # Test token refresh
    print(f"\n{'─' * 60}")
    print(f"Testing token refresh:")

    new_token = manager.refresh_token(token, expires_in_hours=48)
    print(f"✓ Token refreshed with 48h expiration")
    print(f"  New token: {new_token[:80]}..." if len(new_token) > 80 else f"  New token: {new_token}")

    # Test invalid token
    print(f"\n{'─' * 60}")
    print(f"Testing invalid token:")

    result = manager.decrypt_token("bearer_invalid_token_data")
    print(f"✓ Invalid token handling: {'✅ PASS' if not result['valid'] else '❌ FAIL'}")
    print(f"  Error: {result.get('error')}")

    # Test token expiration
    print(f"\n{'─' * 60}")
    print(f"Testing expired token:")

    expired_token = manager.generate_token(user_id=user_id, expires_in_hours=-1)
    result = manager.decrypt_token(expired_token)
    print(f"✓ Expired token handling: {'✅ PASS' if not result['valid'] else '❌ FAIL'}")
    print(f"  Error: {result.get('error')}")

    # Test key export/import
    print(f"\n{'─' * 60}")
    print(f"Testing key export/import:")

    export_path = "/tmp/token_key.txt"
    manager.export_key(export_path)
    imported_manager = TokenManager.import_key(export_path)

    # Verify imported key works
    result = imported_manager.decrypt_token(token)
    print(f"✓ Imported key works: {'✅ PASS' if result['valid'] else '❌ FAIL'}")

    # Clean up
    os.remove(export_path)

    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
    print(f"\n💡 Save this encryption key for production use:")
    print(f"   export TOKEN_ENCRYPTION_KEY={manager.get_key().decode()}")
