import random
import string
import phonenumbers

from fastapi.testclient import TestClient
from datetime import date
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlmodel import Session

from src.config import settings
from src.users.service import get_user_by_username, create_user, get_role_by_name, create_role, update_user
from src.users.schemas import CreateUser, CreateRole, UpdateUser

##=============================================================================================
## UTILITY FUNCTIONS FOR TESTING
##=============================================================================================


def random_lower_string() -> str:
    '''Generates a random string'''
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    '''Generates a random email'''
    return EmailStr(f"{random_lower_string()}@{random_lower_string()}.com")


def random_date() -> date:
    '''Generates a random date'''
    return date(random.randint(1990, 2010), random.randint(0, 12), random.randint(0,29))


def random_phone_number(country_code: str = 'MX') -> PhoneNumber:
    """Generates a random phone number that complies with Pydantic's PhoneNumber class."""
    # Choose a random area code and a random local number
    area_code = random.randint(200, 999)
    local_number = random.randint(1000000, 9999999)
    national_number_str = f"{area_code}{local_number}"
    # Parse the number with phonenumbers, using the given country code
    parsed_number = phonenumbers.parse(national_number_str, country_code)
    # Convert to E164 format
    e164_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)

    return PhoneNumber(e164_number)


def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    '''Returns superuser credentials as token header'''
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def user_authentication_headers(
        *,
        client:TestClient,
        username: str,
        password:str
    ) -> dict[str, str]:
    '''Returns normal user credentials as token header'''
    data={"username": username, "password": password}

    r = client.post(f'{settings.API_V1_STR}/login/access-token', data=data)
    response = r.json()
    auth_token = response["access_token"]

    return {"Authorization": f"Bearer {auth_token}"}


def authentication_token_from_username(
        *,
        client:TestClient, user_name:str, db: Session, role_name:str
    ) -> dict[str, str]:
    '''
    Return a valid token header for the user with the given user_name,
    if the user doesn't exist it is first created.
    '''
    role = get_role_by_name(session=db, role_name=role_name)

    if not role:
        role = CreateRole(
            name=settings.TEST_ROLE
        )
        role =  create_role(session=db, role_create=role)

    user = get_user_by_username(session=db, user_name=user_name)
    password = random_lower_string()

    if not user:
        # Create the test user if it is not found
        user = CreateUser(
            first_name=random_lower_string(),
            last_name=random_lower_string(),
            birthday=random_date(),
            phone_number=random_phone_number(),
            email=random_email(),
            user_name=settings.USERNAME_TEST_USER,
            password=password,
            is_admin=False,
            is_owner=False,
            salary=random.random() * random.randint(100,1000)
        )
        create_user(session=db, user_create=user, role=role)
    else:
        user_in_update = UpdateUser(password=password)
        if not user.id:
            raise Exception("User id not set")
        user = update_user(session=db, db_user=user, user_in=user_in_update)

    return user_authentication_headers(client=client, username=user_name, password=password)
