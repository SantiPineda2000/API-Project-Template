import random

from unittest.mock import patch
from sqlmodel import Session
from fastapi.testclient import TestClient

from src.config import settings
from tests.utils import random_lower_string, random_date, random_email, random_phone_number

from src.users.service import get_user_by_username, create_user
from src.users.schemas import UsersPublic
from tests.users.utils import user_clean_up_tests

##=============================================================================================
## USERS ROUTER TESTS
##=============================================================================================


# Tests for route "/"
# ---------------------------------------------------------------------------------------------

def test_get_all_users_super_user(
        client: TestClient, super_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        url=f"{settings.API_V1_STR}/users/",
        headers=super_user_token_headers
    )
    response = r.json()
    assert r.status_code == 200
    assert type(response["data"]) == list


def test_get_all_users_admin_user(
        client: TestClient, admin_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        url=f"{settings.API_V1_STR}/users/",
        headers=admin_user_token_headers
    )
    response = r.json()
    assert r.status_code == 200
    assert type(response["data"]) == list


def test_get_all_users_normal_user(
        client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    r = client.get(
        url=f"{settings.API_V1_STR}/users/",
        headers=normal_user_token_headers
    )
    response = r.json()
    assert r.status_code > 400
    assert response["detail"]


def test_super_user_post_new_user(
        client:TestClient,
        super_user_token_headers: dict[str, str],
        db: Session
) -> None:
    password = random_lower_string()
    user_name = random_lower_string()
    user_in = {
            "first_name":random_lower_string(),
            "last_name":random_lower_string(),
            "birthday":random_date().isoformat(),
            "phone_number":random_phone_number(),
            "email":random_email(),
            "user_name":user_name,
            "password":password,
            "is_admin":False,
            "is_owner":False,
            "salary":random.random() * random.randint(100,1000),
            "role_name":settings.FIRST_ROLE
    }
    r = client.post(
        url=f"{settings.API_V1_STR}/users/", 
        headers=super_user_token_headers,
        data=user_in,
    )
    response_user = r.json()
    assert r.status_code == 200
    assert response_user["user_name"] == user_name
    assert response_user["is_admin"] == False
    assert response_user["is_owner"] == False
    user_clean_up_tests(user_name=user_name, db=db)


def test_normal_user_post_new_user(
        client:TestClient,
        normal_user_token_headers: dict[str, str],
) -> None:
    password = random_lower_string()
    user_name = random_lower_string()
    user_in = {
            "first_name":random_lower_string(),
            "last_name":random_lower_string(),
            "birthday":random_date().isoformat(),
            "phone_number":random_phone_number(),
            "email":random_email(),
            "user_name": user_name,
            "password":password,
            "is_admin":False,
            "is_owner":False,
            "salary":random.random() * random.randint(100,1000),
            "role_name":settings.FIRST_ROLE
    }
    r = client.post(
        url=f"{settings.API_V1_STR}/users/", 
        headers=normal_user_token_headers,
        data=user_in,
    )
    response_user = r.json()
    assert r.status_code >= 400
    assert response_user["detail"]


def test_post_new_user_not_existing_role(
        client:TestClient,
        super_user_token_headers: dict[str, str],
) -> None:
    password = random_lower_string()
    user_name = random_lower_string()
    user_in = {
            "first_name":random_lower_string(),
            "last_name":random_lower_string(),
            "birthday":random_date().isoformat(),
            "phone_number":random_phone_number(),
            "email":random_email(),
            "user_name": user_name,
            "password":password,
            "is_admin":False,
            "is_owner":False,
            "salary":random.random() * random.randint(100,1000),
            "role_name":"incorrect"
    }
    r = client.post(
        url=f"{settings.API_V1_STR}/users/", 
        headers=super_user_token_headers,
        data=user_in,
    )
    response_user = r.json()
    assert r.status_code >= 400
    assert response_user["detail"] == "The role provided does not exist in the system."


# Tests for route "/me"
# ---------------------------------------------------------------------------------------------

def test_get_users_superuser_me(
    client: TestClient, super_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=super_user_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["terminated_at"] is None
    assert current_user["is_admin"] is True
    assert current_user["is_owner"] is True
    assert current_user["user_name"] == settings.FIRST_SUPERUSER



def test_get_users_normal_user_me(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["terminated_at"] is None
    assert current_user["is_admin"] is False
    assert current_user["is_owner"] is False
    assert current_user["user_name"] == settings.USERNAME_TEST_USER


def test_get_users_admin_user_me(
    client: TestClient, admin_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=admin_user_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["terminated_at"] is None
    assert current_user["is_admin"] is True
    assert current_user["is_owner"] is False
    assert current_user["user_name"] == settings.USERNAME_TEST_USER + "admin"


# Tests for route "/{user_id}"
# ---------------------------------------------------------------------------------------------

# def test_get_existing_user(
#     client: TestClient, super_user_token_headers: dict[str, str], db: Session
# ) -> None:
#     username = random_email()
#     password = random_lower_string()
#     user_in = CreateUser(user_name=username, password=password)
#     user = create_user(session=db, user_create=user_in)
#     user_id = user.id
#     r = client.get(
#         f"{settings.API_V1_STR}/users/{user_id}",
#         headers=super_user_token_headers,
#     )
#     assert 200 <= r.status_code < 300
#     api_user = r.json()
#     existing_user = crud.get_user_by_email(session=db, email=username)
#     assert existing_user
#     assert existing_user.email == api_user["email"]


# def test_get_existing_user_current_user(client: TestClient, db: Session) -> None:
#     username = random_email()
#     password = random_lower_string()
#     user_in = UserCreate(email=username, password=password)
#     user = crud.create_user(session=db, user_create=user_in)
#     user_id = user.id

#     login_data = {
#         "username": username,
#         "password": password,
#     }
#     r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
#     tokens = r.json()
#     a_token = tokens["access_token"]
#     headers = {"Authorization": f"Bearer {a_token}"}

#     r = client.get(
#         f"{settings.API_V1_STR}/users/{user_id}",
#         headers=headers,
#     )
#     assert 200 <= r.status_code < 300
#     api_user = r.json()
#     existing_user = crud.get_user_by_email(session=db, email=username)
#     assert existing_user
#     assert existing_user.email == api_user["email"]


# def test_get_existing_user_permissions_error(
#     client: TestClient, normal_user_token_headers: dict[str, str]
# ) -> None:
#     r = client.get(
#         f"{settings.API_V1_STR}/users/{uuid.uuid4()}",
#         headers=normal_user_token_headers,
#     )
#     assert r.status_code == 403
#     assert r.json() == {"detail": "The user doesn't have enough privileges"}

