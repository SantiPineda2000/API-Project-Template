import pytest
import random

from sqlmodel import Session

from src.config import settings
from src.users.service import create_user, get_role_by_name
from src.users.schemas import CreateUser
from src.auth.service import verify_password
from tests.users.utils import random_lower_string, random_email, random_date, random_phone_number

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

