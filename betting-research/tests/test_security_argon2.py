"""
Unit tests for Argon2 Password Hashing Manager
"""

import pytest
from src.security.argon2_manager import Argon2Manager, hash_password, verify_password


class TestArgon2Manager:
    """Tests for Argon2 password hashing"""

    def test_manager_initialization(self):
        """Test Argon2Manager initializes correctly"""
        manager = Argon2Manager()
        assert manager.time_cost == 3
        assert manager.memory_cost == 65536
        assert manager.parallelism == 4
        assert manager.hash_len == 32
        assert manager.salt_len == 16

    def test_custom_parameters(self):
        """Test Argon2Manager with custom parameters"""
        manager = Argon2Manager(
            time_cost=2,
            memory_cost=32768,
            parallelism=2,
            hash_len=16,
            salt_len=8
        )
        assert manager.time_cost == 2
        assert manager.memory_cost == 32768
        assert manager.parallelism == 2
        assert manager.hash_len == 16
        assert manager.salt_len == 8

    def test_hash_password(self):
        """Test password hashing"""
        manager = Argon2Manager()
        password = "MySecurePassword123!"

        hashed = manager.hash_password(password)

        # Hash should be a non-empty string
        assert isinstance(hashed, str)
        assert len(hashed) > 0

        # Hash should contain Argon2 format
        assert "$argon2id$" in hashed

    def test_hash_empty_password(self):
        """Test that empty password raises error"""
        manager = Argon2Manager()

        with pytest.raises(ValueError, match="Password cannot be empty"):
            manager.hash_password("")

    def test_verify_correct_password(self):
        """Test password verification with correct password"""
        manager = Argon2Manager()
        password = "MySecurePassword123!"

        hashed = manager.hash_password(password)
        is_valid = manager.verify_password(hashed, password)

        assert is_valid is True

    def test_verify_incorrect_password(self):
        """Test password verification with incorrect password"""
        manager = Argon2Manager()
        password = "MySecurePassword123!"

        hashed = manager.hash_password(password)
        is_valid = manager.verify_password(hashed, "WrongPassword")

        assert is_valid is False

    def test_verify_invalid_hash(self):
        """Test password verification with invalid hash"""
        manager = Argon2Manager()

        is_valid = manager.verify_password("invalid_hash", "password")
        assert is_valid is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (due to random salt)"""
        manager = Argon2Manager()
        password = "SamePassword123!"

        hash1 = manager.hash_password(password)
        hash2 = manager.hash_password(password)

        # Hashes should be different (different salts)
        assert hash1 != hash2

        # But both should verify correctly
        assert manager.verify_password(hash1, password) is True
        assert manager.verify_password(hash2, password) is True

    def test_needs_rehash_default_params(self):
        """Test rehash check with default parameters"""
        manager = Argon2Manager()
        password = "MySecurePassword123!"

        hashed = manager.hash_password(password)
        needs_rehash = manager.needs_rehash(hashed)

        # Should not need rehash (same parameters)
        assert needs_rehash is False

    def test_needs_rehash_upgraded_params(self):
        """Test rehash check with upgraded parameters"""
        manager_default = Argon2Manager(time_cost=3, memory_cost=65536)
        manager_upgraded = Argon2Manager(time_cost=4, memory_cost=131072)

        password = "MySecurePassword123!"
        hashed = manager_default.hash_password(password)

        needs_rehash = manager_upgraded.needs_rehash(hashed)

        # Should need rehash (upgraded parameters)
        assert needs_rehash is True

    def test_generate_salt(self):
        """Test salt generation"""
        manager = Argon2Manager()
        salt = manager.generate_salt()

        assert isinstance(salt, bytes)
        assert len(salt) == manager.salt_len

    def test_get_hash_info(self):
        """Test extracting hash information"""
        manager = Argon2Manager()
        password = "MySecurePassword123!"

        hashed = manager.hash_password(password)
        info = manager.get_hash_info(hashed)

        assert info['algorithm'] == 'argon2id'
        assert 'version' in info
        assert info['time_cost'] == manager.time_cost
        assert info['memory_cost'] == manager.memory_cost
        assert info['parallelism'] == manager.parallelism


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_hash_password_function(self):
        """Test convenience hash_password function"""
        password = "MySecurePassword123!"

        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert "$argon2id$" in hashed

    def test_verify_password_function(self):
        """Test convenience verify_password function"""
        password = "MySecurePassword123!"

        hashed = hash_password(password)
        is_valid = verify_password(hashed, password)

        assert is_valid is True

    def test_functions_use_same_manager(self):
        """Test that convenience functions use the same manager instance"""
        password = "MySecurePassword123!"

        hashed1 = hash_password(password)
        hashed2 = hash_password(password)

        # Hashes should be different (different salts from same manager)
        assert hashed1 != hashed2

        # Both should verify correctly
        assert verify_password(hashed1, password) is True
        assert verify_password(hashed2, password) is True
