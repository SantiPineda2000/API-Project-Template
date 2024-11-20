from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from src.auth import service
from src.config import settings
from src.db import engine
from src.auth.schemas import TokenPayload
from src.auth.exceptions import Terminated_User, Invalid_Credentials
from src.users.models import Users
from src.users.service import get_user_by_id
from src.users.exceptions import Insufficient_Privileges, User_Not_Found

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> Users:
    '''Method to get the current user'''
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[service.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise Invalid_Credentials()
    user = get_user_by_id(session=session, user_id=token_data.sub)
    if not user:
        raise User_Not_Found()
    if user.terminated_at is not None:
        raise Terminated_User()
    return user


CurrentUser = Annotated[Users, Depends(get_current_user)]


def get_current_active_owner(current_user: CurrentUser) -> Users:
    '''Method for validating if a user is an owner'''
    if not current_user.is_owner:
        raise Insufficient_Privileges()
    return current_user


def get_current_active_admin(current_user: CurrentUser) -> Users:
    '''Method for validating if a user is an admin'''
    if not current_user.is_admin:
        raise Insufficient_Privileges()
    return current_user

