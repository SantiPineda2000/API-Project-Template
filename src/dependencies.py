from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from src.auth import service
from src.config import settings
from src.db import engine
from src.auth.shcemas import TokenPayload
from src.users.models import Users

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_collaborator(session: SessionDep, token: TokenDep) -> Users:
    '''Method to get the current collaborator'''
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[service.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    collab = session.get(Users, token_data.sub)
    if not collab:
        raise HTTPException(status_code=404, detail="Collaborator not found")
    if collab.terminated_at is not None:
        raise HTTPException(status_code=400, detail="Inactive collaborator")
    return collab


CurrentUser = Annotated[Users, Depends(get_current_collaborator)]


def get_current_active_owner(current_collab: CurrentUser) -> Users:
    '''Method for validating if a collaborator is an owner'''
    if not current_collab.is_owner:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_collab


def get_current_active_admin(current_collab: CurrentUser) -> Users:
    '''Method for validating if a collaborator is an admin'''
    if not current_collab.is_admin:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges" 
        )
    return current_collab

