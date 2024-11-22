import random

from sqlmodel import Session

from src.config import settings
from src.users.service import get_user_by_username, create_user, get_role_by_name, create_role
from src.users.schemas import CreateUser, CreateRole
from tests.utils import random_lower_string, random_email, random_date, random_phone_number

##=============================================================================================
## USERS UTILITY FUNCTIONS
##=============================================================================================


def user_clean_up_tests(*, user_name: str, db:Session) -> None:
    '''
    Deletes the passed user_name, to clean up tests
    '''
    db_user = get_user_by_username(session=db, user_name=user_name)
    db.delete(db_user)
    db.commit()


def create_random_user(*, db: Session) -> dict[str, str]:
    '''
    Create a random user and return the credentials

    Returns
    ---
    {"username":user_name, "password":password}
    '''
    username = random_lower_string()
    password = random_lower_string()
    user_in = CreateUser(
        first_name=random_lower_string(),
        last_name=random_lower_string(),
        phone_number=random_phone_number(),
        email=random_email(),
        birthday=random_date(),
        user_name=username, 
        password=password,
        salary=random.random() * random.randint(100,1000)
        )
    role = get_role_by_name(session=db, role_name=settings.FIRST_ROLE) 
    create_user(session=db, user_create=user_in, role=role)
    return {"username": username, "password": password}


def create_random_role(*, db= Session) -> str:
    '''
    Create a random role and return the name

    Returns
    ---
    name
    '''
    name = random_lower_string()
    description = random_lower_string()
    role_in = CreateRole(
        name=name,
        description=description,
    )
    create_role(session=db, role_create=role_in)
    return name


def role_clean_up_test(*, db:Session, role_name:str) -> None:
    '''
    Deletes the role specified, to clean up tests
    '''
    role = get_role_by_name(session=db, role_name=role_name)
    db.delete(role)
    db.commit()