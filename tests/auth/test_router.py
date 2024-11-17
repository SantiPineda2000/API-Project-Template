import random
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.config import settings
from src.users.service import get_role_by_id, get_user_by_username
from tests.utils import random_lower_string, random_email, random_phone_number, random_date

##=============================================================================================
## AUTH ROUTER TESTS
##=============================================================================================


# Tests for route "/access-token".
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
        super_user_token_headers: dict[str, str], 
        db: Session
) -> None:
    # Creating a random user to terminate and test
    password = random_lower_string()
    role = get_role_by_id(session=db, role_id=1)
    user_in = {
            "first_name":random_lower_string(),
            "last_name":random_lower_string(),
            "birthday":random_date(),
            "phone_number":random_phone_number(),
            "email":random_email(),
            "user_name":settings.USERNAME_TEST_USER,
            "password":password,
            "is_admin":False,
            "is_owner":False,
            "salary":random.random() * random.randint(100,1000),
            "role":role
    }
    user_r = client.post(
        url=f"{settings.API_V1_STR}/users/", 
        headers=super_user_token_headers,
        params=user_in,
    )
    user_data = user_r.json()
    user_db = get_user_by_username(session=db, user_name=user_data["username"])
    # Terminating the user
    client.post(
        url=f"{settings.API_V1_STR}/users/{user_db.id}/terminate", 
        data={"terminate":True}, 
        headers=super_user_token_headers
    )
    # Testing the endpoint with the terminated user
    login_data = {
        "username": settings.USERNAME_TEST_USER,
        "password": password
    }
    r = client.post(
        url=f"{settings.API_V1_STR}/login/access-token",
        data=login_data
    )
    message = r.json()
    assert r.status_code == 401
    assert message["detail"] == "Terminated user"

