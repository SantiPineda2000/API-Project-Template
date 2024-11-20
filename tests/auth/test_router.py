from fastapi.testclient import TestClient

from sqlmodel import Session, select

from src.config import settings
from src.auth.service import generate_password_reset_token, verify_password_reset_token
from src.users.service import verify_password, get_user_by_username

from tests.utils import random_lower_string

##=============================================================================================
## AUTH ROUTER TESTS
##=============================================================================================


# Tests for route "login/access-token".
# ---------------------------------------------------------------------------------------------

def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(
        url=f"{settings.API_V1_STR}/login/access-token", 
        data=login_data
    )
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_get_access_token_incorrect_password(client:TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": "incorrect"
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    message = r.json()
    assert r.status_code == 401
    assert message["detail"] == "Incorrect username or password"


def test_get_access_token_terminated_user(
        client:TestClient,
        terminated_user_token_headers_password: dict[str, str]
) -> None:
    # Testing the endpoint with the terminated user
    login_data = {
        "username": settings.USERNAME_TEST_USER + "terminated",
        "password": terminated_user_token_headers_password["password"]
    }
    r = client.post(
        url=f"{settings.API_V1_STR}/login/access-token",
        data=login_data
    )
    message = r.json()
    assert r.status_code == 401
    assert message["detail"] == "Terminated user"


def test_use_access_token(
        client:TestClient, admin_user_token_headers:dict[str, str]
) -> None:
    r = client.get(
        url=f"{settings.API_V1_STR}/users/",
        headers=admin_user_token_headers
    )
    result = r.json()
    assert r.status_code == 200
    assert result["data"]
    assert result["count"] > 0


# Tests for route "login/password-recovery/{user_name}".
# ---------------------------------------------------------------------------------------------

def test_get_password_recovery_email(client: TestClient) -> None:
    # Testing with the first user created
    user_name = settings.FIRST_SUPERUSER
    r = client.post(
        url=f"{settings.API_V1_STR}/login/password-recovery/{user_name}",
    )
    message = r.json()
    assert r.status_code == 200
    assert message["message"] == "Password recovery email sent"


def test_get_password_recovery_email_user_not_exits(client: TestClient) -> None:
    # Testing with a random user_name
    user_name = random_lower_string()
    r = client.post(
        url=f"{settings.API_V1_STR}/login/password-recovery/{user_name}",
    )
    message = r.json()
    assert r.status_code == 404
    assert message["detail"] == "The user specified does not exist in the system"


def test_get_password_recovery_email_(client: TestClient, terminated_user_token_headers_password: dict[str, str]) -> None:
    # Testing with a user without a registered email
    user_name = settings.USERNAME_TEST_USER + "terminated"
    r = client.post(
        url=f"{settings.API_V1_STR}/login/password-recovery/{user_name}",
        headers=terminated_user_token_headers_password["headers"]
    )
    message = r.json()
    assert r.status_code == 401
    assert message["detail"] == "Terminated user"


# Tests for route "login/reset-password".
# ---------------------------------------------------------------------------------------------

def test_reset_password(
    client: TestClient, db: Session, admin_user_token_headers:dict[str, str]
) -> None:
    user_name = settings.USERNAME_TEST_USER + "admin"
    token = generate_password_reset_token(username=user_name)
    data = {"new_password": "changethis", "token": token}
    r = client.post(
        f"{settings.API_V1_STR}/login/reset-password",
        headers=admin_user_token_headers,
        json=data,
    )
    message = r.json()
    assert r.status_code == 200
    assert message["message"] == "Password updated successfully!"
    user = get_user_by_username(session=db, user_name=user_name)
    assert user
    assert verify_password(data["new_password"], user.hashed_password)


def test_reset_password_invalid_token(
    client: TestClient, admin_user_token_headers: dict[str, str]
) -> None:
    data = {"new_password": "changethis", "token": "invalid"}
    r = client.post(
        f"{settings.API_V1_STR}/login/reset-password/",
        headers=admin_user_token_headers,
        json=data,
    )
    response = r.json()

    assert "detail" in response
    assert r.status_code == 400
    assert response["detail"] == "Invalid token"


def test_reset_password_terminated_user(
        client: TestClient, terminated_user_token_headers_password: dict[str, str]
) -> None:
    user_name = settings.USERNAME_TEST_USER + "terminated"
    token = generate_password_reset_token(username=user_name)
    data = {"new_password":"changethis", "token": token}
    r = client.post(
        url=f"{settings.API_V1_STR}/login/reset-password/",
        headers=terminated_user_token_headers_password["headers"],
        json=data,
    )
    response = r.json()
    assert "detail" in response
    assert r.status_code == 401
    assert response["detail"] == "Terminated user"