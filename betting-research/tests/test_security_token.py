"""
Unit tests for Fernet Token Encryption Manager
"""

import pytest
import os
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from src.security.token_manager import TokenManager, generate_token, decrypt_token


class TestTokenManager:
    """Tests for TokenManager"""

    def test_manager_initialization_with_key(self):
        """Test TokenManager initialization with provided key"""
        key = Fernet.generate_key()
        manager = TokenManager(encryption_key=key)

        assert manager.get_key() == key

    def test_manager_initialization_without_key(self):
        """Test TokenManager initialization without key (generates new key)"""
        manager = TokenManager()

        key = manager.get_key()
        assert isinstance(key, bytes)
        assert len(key) == 44  # Fernet key length in base64

    def test_manager_initialization_with_env_var(self):
        """Test TokenManager initialization with environment variable"""
        test_key = Fernet.generate_key()
        os.environ['TOKEN_ENCRYPTION_KEY'] = test_key.decode()

        manager = TokenManager()
        assert manager.get_key() == test_key

        # Clean up
        del os.environ['TOKEN_ENCRYPTION_KEY']

    def test_generate_token_basic(self):
        """Test basic token generation"""
        manager = TokenManager()
        user_id = 12345

        token = manager.generate_token(user_id)

        assert isinstance(token, str)
        assert token.startswith("bearer_")

    def test_generate_token_with_payload(self):
        """Test token generation with custom payload"""
        manager = TokenManager()
        user_id = 12345
        payload = {"role": "admin", "permissions": ["read", "write"]}

        token = manager.generate_token(user_id, payload=payload)

        assert isinstance(token, str)
        assert token.startswith("bearer_")

    def test_generate_token_with_expiration(self):
        """Test token generation with custom expiration"""
        manager = TokenManager()
        user_id = 12345

        token = manager.generate_token(user_id, expires_in_hours=48)

        assert isinstance(token, str)
        assert token.startswith("bearer_")

    def test_decrypt_token_valid(self):
        """Test decrypting a valid token"""
        manager = TokenManager()
        user_id = 12345

        token = manager.generate_token(user_id)
        result = manager.decrypt_token(token)

        assert result['valid'] is True
        assert result['user_id'] == user_id
        assert 'payload' in result
        assert 'exp' in result['payload']
        assert 'iat' in result['payload']

    def test_decrypt_token_empty(self):
        """Test decrypting empty token"""
        manager = TokenManager()

        result = manager.decrypt_token("")

        assert result['valid'] is False
        assert 'error' in result

    def test_decrypt_token_invalid(self):
        """Test decrypting invalid token"""
        manager = TokenManager()

        result = manager.decrypt_token("bearer_invalid_token_data")

        assert result['valid'] is False
        assert 'error' in result

    def test_verify_token_correct_user(self):
        """Test token verification with correct user"""
        manager = TokenManager()
        user_id = 12345

        token = manager.generate_token(user_id)
        is_valid = manager.verify_token(token, user_id)

        assert is_valid is True

    def test_verify_token_wrong_user(self):
        """Test token verification with wrong user"""
        manager = TokenManager()
        user_id = 12345

        token = manager.generate_token(user_id)
        is_valid = manager.verify_token(token, 99999)

        assert is_valid is False

    def test_verify_token_invalid(self):
        """Test token verification with invalid token"""
        manager = TokenManager()
        user_id = 12345

        is_valid = manager.verify_token("invalid_token", user_id)

        assert is_valid is False

    def test_token_expiration(self):
        """Test expired token validation"""
        manager = TokenManager()
        user_id = 12345

        # Generate token with negative expiration (already expired)
        token = manager.generate_token(user_id, expires_in_hours=-1)
        result = manager.decrypt_token(token)

        assert result['valid'] is False
        assert 'expired' in result['error'].lower()

    def test_token_refresh(self):
        """Test token refresh with new expiration"""
        manager = TokenManager()
        user_id = 12345

        original_token = manager.generate_token(user_id, expires_in_hours=1)
        new_token = manager.refresh_token(original_token, expires_in_hours=48)

        assert isinstance(new_token, str)
        assert new_token.startswith("bearer_")

        # Verify new token
        result = manager.decrypt_token(new_token)
        assert result['valid'] is True
        assert result['user_id'] == user_id

    def test_token_refresh_invalid_token(self):
        """Test token refresh with invalid token"""
        manager = TokenManager()

        new_token = manager.refresh_token("invalid_token")

        assert new_token is None

    def test_token_preserves_custom_payload(self):
        """Test that token preserves custom payload on refresh"""
        manager = TokenManager()
        user_id = 12345
        custom_payload = {"role": "admin", "permissions": ["read", "write"]}

        original_token = manager.generate_token(user_id, payload=custom_payload)
        new_token = manager.refresh_token(original_token)

        # Verify payload is preserved
        result = manager.decrypt_token(new_token)
        assert result['valid'] is True
        assert result['payload']['role'] == "admin"
        assert result['payload']['permissions'] == ["read", "write"]

    def test_export_import_key(self, tmp_path):
        """Test key export and import"""
        manager1 = TokenManager()
        key = manager1.get_key()

        # Export key
        key_path = tmp_path / "token_key.txt"
        manager1.export_key(str(key_path))

        # Import key into new manager
        manager2 = TokenManager.import_key(str(key_path))

        # Verify keys match
        assert manager2.get_key() == key

        # Test that manager2 can decrypt manager1's tokens
        token = manager1.generate_token(12345)
        result = manager2.decrypt_token(token)
        assert result['valid'] is True


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_generate_token_function(self):
        """Test convenience generate_token function"""
        user_id = 12345

        token = generate_token(user_id)

        assert isinstance(token, str)
        assert token.startswith("bearer_")

    def test_decrypt_token_function(self):
        """Test convenience decrypt_token function"""
        user_id = 12345

        token = generate_token(user_id)
        result = decrypt_token(token)

        assert result['valid'] is True
        assert result['user_id'] == user_id

    def test_functions_use_same_manager(self):
        """Test that convenience functions use the same manager instance"""
        user_id = 12345

        token1 = generate_token(user_id)
        result1 = decrypt_token(token1)

        assert result1['valid'] is True
        assert result1['user_id'] == user_id


class TestKeyDerivation:
    """Tests for key derivation from password"""

    def test_derive_key_from_password(self):
        """Test deriving key from password"""
        password = "MySecurePassword"
        salt = b"salt_16_bytes_long"

        key = TokenManager.derive_key_from_password(password, salt)

        assert isinstance(key, bytes)
        assert len(key) == 44  # Fernet key length in base64

    def test_derived_key_works_with_manager(self):
        """Test that derived key works with TokenManager"""
        password = "MySecurePassword"
        salt = b"salt_16_bytes_long"

        key = TokenManager.derive_key_from_password(password, salt)
        manager = TokenManager(encryption_key=key)

        # Test token generation/decryption
        token = manager.generate_token(12345)
        result = manager.decrypt_token(token)

        assert result['valid'] is True

    def test_derive_key_short_salt(self):
        """Test that short salt raises error"""
        password = "MySecurePassword"
        short_salt = b"short"

        with pytest.raises(ValueError, match="Salt must be at least 16 bytes"):
            TokenManager.derive_key_from_password(password, short_salt)

    def test_same_password_same_salt_same_key(self):
        """Test that same password + salt produces same key"""
        password = "MySecurePassword"
        salt = b"salt_16_bytes_long"

        key1 = TokenManager.derive_key_from_password(password, salt)
        key2 = TokenManager.derive_key_from_password(password, salt)

        assert key1 == key2

    def test_same_password_different_salt_different_key(self):
        """Test that same password + different salt produces different keys"""
        password = "MySecurePassword"
        salt1 = b"salt_16_bytes_long"
        salt2 = b"another_16_bytes_"

        key1 = TokenManager.derive_key_from_password(password, salt1)
        key2 = TokenManager.derive_key_from_password(password, salt2)

        assert key1 != key2
