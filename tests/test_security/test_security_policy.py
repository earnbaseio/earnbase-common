"""Tests for SecurityPolicy."""

import pytest
from earnbase_common.security import SecurityPolicy


@pytest.mark.unit
@pytest.mark.security
class TestSecurityPolicy:
    """Test SecurityPolicy."""

    def test_default_policy_values(self, security_policy):
        """Test default security policy values."""
        # Password policies
        assert security_policy.PASSWORD_MIN_LENGTH == 8
        assert len(security_policy.PASSWORD_PATTERNS) == 4
        assert "uppercase" in security_policy.PASSWORD_PATTERNS
        assert "lowercase" in security_policy.PASSWORD_PATTERNS
        assert "digit" in security_policy.PASSWORD_PATTERNS
        assert "special" in security_policy.PASSWORD_PATTERNS

        # Account policies
        assert security_policy.MAX_LOGIN_ATTEMPTS == 5
        assert security_policy.ACCOUNT_LOCKOUT_MINUTES == 15

        # Token policies
        assert security_policy.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert security_policy.REFRESH_TOKEN_EXPIRE_DAYS == 7
        assert security_policy.VERIFICATION_TOKEN_EXPIRE_HOURS == 24
        assert security_policy.RESET_TOKEN_EXPIRE_HOURS == 24

        # Session policies
        assert security_policy.MAX_SESSIONS_PER_USER == 5
        assert security_policy.SESSION_IDLE_TIMEOUT_MINUTES == 60

    def test_policy_immutability(self, security_policy):
        """Test that security policy is immutable."""
        with pytest.raises(TypeError):
            security_policy.PASSWORD_MIN_LENGTH = 10

        with pytest.raises(TypeError):
            security_policy.PASSWORD_PATTERNS = {}

        with pytest.raises(TypeError):
            security_policy.MAX_LOGIN_ATTEMPTS = 3

    def test_password_patterns_format(self, security_policy):
        """Test password pattern format."""
        for pattern_name, (regex, message) in security_policy.PASSWORD_PATTERNS.items():
            # Check pattern name format
            assert isinstance(pattern_name, str)
            assert pattern_name.islower()

            # Check regex and message format
            assert isinstance(regex, str)
            assert isinstance(message, str)
            assert len(regex) > 0
            assert len(message) > 0

    @pytest.mark.parametrize(
        "pattern_name,test_pass,test_fail",
        [
            ("uppercase", "Password123!", "password123!"),  # Test uppercase pattern
            ("lowercase", "Password123!", "PASSWORD123!"),  # Test lowercase pattern
            ("digit", "Password123!", "Password!!!"),  # Test digit pattern
            ("special", "Password123!", "Password123"),  # Test special char pattern
        ],
    )
    def test_password_pattern_matching(
        self, security_policy, pattern_name, test_pass, test_fail
    ):
        """Test password pattern matching."""
        import re

        pattern = security_policy.PASSWORD_PATTERNS[pattern_name][0]

        # Test passing case
        assert re.search(pattern, test_pass) is not None

        # Test failing case
        assert re.search(pattern, test_fail) is None

    def test_custom_policy_values(self):
        """Test creating policy with custom values."""
        custom_policy = SecurityPolicy(
            PASSWORD_MIN_LENGTH=10,
            MAX_LOGIN_ATTEMPTS=3,
            ACCOUNT_LOCKOUT_MINUTES=30,
            ACCESS_TOKEN_EXPIRE_MINUTES=15,
            MAX_SESSIONS_PER_USER=3,
        )

        assert custom_policy.PASSWORD_MIN_LENGTH == 10
        assert custom_policy.MAX_LOGIN_ATTEMPTS == 3
        assert custom_policy.ACCOUNT_LOCKOUT_MINUTES == 30
        assert custom_policy.ACCESS_TOKEN_EXPIRE_MINUTES == 15
        assert custom_policy.MAX_SESSIONS_PER_USER == 3

        # Other values should remain default
        assert custom_policy.PASSWORD_PATTERNS == SecurityPolicy().PASSWORD_PATTERNS
        assert (
            custom_policy.REFRESH_TOKEN_EXPIRE_DAYS
            == SecurityPolicy().REFRESH_TOKEN_EXPIRE_DAYS
        )

    def test_policy_validation(self):
        """Test policy validation rules."""
        # Test minimum values
        with pytest.raises(ValueError):
            SecurityPolicy(PASSWORD_MIN_LENGTH=0)

        with pytest.raises(ValueError):
            SecurityPolicy(MAX_LOGIN_ATTEMPTS=0)

        with pytest.raises(ValueError):
            SecurityPolicy(ACCOUNT_LOCKOUT_MINUTES=0)

        # Test invalid types
        with pytest.raises(TypeError):
            SecurityPolicy(PASSWORD_MIN_LENGTH="8")

        with pytest.raises(TypeError):
            SecurityPolicy(MAX_LOGIN_ATTEMPTS="5")

    def test_policy_hash_and_equality(self):
        """Test policy hash and equality comparison."""
        policy1 = SecurityPolicy()
        policy2 = SecurityPolicy()
        policy3 = SecurityPolicy(PASSWORD_MIN_LENGTH=10)

        # Same default policies should be equal
        assert policy1 == policy2
        assert hash(policy1) == hash(policy2)

        # Different policies should not be equal
        assert policy1 != policy3
        assert hash(policy1) != hash(policy3)
