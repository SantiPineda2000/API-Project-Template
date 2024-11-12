from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.dependencies import SessionDep
from src.auth import service, exceptions
from src.config import settings
from src.auth.shcemas import Token
from src.users.service import authenticate

##=============================================================================================
## AUTHORIZATION ROUTES
##=============================================================================================

auth_routes = APIRouter()

@auth_routes.post(
        "/access-token"
)
def login_access_token(
    session: SessionDep, 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    '''
    OAuth2 compatible token login, get an access token for future requests
    '''
    user = authenticate(
        session=session, user_name=form_data.username, password=form_data.password
        )
    if not user:
        raise exceptions.Invalid_Credentials()
    
    elif not user.terminated_at is None:
        raise exceptions.Terminated_User()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return Token(
        access_token=service.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )

# !!! Add password recovery endpoints here !!!