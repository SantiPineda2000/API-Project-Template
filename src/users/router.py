import mimetypes
from typing import Any, Annotated
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from datetime import date
from pydantic import EmailStr
from fastapi.responses import FileResponse
from pathlib import Path

from src.uploads import upload_image
from src.exceptions import Unsupported_File, File_Not_Found
from src.users import service, exceptions
from src.dependencies import CurrentUser, SessionDep, get_current_active_admin, get_current_active_owner, get_current_collaborator
from src.schemas import Message

from src.mail.utils import generate_new_account_email
from src.mail.service import send_email
from src.auth.service import verify_password
from src.users.models import Users, Roles
from src.users.constants import image_const
from src.users.schemas import(
    UpdatePassword, 
    UpdateUser, 
    UserUpdateMe,
    UsersPublic, 
    UserPublicWithoutRoles,
    UserPublicWithRoles, 
    CreateUser,
    RolePublic,
    RolesPublic,
    RolePublicWithoutUsers,
    RolesNames,
    CreateRole,
    UpdateRole,
)

##=============================================================================================
## USERS CRUD ROUTES
##=============================================================================================

user_routes = APIRouter()


@user_routes.get(
    "/", 
    dependencies=[Depends(get_current_active_admin)], # Only admins can view users
    response_model=UsersPublic,
    )
def read_users(*, session: SessionDep, skip: int = 0, limit: int = 10) -> Any:
    '''
    Retrieve users
    '''
    # Retrieving the count and users list from the database
    count, users = service.retrieve_count(session=session, model=Users, skip=skip, limit=limit)
    # Returning the users list and count
    return UsersPublic(data=users, count=count) 


@user_routes.post(
    "/",
    dependencies=[Depends(get_current_active_admin)], # Only admins can create collaborators
    response_model=UserPublicWithRoles
)
async def create_user(
        *,
        session:SessionDep, 
        first_name: Annotated[str, Form()],
        last_name: Annotated[str, Form()],
        phone_number: Annotated[str, Form()],
        email: Annotated[EmailStr, Form()],
        birthday: Annotated[date, Form(description="The format is yyyy-mm-dd")],
        user_name: Annotated[str, Form()],
        salary: Annotated[float, Form()],
        password: Annotated[str, Form()],
        is_admin: Annotated[bool, Form()] = False,
        is_owner: Annotated[bool, Form()] = False,
        role_name: Annotated[str, Form()],
        # Image optional
        user_image: Annotated[
                        UploadFile | None, 
                        File(description=f"Accepted image files: {' '.join([t.split('/')[-1] for t in image_const.ALLOWED_CONTENT_TYPES])}")
                    ] = None
    ) -> Any:
    '''
    Create a user
    '''
    # Assamble user data
    user_in = CreateUser(
        first_name=first_name, 
        last_name=last_name, 
        birthday=birthday, 
        phone_number= '+52' + phone_number, # Making a valid phone number with country code (Mexico)
        email= email,
        user_name=user_name,
        password=password,
        is_admin=is_admin, 
        is_owner=is_owner,
        salary=salary
        )

    user = service.get_user_by_username(session=session, user_name=user_in.user_name)
    if user:
        raise exceptions.User_Not_Found()
    
    role = service.get_role_by_name(session=session, role_name=role_name)
    
    if not role:
        raise exceptions.Role_Not_Found()
    
    if user_image:
        filename = '_'.join([first_name.lower(), last_name.lower(), 'photo'])
        img_path = await upload_image(image_const=image_const, image=user_image, image_name=filename)
    else:
        img_path = None

    user = service.create_user(session=session, user_create=user_in, role=role, img_path=img_path)

    # Generating the email from template
    email_data = generate_new_account_email(email_to=user.email, username=user.user_name, password=password)
    
    # Sending the email
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content
    )

    return user


@user_routes.patch(
        "/me", 
        response_model=UserPublicWithoutRoles
)
async def update_user_me(
    *, 
    session: SessionDep,
    current_user: CurrentUser,
    # Optional update fields
    first_name: Annotated[str, Form()] = None,
    last_name: Annotated[str, Form()] = None,
    phone_number: Annotated[str, Form()] = None,
    email: Annotated[EmailStr, Form()] = None,
    birthday: Annotated[date, Form(description="The format is yyyy-mm-dd")] = None,
    user_name: Annotated[str, Form()] = None,
    password: Annotated[str, Form()] = None,
    user_image: Annotated[
                        UploadFile | None, 
                        File(description=f"Accepted image files: {' '.join([t.split('/')[-1] for t in image_const.ALLOWED_CONTENT_TYPES])}")
                    ] = None
    ) -> Any:
    '''
    Update own user
    '''
    # Assamble user data
    passed_data = {
        "first_name":first_name, 
        "last_name":last_name, 
        "user_name":user_name,
        "phone_number":phone_number,
        "email":email,
        "birthday":birthday,
        "password":password
        }

    not_empty_data = {k: v for k, v in passed_data.items() if v is not None and v !=""}

    user_in = UserUpdateMe(**not_empty_data)

    if user_in.username is not None:
        existig_user = service.get_user_by_username(session=session, user_name=user_in.username)
        if existig_user and existig_user.id != current_user.id:
            raise exceptions.User_Already_Exists()
        
    if user_image:
        filename = '_'.join([current_user.first_name.lower(), current_user.last_name.lower(), 'photo'])
        img_path = await upload_image(image_const=image_const, image=user_image, image_name=filename)
    else:
        img_path = None
        
    db_user = service.update_user(session=session, db_user=current_user, user_in=user_in, img_path=img_path)

    return db_user


@user_routes.patch(
        "/me/password", 
        response_model=Message
)
def update_password_me(*, session: SessionDep, body:UpdatePassword, current_user: CurrentUser) -> Any:
    '''
    Update own password
    '''
    if not verify_password(body.current_password, current_user.hashed_password):
        raise exceptions.Incorrect_Password()
    if body.current_password == body.new_password:
        raise exceptions.Same_Password()
    
    service.update_hash_password(session=session, db_user=current_user, password=body.new_password)
    
    return Message(message="Password updated successfully!")


@user_routes.get(
        "/me", 
        response_model=UserPublicWithRoles
)
def read_user_me(current_user: CurrentUser) -> Any:
    '''
    Get current user
    '''
    return current_user


@user_routes.get(
        "/{user_id}", 
        response_model=Users
)
def read_user_by_id(*, user_id: int, session: SessionDep, current_user: CurrentUser) -> Any:
    '''
    Get a specific user by id.
    '''
    user = service.get_user_by_id(session=session, user_id=user_id)

    if not user:
        raise exceptions.User_Not_Found()
    
    if user == current_user:
        return user
    
    if not current_user.is_admin:
        raise exceptions.Insufficient_Privileges()
    
    return user


@user_routes.patch(
        "/{user_id}", 
        dependencies=[Depends(get_current_active_admin)], # Only admins can update a user
        response_model=UserPublicWithRoles
)
async def update_user(
        *, 
        session: SessionDep, 
        user_id: int,
        # Optional update fields
        first_name: Annotated[str | None, Form()] = None,
        user_name: Annotated[str | None, Form()] = None,
        last_name: Annotated[str | None, Form()] = None,
        phone_number: Annotated[str | None, Form()] = None,
        email: Annotated[EmailStr | None, Form()] = None,
        birthday: Annotated[date | None, Form(description="The format is yyyy-mm-dd")] = None,
        salary: Annotated[float | None, Form()] = None,
        password: Annotated[str | None, Form()] = None,
        is_admin: Annotated[bool | None, Form()] = None,
        role_name: Annotated[str | None, Form()] = None,
        user_image: Annotated[
                    UploadFile | None, 
                    File(description=f"Accepted image files: {' '.join([t.split('/')[-1] for t in image_const.ALLOWED_CONTENT_TYPES])}")
                ] = None
        ) -> Any:
    '''
    Update a user (administrators and owners only).
    '''
    db_user = service.get_user_by_id(session=session, user_id=user_id)
    if not db_user:
        raise exceptions.User_Not_Found()
    
    # Assamble user data
    passed_data = {
        "first_name":first_name, 
        "last_name":last_name, 
        "user_name":user_name,
        "phone_number":phone_number,
        "email":email,
        "birthday":birthday,
        "password":password,
        "is_admin":is_admin,
        "salary":salary, 
        "role_name":role_name
        }
    
    not_empty_data = {k: v for k, v in passed_data.items() if v is not None and v !=""}

    user_in = UpdateUser(**not_empty_data)

    if user_in.user_name is not None:
        existing_user = service.get_user_by_username(session=session, user_name=user_in.user_name)
        if existing_user and existing_user.id != user_id:
            raise exceptions.Username_Conflict()
        
    # Get the role from the 'role_name' if passed, else set it to None
    if user_in.role_name is not None:
        role = service.get_role_by_name(session=session, role_name=user_in.role_name)
        if not role:
            raise exceptions.Role_Not_Found()
    else:
        role = None

    if user_image:
        # Getting the image name from the db_user
        filename = '_'.join([db_user.first_name.lower(), db_user.last_name.lower(), 'photo'])
        img_path = await upload_image(image_const=image_const, image=user_image, image_name=filename)
    else:
        img_path = None

    db_user = service.update_user(session=session, db_user=db_user, user_in=user_in, role=role, img_path=img_path)
    return db_user


@user_routes.patch(
        "/{user_id}/terminate",
        dependencies=[Depends(get_current_active_owner)], # Only owners can terminate a user
)
def terminate_user(*, session:SessionDep, user_id: int, terminate: bool = False) -> Message:
    '''
    Terminate a user (owners only)
    '''
    db_user = session.get(Users, user_id)
    if not db_user:
        raise exceptions.User_Not_Found()
    
    if terminate:
        message = service.terminate_user(session=session, db_user=db_user)
    
    return Message(message=message)
    

@user_routes.delete(
        "/{user_id}", 
        dependencies=[Depends(get_current_active_owner)] # Only owners can delete users
)
def delete_user(*, session: SessionDep, current_user: CurrentUser, user_id: int) -> Message:
    '''
    Delete a user (owners only).
    '''
    user = session.get(Users, user_id)
    if not user:
        raise exceptions.User_Not_Found()
    
    if user == current_user:
        raise exceptions.Self_Delete()
    
    message = service.delete_user(session=session, db_user=user)
    
    return Message(message=message)


##=============================================================================================
## ROLES CRUD ROUTES
##=============================================================================================


roles_routes = APIRouter()


@roles_routes.get(
        "/",
        dependencies=[Depends(get_current_active_admin)], # Only admins can view roles
        response_model=RolesPublic | RolesNames
)
def read_roles(*, session: SessionDep, skip: int = 0, limit: int = 10, just_names: bool = False) -> Any:
    '''
    Retrieve roles
    '''
        # Retrieving the count and users list from the database
    count, roles = service.retrieve_count(session=session, model=Roles, skip=skip, limit=limit)

    if just_names:
        return RolesNames(role_names=[record.name for record in roles])
    
    return RolesPublic(data=roles, count=count) # Returning the roles' list and count


@roles_routes.post(
    "/",
    dependencies=[Depends(get_current_active_admin)], # Only admins can create roles
    response_model=RolePublicWithoutUsers
)
def create_role(*, session:SessionDep, role_in: CreateRole) -> Any:
    '''
    Create a role
    '''
    role = service.get_role_by_name(session=session, role_name=role_in.name)

    if role:
        raise exceptions.Role_Name_Conflict()
    
    role = service.create_role(session=session, role_create=role_in)
    
    return role


@roles_routes.get(
    "/{role_id}",
    dependencies=[Depends(get_current_active_admin)], # Only admins can view roles
    response_model=RolePublic
)
def read_role_by_id(*, session:SessionDep, role_id: int) -> Any:
    '''
    Retrieve role by id
    '''
    role = service.get_role_by_id(session=session, role_id=role_id)

    if not role:
        raise exceptions.Role_Not_Found()
    
    return role


@roles_routes.patch(
    "/{role_id}",
    dependencies=[Depends(get_current_active_admin)], # Only admins can modify roles
    response_model=RolePublicWithoutUsers
)
def update_role(*, session: SessionDep, role_id: int, role_in: UpdateRole) -> Any:
    '''
    Update Role (admins and owners only)
    '''
    db_role = service.get_role_by_id(session=session, role_id=role_id)

    if not db_role:
        raise exceptions.Role_Not_Found()
    
    if role_in.name:
        existing_role = service.get_role_by_name(session=session, role_name=role_in.name)
        
        if existing_role and existing_role.id != db_role.id:
            raise exceptions.Role_Already_Exists()

    db_role = service.update_role(session=session, db_role=db_role, role_in=role_in)

    return db_role


@roles_routes.delete(
    "/{role_id}",
    dependencies=[Depends(get_current_active_admin)] # Only admins can delete roles
)
def delete_roles(*, session: SessionDep, role_id: int) -> Any:
    '''
    Delete a role (admins only)
    '''
    role = service.get_role_by_id(session=session, role_id=role_id)
    if not role:
        raise exceptions.Role_Not_Found()
    
    # Avoid deleting a role if user(s) have it linked.
    if len(role.users) >= 1:
        raise exceptions.Role_In_Use()
    
    message = service.delete_role(session=session, db_role=role)

    return Message(message=message)

##=============================================================================================
## FILE ROUTE
##=============================================================================================

files_router = APIRouter()

@files_router.get(
    "/images",
    dependencies=[Depends(get_current_collaborator)], # For users only
    response_class=FileResponse
)
async def fetch_file(*, path: str = Query(...)) -> Any:
    '''
    File fetching endpoint (development only)
    '''
    # Getting the path
    image_path = Path(path)

    if not image_path.is_file():
        raise File_Not_Found()

    # Getting the image name and type
    image_name = path.split("/")[-1]
    image_type, _ = mimetypes.guess_type(url=image_path)

    if image_type not in image_const.ALLOWED_CONTENT_TYPES:
        raise Unsupported_File()
    
    image = FileResponse(path=path, media_type=image_type, filename=image_name)
    return image