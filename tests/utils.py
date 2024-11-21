import random
import string
import phonenumbers
import numpy as np

from PIL import Image
from datetime import date
from sqlmodel import Session
from fastapi.testclient import TestClient
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.config import settings
from src.users.service import get_user_by_username, get_role_by_name

##=============================================================================================
## UTILITY FUNCTIONS FOR TESTING
##=============================================================================================


def random_lower_string() -> str:
    '''Generates a random string'''
    return "".join(random.choices(string.ascii_lowercase, k=20))


def random_email() -> str:
    '''Generates a random email'''
    return str(object=f"{random_lower_string()}@{random_lower_string()}.com")


def random_date() -> date:
    '''Generates a random date'''
    return date(random.randint(1990, 2010), random.randint(1, 12), random.randint(1,28))


def random_phone_number(country_code: str = 'MX') -> PhoneNumber:
    """Generates a mexican random phone number that complies with Pydantic's PhoneNumber class."""
    # Choose a random area code and a random local number
    area_code = 222
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
        client:TestClient, 
        user_name:str, 
        db: Session, 
        role_name:str,
        super_user_token_headers: dict[str, str]
    ) -> dict[str, str]:
    '''
    Return a valid token header for the user with the given user_name,
    if the user doesn't exist it is first created.
    '''
    role = get_role_by_name(session=db, role_name=role_name)

    if not role:
        role_in = {
            "name":role_name
        }
        role = client.post(
            url=f"{settings.API_V1_STR}/roles/",
            headers=super_user_token_headers,
            json=role_in
        )

    user = get_user_by_username(session=db, user_name=user_name)
    password = random_lower_string()

    if not user:
        # Create the test user if it is not found
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
            "role_name":role_name
        }
        user_r = client.post(
            url=f"{settings.API_V1_STR}/users/", 
            headers=super_user_token_headers,
            data=user_in,
        )
    else:
        user_in_update = {"password":password}

        if not user.id:
            raise Exception("User id not set")
        
        user_r = client.patch(
            url=f"{settings.API_V1_STR}/login/{user.id}",
            headers=super_user_token_headers,
            data=user_in_update,
        )

    user = user_r.json()
    return user_authentication_headers(client=client, username=user["user_name"], password=password)


def get_admin_token_headers(
        *,
        client: TestClient,
        super_user_token_headers: dict[str, str],
) -> dict[str, str]:
    '''
    Returns a dictionary containing the authentication headers for the test admin user `USERNAME_TEST_USER + "admin"`.

    Returns
    ---
    "Authorization bearer" : TOKEN
    '''
    # Creating a random user to terminate and test
    password = random_lower_string()
    user_name = settings.USERNAME_TEST_USER + "admin"
    user_in = {
            "first_name":random_lower_string(),
            "last_name":random_lower_string(),
            "birthday":random_date().isoformat(),
            "phone_number":random_phone_number(),
            "email":random_email(),
            "user_name": user_name,
            "password":password,
            "is_admin":True,
            "is_owner":False,
            "salary":random.random() * random.randint(100,1000),
            "role_name":settings.FIRST_ROLE
    }
    client.post(
        url=f"{settings.API_V1_STR}/users/", 
        headers=super_user_token_headers,
        data=user_in,
    )
    return user_authentication_headers(client=client, username=user_name, password=password)


def terminated_user_authentication_headers_and_password(
        *,
        client: TestClient,
        db: Session,
        super_user_token_headers: dict[str, str],
) -> dict[str, str]:
    '''
    Returns a dictionary containing the authentication headers and password for the 
    test user USERNAME_TEST_USER.

    Returns
    ---
    "authorization_headers":{"Authorization bearer":TOKEN}
    "password":password
    '''
    # Creating a random user to terminate and test
    password = random_lower_string()
    user_in = {
            "first_name":random_lower_string(),
            "last_name":random_lower_string(),
            "birthday":random_date().isoformat(),
            "phone_number":random_phone_number(),
            "email":random_email(),
            "user_name":settings.USERNAME_TEST_USER + "terminated",
            "password":password,
            "is_admin":False,
            "is_owner":False,
            "salary":random.random() * random.randint(100,1000),
            "role_name":settings.FIRST_ROLE
    }
    client.post(
        url=f"{settings.API_V1_STR}/users/", 
        headers=super_user_token_headers,
        data=user_in,
    )
    auth_headers = user_authentication_headers(
                    client=client, 
                    username=settings.USERNAME_TEST_USER + "terminated",
                    password=password
                    )
    user_db = get_user_by_username(session=db, user_name=settings.USERNAME_TEST_USER + "terminated")
    # Terminating the user
    client.patch(
        url=f"{settings.API_V1_STR}/users/{user_db.id}/terminate", 
        headers=super_user_token_headers,
        params={"user_id":user_db.id,"terminate":True}, 
    )
    return {"headers": auth_headers, "password":password}



def create_random_image(*, target_size: int) -> Image:
    """
    Creates a random image of the specified type and size and wraps it in an UploadFile instance.
    
    Args:
        image_type (str): The type of the image (e.g., "png", "jpeg").
        target_size (int): Approximate target file size in bytes.
    
    Returns:
        UploadFile: An UploadFile object containing the random image.
    """
    # Initial dimensions for the image
    width = int(round(np.sqrt(target_size / 24), 0)) # Calculate the width and height from target_size
    height = width

    # Generate a random matrix with shape (size, size, 3) for RGB channels
    array = np.random.randint(0, 255, (width, height, 3), dtype=np.uint8)
    image = Image.fromarray(obj=array, mode="RGB")
    
    return image