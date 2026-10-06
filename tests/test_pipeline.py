import pytest
from src.main import validate_crypto_record


def test_validate_crypto_record_valid():
    """Test that a valid crypto record passes validation."""
    assert validate_crypto_record("bitcoin", 65000.50, 1200000000000, 35000000000) is True


def test_validate_crypto_record_invalid_price():
    """Test that non-numeric or negative price fails validation."""
    assert validate_crypto_record("bitcoin", -100, 1200000000000, 35000000000) is False
    assert validate_crypto_record("bitcoin", "invalid_price", 1200000000000, 35000000000) is False


def test_validate_crypto_record_invalid_symbol():
    """Test that empty symbol string fails validation."""
    assert validate_crypto_record("", 65000.50, 1200000000000, 35000000000) is False
    assert validate_crypto_record(None, 65000.50, 1200000000000, 35000000000) is False