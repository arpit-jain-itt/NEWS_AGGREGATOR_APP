import pytest
from client.utils import validators

def test_validate_email():
    assert validators.validate_email('test@example.com') is True
    assert validators.validate_email('bad-email') is False
    assert validators.validate_email('user@domain') is False
    assert validators.validate_email('user@domain.com') is True


def test_validate_password():
    assert validators.validate_password('Password123') is True
    assert validators.validate_password('password') is False
    assert validators.validate_password('PASSWORD123') is False
    assert validators.validate_password('Pass123') is False
    assert validators.validate_password('Password') is False
    assert validators.validate_password('12345678') is False


def test_validate_categories():
    valid = ['general', 'sports', 'tech']
    # All valid
    is_valid, cleaned, invalid = validators.validate_categories('general, sports', valid)
    assert is_valid is True
    assert set(cleaned) == {'general', 'sports'}
    assert invalid == []
    # Some invalid
    is_valid, cleaned, invalid = validators.validate_categories('general,unknown', valid)
    assert is_valid is False
    assert 'unknown' in invalid
    # Empty input
    is_valid, cleaned, invalid = validators.validate_categories('', valid)
    assert is_valid is True
    assert cleaned == []
    assert invalid == [] 