import pytest
from datetime import datetime, timedelta, timezone
import jwt

from src.config import settings
from src.auth.service import create_access_token, ALGORITHM, generate_password_reset_token, verify_password_reset_token
from tests.auth.utils import get_data

##=============================================================================================
## AUTH SERVICE TESTS
##=============================================================================================


# Create access token tests
# ---------------------------------------------------------------------------------------------

# Test: Valid token creation
def test_create_access_token_valid() -> None:
    data = get_data()
    
    token = create_access_token(data["subject"], data["expires_delta"])

    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=ALGORITHM)

    assert decoded_token["sub"] == str(data["subject"])
    assert "exp" in decoded_token

    # Check expiration
    expiration = datetime.fromtimestamp(decoded_token["exp"], tz=timezone.utc)
    expected_expiration = datetime.now(timezone.utc) + data["expires_delta"]
    assert expiration.timestamp() == pytest.approx(expected_expiration.timestamp(), rel=0.01)  # Allow small time drift


# Test: Invalid secret key
def test_create_access_token_invalid_secret() -> None:
    data = get_data()
    
    token = create_access_token(data["subject"], data["expires_delta"])

    with pytest.raises(jwt.exceptions.InvalidSignatureError):
        jwt.decode(token, "wrong_secret_key", algorithms=[ALGORITHM])


# Test: Expired token
def test_create_access_token_expired() -> None:
    subject = 123
    expires_delta = timedelta(seconds=-1)  # Expired token

    token = create_access_token(subject, expires_delta)

    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


# Test: Different subject types
def test_create_access_token_different_subjects() -> None:
    subjects = ["user123", 456, {"user_id": 789}, None]
    expires_delta = timedelta(minutes=5)

    for subject in subjects:
        token = create_access_token(subject, expires_delta)
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

        assert decoded_token["sub"] == str(subject)


# Password reset token generation and validation tests
# ---------------------------------------------------------------------------------------------

# Test generating a password reset token
def test_generate_password_reset_token() -> None:
    user_name = "test_user"

    token = generate_password_reset_token(username=user_name)

    # Decode the contents to validate
    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_token["sub"] == user_name
    assert "exp" in decoded_token
    assert "nbf" in decoded_token

    exp_time = datetime.fromtimestamp(decoded_token["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    assert now < exp_time <= now + timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)


# Test verifying a valid token
def test_verify_password_reset_token_valid():
    username = "test_user"
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)

    # Create a valid token
    valid_token = jwt.encode(
        {"exp": exp.timestamp(), "nbf": now, "sub": username},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )

    result = verify_password_reset_token(valid_token)
    assert result == username


# Test verifying an expired token
def test_verify_password_reset_token_expired():
    username = "test_user"
    now = datetime.now(timezone.utc)
    expired_time = now - timedelta(hours=1)  # Already expired

    expired_token = jwt.encode(
        {"exp": expired_time.timestamp(), "nbf": now, "sub": username},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )

    result = verify_password_reset_token(expired_token)
    assert result is None


# Test verifying a token with invalid signature
def test_verify_password_reset_token_invalid_signature():
    username = "test_user"
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)

    # Create a token with a different secret key
    invalid_token = jwt.encode(
        {"exp": exp.timestamp(), "nbf": now, "sub": username},
        "wrong_secret_key",
        algorithm=ALGORITHM,
    )

    result = verify_password_reset_token(invalid_token)
    assert result is None


# Test verifying a malformed token
def test_verify_password_reset_token_malformed():
    malformed_token = "this_is_not_a_valid_token"

    result = verify_password_reset_token(malformed_token)
    assert result is None