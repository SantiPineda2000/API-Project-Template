import pytest
import random

from sqlmodel import Session
from datetime import date

from src.config import settings
from src.users.service import create_user, get_role_by_name, get_user_by_username, get_user_by_id, update_user, update_hash_password, delete_user, terminate_user, authenticate
from src.users.schemas import CreateUser, UpdateUser
from src.auth.service import verify_password
from tests.users.utils import random_lower_string, random_email, random_date, random_phone_number, create_random_user, create_random_role

##=============================================================================================
## USERS SERVICE TESTS
##=============================================================================================

# Create user tests
# ---------------------------------------------------------------------------------------------

# Test: User creation with image path
def test_create_user_with_img_path(db:Session) -> None:
    password = random_lower_string()
    user_name = random_lower_string()
    img_path = random_lower_string()
    user_in = CreateUser(
            first_name=random_lower_string(),
            last_name=random_lower_string(),
            birthday=random_date().isoformat(),
            phone_number=random_phone_number(),
            email=random_email(),
            user_name=user_name,
            password=password,
            is_admin=False,
            is_owner=False,
            salary=random.random() * random.randint(100,1000),
    )
    role = get_role_by_name(session=db, role_name=settings.FIRST_ROLE)
    user = create_user(
        session=db, user_create=user_in, role=role, img_path=img_path
    )
    assert user.img_path == img_path
    assert user.user_name == user_name
    assert verify_password(password, user.hashed_password)


# Test: User creation without image path
def test_create_user_without_img_path(db:Session) -> None:
    password = random_lower_string()
    user_name = random_lower_string()
    user_in = CreateUser(
            first_name=random_lower_string(),
            last_name=random_lower_string(),
            birthday=random_date().isoformat(),
            phone_number=random_phone_number(),
            email=random_email(),
            user_name=user_name,
            password=password,
            is_admin=False,
            is_owner=False,
            salary=random.random() * random.randint(100,1000),
    )
    role = get_role_by_name(session=db, role_name=settings.FIRST_ROLE)
    user = create_user(
        session=db, user_create=user_in, role=role
    )
    assert user.user_name == user_name
    assert verify_password(password, user.hashed_password)


# Test: Invalid session
def test_create_user_invalid_session() -> None:
    with pytest.raises(AttributeError):
        create_user(session=None, user_create="mock_user_create", role=settings.TEST_ROLE)


# Test: Invalid user_create data
def test_create_user_invalid_user_create(db: Session):
    role = get_role_by_name(session=db, role_name=settings.TEST_ROLE)
    with pytest.raises(AttributeError):
        create_user(session=db, user_create=None, role=role)


# Test: Invalid role
def test_create_user_invalid_role(db:Session):
    password = random_lower_string()
    user_name = random_lower_string()
    user_in = CreateUser(
            first_name=random_lower_string(),
            last_name=random_lower_string(),
            birthday=random_date().isoformat(),
            phone_number=random_phone_number(),
            email=random_email(),
            user_name=user_name,
            password=password,
            is_admin=False,
            is_owner=False,
            salary=random.random() * random.randint(100,1000),
    )
    with pytest.raises(AttributeError):
        create_user(session=db, user_create=user_in, role=None)

# Get user by name tests
# ---------------------------------------------------------------------------------------------

# Test when the user is found
def test_get_user_by_username_found(db:Session) -> None:
    user = get_user_by_username(session=db, user_name=settings.FIRST_SUPERUSER)
    assert user is not None
    assert user.user_name == settings.FIRST_SUPERUSER
    assert user.is_admin == True
    assert user.is_owner == True


# Test when the user is not found
def test_get_user_by_username_not_found(db:Session) -> None:
    user = get_user_by_username(session=db, user_name="nonexistent_user")
    assert user is None


# Test with invalid input (e.g., empty username)
def test_get_user_by_username_invalid_input(db:Session) -> None:
    user = get_user_by_username(session=db, user_name="")
    assert user is None


# Get users by id tests
# ---------------------------------------------------------------------------------------------

# Test when the user is found by ID
def test_get_user_by_id_found(db:Session):
    user = get_user_by_id(session=db, user_id=1)
    assert user is not None
    assert user.user_name == settings.FIRST_SUPERUSER
    assert user.is_admin == True
    assert user.is_owner == True

# Test when the user is not found by ID
def test_get_user_by_id_not_found(db:Session):
    user = get_user_by_id(session=db, user_id=999)
    assert user is None


# Update users tests
# ---------------------------------------------------------------------------------------------

# Test updating a user
def test_update_user(db:Session) -> None:
    credentials = create_random_user(db=db)
    user = get_user_by_username(session=db, user_name=credentials["username"])

    # Create an UpdateUser instance with new data
    update_data = UpdateUser(user_name="updated_user", password="newpassword")
    updated_user = update_user(session=db, db_user=user, user_in=update_data)

    assert updated_user.user_name == "updated_user"
    assert verify_password(plain_password="newpassword", hashed_password=updated_user.hashed_password)

# Test updating a user with a role
def test_update_user_with_role(db:Session) -> None:
    credentials = create_random_user(db=db)
    user = get_user_by_username(session=db, user_name=credentials["username"])

    role_name = create_random_role(db=db)
    role = get_role_by_name(session=db, role_name=role_name)

    update_data = UpdateUser(user_name="updated_user_with_role")
    updated_user = update_user(session=db, db_user=user, user_in=update_data, role=role)

    assert updated_user.user_name == "updated_user_with_role"
    assert role.id == updated_user.roles_id

# Test updating a user with an image path
def test_update_user_with_image_path(db:Session)-> None:
    credentials = create_random_user(db=db)
    user = get_user_by_username(session=db, user_name=credentials["username"])

    update_data = UpdateUser(user_name="updated_user_with_img")
    img_path = "/path/to/image.jpg"
    updated_user = update_user(session=db, db_user=user, user_in=update_data, img_path=img_path)

    assert updated_user.user_name == "updated_user_with_img"
    assert updated_user.img_path == img_path


# Test updating a user, invalid user
def test_update_invalid_user(db:Session) -> None:
    update_data = {
        "user_name":"new name",
        "password":"newpassword"
    }
    with pytest.raises(AttributeError):
        update_user(session=db, db_user={"user_name":"Invalid user"}, user_in=update_data)


# Test updating a user, invalid role
def test_update_invalid_role(db:Session) -> None:
    credentials = create_random_user(db=db)
    user = get_user_by_username(session=db, user_name=credentials["username"])
    update_data = {
        "user_name":"new name",
        "password":"newpassword"
    }
    with pytest.raises(AttributeError):
        update_user(session=db, db_user=user, user_in=update_data, role="invalid role")


# Test updating a user, invalid update data
def test_update_invalid_update_data(db:Session) -> None:
    credentials = create_random_user(db=db)
    user = get_user_by_username(session=db, user_name=credentials["username"])
    update_data = {
       "Not Valid data":22
    }
    with pytest.raises(AttributeError):
        update_user(session=db, db_user=user, user_in=update_data)

# Update hashed password tests
# ---------------------------------------------------------------------------------------------

# Test updating a user's password
def test_update_hashed_password(db:Session) -> None:
    credentials = create_random_user(db=db)
    user = get_user_by_username(session=db, user_name=credentials["username"])
    
    # Updating the password
    message = update_hash_password(session=db, db_user=user, password="newpassword")

    # Getting the updated password
    user = get_user_by_username(session=db, user_name=credentials["username"])
    
    assert message == "Password updated successfully!"
    assert verify_password(plain_password="newpassword", hashed_password=user.hashed_password)

# Test updating a user's password, invalid user
def test_update_hashed_password_invalid_user(db:Session) -> None:

    # Updating an invalid user
    with pytest.raises(AttributeError):
        update_hash_password(session=db, db_user={"user_name":"Invalid user"}, password="newpass")


# Terminate user tests
# ---------------------------------------------------------------------------------------------

def test_terminate_user(db:Session) -> None:
    credentials = create_random_user(db=db)
    user = get_user_by_username(session=db, user_name=credentials["username"])
    # Terminating the user
    message = terminate_user(session=db, db_user=user)
    user = get_user_by_username(session=db, user_name=user.user_name)
    assert user.user_name in message
    assert type(user.terminated_at) == date

# Delete user tests
# ---------------------------------------------------------------------------------------------

def test_delete_user(db:Session) -> None:
    credentials = create_random_user(db=db)
    user = get_user_by_username(session=db, user_name=credentials["username"])

    assert user is not None
    # Delete the user
    message = delete_user(session=db, db_user=user)

    assert user.user_name in message
    assert get_user_by_username(session=db, user_name=user.user_name) is None


# Authenticate user test
# ---------------------------------------------------------------------------------------------

def test_authenticate_user(db:Session) -> None:
    credentials = create_random_user(db=db)

    assert authenticate(session=db, user_name=credentials["username"], password=credentials["password"])


def test_authenticate_user_incorrect_password(db:Session) -> None:
    credentials = create_random_user(db=db)

    assert authenticate(session=db, user_name=credentials["username"], password="incorrect password") == None


def test_authenticate_invalid_user(db:Session) -> None:

    assert authenticate(session=db, user_name="Not a user", password="Not a password") == None
