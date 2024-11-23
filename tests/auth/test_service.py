import pytest
from datetime import datetime, timedelta, timezone
import jwt

from src.config import settings
from src.auth.service import create_access_token, ALGORITHM
from tests.auth.utils import get_data

##=============================================================================================
## AUTH SERVICE TESTS
##=============================================================================================

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