from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas import Message
from src.dependencies import SessionDep
from src.auth import service, exceptions
from src.config import settings
from src.auth.shcemas import Token, NewPassword
from src.users.service import authenticate, get_user_by_username, update_hash_password
from src.users.exceptions import User_Not_Found, Terminated_User
from src.mail.utils import generate_reset_password_email
from src.mail.service import send_email

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

# Email sending endpoint
@auth_routes.post("/password-recovery/{email}")
def recover_password(user_name: str, session: SessionDep) -> Message:
    '''
    Password Recovery, through an email sent to the user's email
    '''
    user = get_user_by_username(session=session, user_name=user_name)

    if not user:
        raise User_Not_Found()
    
    if user.email is None:
        raise exceptions.Email_Not_Registered()

    # Creating the reset token
    password_reset_token = service.generate_password_reset_token(username=user.user_name)
    
    # Generating the email from template
    email_data = generate_reset_password_email(email_to=user.email, token=password_reset_token, username=user_name)
    # Sending the email
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content
    )
    return Message(message="Password recovery email sent")


# Recovery endpoint
@auth_routes.post("/reset-password")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    '''
    Reset password
    '''
    user_name = service.verify_password_reset_token(token=body.token)
    
    if not user_name:
        raise exceptions.Invalid_Token()
    
    user = get_user_by_username(session=session, user_name=user_name)

    if not user:
        raise User_Not_Found()
    elif user.terminated_at is not None:
        raise Terminated_User()
    
    # Using the service function at src.users.service to update the password
    message = update_hash_password(session=session, db_user=user, password=body.new_password)

    return Message(message=message)