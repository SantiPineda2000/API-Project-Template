import random
import pathlib

from sqlmodel import Session
from fastapi.testclient import TestClient

from src.config import settings
from tests.utils import random_lower_string, random_date, random_email, random_phone_number

from src.auth.service import verify_password
from src.users.service import get_user_by_username
from tests.users.utils import user_clean_up_tests, create_random_user

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
    assert response["count"] == 1


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


def test_admin_user_post_new_user(
        client:TestClient,
        admin_user_token_headers: dict[str, str],
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
        headers=admin_user_token_headers,
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


def test_post_new_user_already_exists(
        client: TestClient,
        super_user_token_headers: dict[str, str]
) -> None:
    password = random_lower_string()
    user_name = settings.FIRST_SUPERUSER
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
        headers=super_user_token_headers,
        data=user_in,
    )
    response_user = r.json()
    assert r.status_code >= 400
    assert response_user["detail"] == "A user with this username already exists in the system."


def test_post_user_with_accepted_image_type_size(
        client: TestClient,
        super_user_token_headers:dict[str, str],
        db: Session,
        png_accepted_size_image_file: pathlib.Path
) -> None:
    password = random_lower_string()
    user_name = random_lower_string()
    image_file = open(file=png_accepted_size_image_file, mode='rb')
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
            "role_name":settings.FIRST_ROLE,
    }
    r = client.post(
        url=f"{settings.API_V1_STR}/users/", 
        headers=super_user_token_headers,
        data=user_in,
        files={"user_image":("test_img.png", image_file, "image/png")}
    )
    response_user = r.json()
    assert r.status_code == 200
    assert response_user["img_path"]
    user_clean_up_tests(user_name=user_name, db=db)


def test_post_user_with_image_not_accepted_type(
        client: TestClient,
        super_user_token_headers:dict[str, str],
        bmp_accepted_size_image_file: pathlib.Path
) -> None:
    password = random_lower_string()
    user_name = random_lower_string()
    image_file = open(file=bmp_accepted_size_image_file, mode='rb')
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
            "role_name":settings.FIRST_ROLE,
    }
    r = client.post(
        url=f"{settings.API_V1_STR}/users/", 
        headers=super_user_token_headers,
        data=user_in,
        files={"user_image":("test_img.bmp", image_file, "image/bmp")}
    )
    response_user = r.json()
    assert r.status_code == 415
    assert "Unsupported file type," in response_user["detail"]



def test_post_user_with_image_size_too_large(
        client: TestClient,
        super_user_token_headers:dict[str, str],
        jpeg_unaccepted_size_image_file: pathlib.Path
) -> None:
    password = random_lower_string()
    user_name = random_lower_string()
    image_file = open(file=jpeg_unaccepted_size_image_file, mode='rb')
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
            "role_name":settings.FIRST_ROLE,
    }
    r = client.post(
        url=f"{settings.API_V1_STR}/users/", 
        headers=super_user_token_headers,
        data=user_in,
        files={"user_image":("test_img.jpeg", image_file, "image/jpeg")}
    )
    response_user = r.json()
    assert r.status_code == 413
    assert "Contents of the file too large," in response_user["detail"]

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


def test_update_user_me(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    first_name = "Updated Name"
    email = random_email()
    data = {"first_name": first_name, "email": email}
    r = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        data=data,
    )
    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["email"] == email
    assert updated_user["first_name"] == first_name


def test_update_user_me_user_name_exists(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    credentials = create_random_user(db=db)
    data = {"user_name": credentials["username"]}
    r = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        data=data,
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "A user with this username already exists in the system."
    user_clean_up_tests(user_name=credentials["username"], db=db)


def test_update_user_me_with_image(
        client:TestClient, normal_user_token_headers: dict[str, str], png_accepted_size_image_file: pathlib.Path
) -> None:
    image_file = open(file=png_accepted_size_image_file, mode='rb')
    file = {"user_image": ("test_img.png", image_file, "image/png")}
    r = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        files=file,
    )
    updated_me = r.json()
    assert r.status_code == 200
    assert updated_me["img_path"]


def test_update_user_me_with_image_not_accepted_type(
        client:TestClient, normal_user_token_headers: dict[str, str], bmp_accepted_size_image_file: pathlib.Path
) -> None:
    image_file = open(file=bmp_accepted_size_image_file, mode='rb')
    file = {"user_image": ("test_img.bmp", image_file, "image/bmp")}
    r = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        files=file,
    )
    updated_me = r.json()
    assert r.status_code == 415
    assert "Unsupported file type," in updated_me["detail"]


def test_update_user_me_with_image_size_too_large(
        client:TestClient, normal_user_token_headers: dict[str, str], jpeg_unaccepted_size_image_file: pathlib.Path
) -> None:
    image_file = open(file=jpeg_unaccepted_size_image_file, mode='rb')
    file = {"user_image": ("test_img.jpeg", image_file, "image/jpeg")}
    r = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        files=file,
    )
    updated_me = r.json()
    assert r.status_code == 413
    assert "Contents of the file too large," in updated_me["detail"]


# Tests for route "/me/password"
# ---------------------------------------------------------------------------------------------

def test_update_password_me(
    client: TestClient, super_user_token_headers: dict[str, str], db: Session
) -> None:
    new_password = random_lower_string()
    data = {
        "current_password": settings.FIRST_SUPERUSER_PASSWORD,
        "new_password": new_password,
    }
    r = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=super_user_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["message"] == "Password updated successfully!"

    user_db = get_user_by_username(session=db, user_name=settings.FIRST_SUPERUSER)
    assert user_db
    assert user_db.user_name == settings.FIRST_SUPERUSER
    assert verify_password(new_password, user_db.hashed_password)

    # Revert to the old password to keep consistency in test
    old_data = {
        "current_password": new_password,
        "new_password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=super_user_token_headers,
        json=old_data,
    )
    db.refresh(user_db)
    assert r.status_code == 200
    assert verify_password(settings.FIRST_SUPERUSER_PASSWORD, user_db.hashed_password)


def test_update_password_me_incorrect_password(
    client: TestClient, super_user_token_headers: dict[str, str]
) -> None:
    new_password = random_lower_string()
    data = {"current_password": new_password, "new_password": new_password}
    r = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=super_user_token_headers,
        json=data,
    )
    assert r.status_code == 400
    updated_user = r.json()
    assert updated_user["detail"] == "Incorrect password"


def test_update_password_me_same_password_error(
    client: TestClient, super_user_token_headers: dict[str, str]
) -> None:
    data = {
        "current_password": settings.FIRST_SUPERUSER_PASSWORD,
        "new_password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=super_user_token_headers,
        json=data,
    )
    assert r.status_code == 400
    updated_user = r.json()
    assert updated_user["detail"] == "New password cannot be the same as the current one"


# Tests for route "/{user_id}"
# ---------------------------------------------------------------------------------------------

def test_get_existing_user_super_user(
    client: TestClient, super_user_token_headers: dict[str, str], db: Session
) -> None: 
    credentials = create_random_user(db=db)
    user = get_user_by_username(session=db, user_name=credentials["username"])
    r = client.get(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=super_user_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = get_user_by_username(session=db, user_name=credentials["username"])
    assert existing_user
    assert existing_user.email == api_user["email"]
    user_clean_up_tests(user_name=credentials["username"], db=db)


def test_get_existing_user_super_user(
    client: TestClient, admin_user_token_headers: dict[str, str], db: Session
) -> None: 
    credentials = create_random_user(db=db)
    user = get_user_by_username(session=db, user_name=credentials["username"])
    r = client.get(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=admin_user_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = get_user_by_username(session=db, user_name=credentials["username"])
    assert existing_user
    assert existing_user.email == api_user["email"]
    user_clean_up_tests(user_name=credentials["username"], db=db)



def test_get_existing_user_current_user(client: TestClient, db: Session) -> None:
    credentials = create_random_user(db=db)
    user = get_user_by_username(session=db, user_name=credentials["username"])
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=credentials)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}

    r = client.get(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = get_user_by_username(session=db, user_name=credentials["username"])
    assert existing_user
    assert existing_user.email == api_user["email"]
    user_clean_up_tests(user_name=credentials["username"], db=db)


def test_get_not_existing_user(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/users/{random.randint(a=30, b=130)}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 404
    assert r.json() == {"detail": "The user specified does not exist in the system"}


def test_get_existing_user_permissions_error(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/users/{1}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403
    assert r.json() == {"detail": "The user doesn't have enough privileges"}
    

def test_update_user_super_user(
        client: TestClient, db: Session, super_user_token_headers: dict[str, str]
) -> None:
    credentials = create_random_user(db=db)
    user_db = get_user_by_username(session=db, user_name=credentials["username"])
    email = random_email()
    first_name = random_lower_string()
    data = {
        "email":email,
        "first_name": first_name
    }
    r = client.patch(
        url=f"{settings.API_V1_STR}/users/{user_db.id}",
        headers=super_user_token_headers,
        data=data
    )
    response_user = r.json()
    assert r.status_code == 200
    assert response_user["email"] == email
    assert response_user["first_name"] == first_name
    user_clean_up_tests(user_name=user_db.user_name, db=db)


def test_update_user_admin_user(
        client: TestClient, db: Session, admin_user_token_headers: dict[str, str]
) -> None:
    credentials = create_random_user(db=db)
    user_db = get_user_by_username(session=db, user_name=credentials["username"])
    email = random_email()
    first_name = random_lower_string()
    data = {
        "email":email,
        "first_name": first_name
    }
    r = client.patch(
        url=f"{settings.API_V1_STR}/users/{user_db.id}",
        headers=admin_user_token_headers,
        data=data
    )
    response_user = r.json()
    assert r.status_code == 200
    assert response_user["email"] == email
    assert response_user["first_name"] == first_name
    user_clean_up_tests(user_name=user_db.user_name, db=db)


def test_update_user_normal_user(
        client: TestClient, db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    credentials = create_random_user(db=db)
    user_db = get_user_by_username(session=db, user_name=credentials["username"])
    email = random_email()
    first_name = random_lower_string()
    data = {
        "email":email,
        "first_name": first_name
    }
    r = client.patch(
        url=f"{settings.API_V1_STR}/users/{user_db.id}",
        headers=normal_user_token_headers,
        data=data
    )
    response_user = r.json()
    assert r.status_code == 403
    assert response_user["detail"] == "The user doesn't have enough privileges"
    user_clean_up_tests(user_name=credentials["username"], db=db)


def test_update_user_with_image(
       client:TestClient, super_user_token_headers: dict[str, str], png_accepted_size_image_file: pathlib.Path, db: Session
) -> None:
    credentials = create_random_user(db=db)
    user_db = get_user_by_username(session=db, user_name=credentials["username"])
    image_file = open(file=png_accepted_size_image_file, mode='rb')
    file = {"user_image": ("test_img.png", image_file, "image/png")}
    r = client.patch(
        f"{settings.API_V1_STR}/users/{user_db.id}",
        headers=super_user_token_headers,
        files=file,
    )
    updated_me = r.json()
    assert r.status_code == 200
    assert updated_me["img_path"]


def test_update_user_with_image_not_accepted_type(
        client:TestClient, super_user_token_headers: dict[str, str], bmp_accepted_size_image_file: pathlib.Path, db: Session
) -> None:
    credentials = create_random_user(db=db)
    user_db = get_user_by_username(session=db, user_name=credentials["username"])
    image_file = open(file=bmp_accepted_size_image_file, mode='rb')
    file = {"user_image": ("test_img.bmp", image_file, "image/bmp")}
    r = client.patch(
        f"{settings.API_V1_STR}/users/{user_db.id}",
        headers=super_user_token_headers,
        files=file,
    )
    updated_me = r.json()
    assert r.status_code == 415
    assert "Unsupported file type," in updated_me["detail"]
    user_clean_up_tests(user_name=credentials["username"], db=db)


def test_update_user_with_image_size_too_large(
        client:TestClient, super_user_token_headers: dict[str, str], jpeg_unaccepted_size_image_file: pathlib.Path, db: Session
) -> None:
    credentials = create_random_user(db=db)
    user_db = get_user_by_username(session=db, user_name=credentials["username"])
    image_file = open(file=jpeg_unaccepted_size_image_file, mode='rb')
    file = {"user_image": ("test_img.jpeg", image_file, "image/jpeg")}
    r = client.patch(
        f"{settings.API_V1_STR}/users/{user_db.id}",
        headers=super_user_token_headers,
        files=file,
    )
    updated_me = r.json()
    assert r.status_code == 413
    assert "Contents of the file too large," in updated_me["detail"]
    user_clean_up_tests(user_name=credentials["username"], db=db)


def test_delete_normal_user_by_super_user(
        client:TestClient, super_user_token_headers: dict[str, str], db: Session
) -> None:
    credentials = create_random_user(db=db)
    user_del = get_user_by_username(session=db, user_name=credentials["username"])
    # Deleting the user
    r = client.delete(
        url=f"{settings.API_V1_STR}/users/{user_del.id}",
        headers=super_user_token_headers
    )
    message = r.json()
    assert r.status_code == 200
    assert "deleted successfully!" in message["message"]


def test_delete_normal_user_by_admin_user(
        client:TestClient, admin_user_token_headers: dict[str, str], db: Session
) -> None:
    credentials = create_random_user(db=db)
    user_del = get_user_by_username(session=db, user_name=credentials["username"])
    # Deleting the user
    r = client.delete(
        url=f"{settings.API_V1_STR}/users/{user_del.id}",
        headers=admin_user_token_headers
    )
    message = r.json()
    assert r.status_code == 403
    assert message["detail"] == "The user doesn't have enough privileges"


def test_delete_normal_user_by_normal_user(
        client:TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    credentials = create_random_user(db=db)
    user_del = get_user_by_username(session=db, user_name=credentials["username"])
    # Deleting the user
    r = client.delete(
        url=f"{settings.API_V1_STR}/users/{user_del.id}",
        headers=normal_user_token_headers
    )
    message = r.json()
    assert r.status_code == 403
    assert message["detail"] == "The user doesn't have enough privileges"


def test_delete_not_created_user(
        client:TestClient, super_user_token_headers: dict[str, str], db: Session
) -> None:
    # Deleting the user
    r = client.delete(
        url=f"{settings.API_V1_STR}/users/{random.randint(20, 50)}",
        headers=super_user_token_headers
    )
    message = r.json()
    assert r.status_code == 404
    assert message["detail"] == "The user specified does not exist in the system"


def test_delete_own_user_owner(
        client:TestClient, super_user_token_headers: dict[str, str]
) -> None:
    # Deleting the user
    r = client.delete(
        url=f"{settings.API_V1_STR}/users/{1}",
        headers=super_user_token_headers
    )
    message = r.json()
    assert r.status_code == 403
    assert message["detail"] == "Owners are not allowed to delete themselves"

 
# Tests for route "/{user_id}/terminate"
# ---------------------------------------------------------------------------------------------

def test_terminate_normal_user_by_super_user(
        client: TestClient, super_user_token_headers: dict[str, str], db: Session
) -> None:
    # Creating the normal user
    user_credentials = create_random_user(db=db)
    user_db = get_user_by_username(session=db, user_name=user_credentials["username"])
    # Terminating the user
    r = client.patch(
        url=f"{settings.API_V1_STR}/users/{user_db.id}/terminate",
        headers=super_user_token_headers,
        params={"terminate":True}
    )
    message = r.json()
    assert r.status_code == 200
    assert message["message"] == f"User '{user_db.user_name}' terminated!"
    user_clean_up_tests(user_name=user_db.user_name, db=db)


def test_terminate_normal_user_by_admin_user(
        client: TestClient, admin_user_token_headers: dict[str, str], db: Session
) -> None:
    # Creating the normal user
    user_credentials = create_random_user(db=db)
    user_db = get_user_by_username(session=db, user_name=user_credentials["username"])
    # Terminating the user
    r = client.patch(
        url=f"{settings.API_V1_STR}/users/{user_db.id}/terminate",
        headers=admin_user_token_headers,
        json={"terminate":True}
    )
    message = r.json()
    assert r.status_code > 400
    assert message["detail"] == "The user doesn't have enough privileges"
    user_clean_up_tests(user_name=user_db.user_name, db=db)


def test_terminate_normal_user_by_normal_user(
        client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    # Creating the normal user
    user_credentials = create_random_user(db=db)
    user_db = get_user_by_username(session=db, user_name=user_credentials["username"])
    # Terminating the user
    r = client.patch(
        url=f"{settings.API_V1_STR}/users/{user_db.id}/terminate",
        headers=normal_user_token_headers,
        json={"terminate":True}
    )
    message = r.json()
    assert r.status_code > 400
    assert message["detail"] == "The user doesn't have enough privileges"
    user_clean_up_tests(user_name=user_db.user_name, db=db)


def test_terminate_own_user(
        client: TestClient, super_user_token_headers:dict[str, str], db: Session
) -> None:
    # Getting the owner user
    user = get_user_by_username(session=db, user_name=settings.FIRST_SUPERUSER)
    r = client.patch(
        url=f"{settings.API_V1_STR}/users/{user.id}/terminate",
        headers=super_user_token_headers,
        json={"terminate":True}
    )
    message = r.json()
    assert r.status_code == 403
    assert message["detail"] == "Owners are not allowed to terminate themselves"


def test_terminate_not_registered_user(
        client: TestClient, super_user_token_headers:dict[str, str]
) -> None:
    r = client.patch(
        url=f"{settings.API_V1_STR}/users/{random.randint(20,55)}/terminate",
        headers=super_user_token_headers,
        json={"terminate":True}
    )
    message = r.json()
    assert r.status_code == 404
    assert message["detail"] == "The user specified does not exist in the system"


def test_not_terminate_normal_user_by_super_user(
        client: TestClient, super_user_token_headers: dict[str, str], db: Session
) -> None:
    # Creating the normal user
    user_credentials = create_random_user(db=db)
    user_db = get_user_by_username(session=db, user_name=user_credentials["username"])
    # Terminating the user
    r = client.patch(
        url=f"{settings.API_V1_STR}/users/{user_db.id}/terminate",
        headers=super_user_token_headers,
        json={"terminate":False}
    )
    message = r.json()
    assert r.status_code == 200
    assert message["message"] == f"User '{user_db.user_name}' not terminated"
    user_clean_up_tests(user_name=user_db.user_name, db=db)
