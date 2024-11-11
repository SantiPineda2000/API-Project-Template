from typing import Any, Annotated
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlmodel import func, select
from datetime import date
from pydantic import EmailStr

from src.config import settings
from src.uploads import upload_image
from src.users import service, exceptions, constants
from src.dependencies import CurrentUser, SessionDep, get_current_active_admin, get_current_active_owner
from src.auth.service import get_password_hash, verify_password
from src.users.models import Users, Roles
from src.users.schemas import(
    UpdatePassword, 
    UpdateUser, 
    UserUpdateMe,
    UsersPublic, 
    UserPublicWithoutRoles,
    UserPublicWithRoles,
    Message, 
    CreateUser,
    RolePublic,
    RolesPublic,
    RolePublicWithoutUsers,
    RolesNames,
    CreateRole,
    UpdateRole
)

##=============================================================================================
## COLLABORATOR CRUD ROUTES
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
    # Counting the Users registered in the db
    count_statement = select(func.count()).select_from(Users)
    count = session.exec(statement=count_statement).one()
    # Retrieving the users (max. 10)
    statement = select(Users).offset(skip).limit(limit)
    users = session.exec(statement=statement).all()
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
                        File(description=f"Accepted image files: {' '.join([t.split('/')[-1] for t in constants.ALLOWED_CONTENT_TYPES])}")
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
        if user_image.content_type not in constants.ALLOWED_CONTENT_TYPES:
            raise exceptions.Unsupported_File(supported=constants.ALLOWED_CONTENT_TYPES)
        
        elif user_image.size > constants.MAX_IMAGE_SIZE:
            raise exceptions.File_Too_Large(max_bytes=constants.MAX_IMAGE_SIZE)
        
        # Change the image name but keep the extension
        file_ext = user_image.filename.split('.')[-1]
        user_image.filename = '_'.join([first_name.lower(), last_name.lower(), 'photo']) + f'.{file_ext}'
        
        img_path = await upload_image(sub_dir=constants.USERS_IMAGES_UPLOAD_SUB_DIR, image=user_image, environment=settings.ENVIRONMENT)
    else:
        img_path = None

    user = service.create_user(session=session, user_create=user_in, role=role, img_path=img_path)

    # !!! Add confirmation via [WhatsApp or Email] here !!!

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
                        File(description=f"Accepted image files: {' '.join([t.split('/')[-1] for t in constants.ALLOWED_CONTENT_TYPES])}")
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

    user_in = UpdateUser(**{k: v for k, v in passed_data.items() if v is not None})

    if user_in.username:
        existig_user = service.get_user_by_username(session=session, user_name=user_in.username)
        if existig_user and existig_user.id != current_user.id:
            raise exceptions.User_Already_Exists()
        
    if user_image:
        if user_image.content_type not in constants.ALLOWED_CONTENT_TYPES:
            raise exceptions.Unsupported_File(supported=constants.ALLOWED_CONTENT_TYPES)
        
        elif user_image.size > constants.MAX_IMAGE_SIZE:
            raise exceptions.File_Too_Large(max_bytes=constants.MAX_IMAGE_SIZE)
        
        img_path = await upload_image(constants.USERS_IMAGES_UPLOAD_SUB_DIR, user_image, environment=settings.ENVIRONMENT)
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
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    
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
    user = session.get(Users, user_id)
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
        first_name: Annotated[str, Form()] = None,
        last_name: Annotated[str, Form()] = None,
        user_name: Annotated[str, Form()] = None,
        phone_number: Annotated[str, Form()] = None,
        email: Annotated[EmailStr, Form()] = None,
        birthday: Annotated[date, Form(description="The format is yyyy-mm-dd")] = None,
        salary: Annotated[float, Form()] = None,
        password: Annotated[str, Form()] = None,
        is_admin: Annotated[bool, Form()] = False,
        role_name: Annotated[str, Form()] = None,
        user_image: Annotated[
                    UploadFile | None, 
                    File(description=f"Accepted image files: {' '.join([t.split('/')[-1] for t in constants.ALLOWED_CONTENT_TYPES])}")
                ] = None
        ) -> Any:
    '''
    Update a user (administrators and owners only).
    '''
    db_user = session.get(Users, user_id)
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

    user_in = UpdateUser(**{k: v for k, v in passed_data.items() if v is not None})

    if user_in.user_name:
        existing_user = service.get_user_by_username(session=session, user_name=user_in.user_name)
        if existing_user and existing_user.id != user_id:
            raise exceptions.Username_Conflict()
        
    # Get the role from the 'role_name' if passed, else set it to None
    if "role_name" in user_in:
        role = service.get_role_by_name(session=session, role_name=user_in.role_name)
        if not role:
            raise exceptions.Role_Not_Found()
    else:
        role = None

    if user_image:
        if user_image.content_type not in constants.ALLOWED_CONTENT_TYPES:
            raise exceptions.Unsupported_File(supported=constants.ALLOWED_CONTENT_TYPES)
        
        elif user_image.size > constants.MAX_IMAGE_SIZE:
            raise exceptions.File_Too_Large(max_bytes=constants.MAX_IMAGE_SIZE)
        
        img_path = await upload_image(constants.USERS_IMAGES_UPLOAD_SUB_DIR, user_image, environment=settings.ENVIRONMENT)
    else:
        img_path = None

    db_user = service.update_user(session=session, db_user=db_user, user_in=user_in, role=role, img_path=img_path)
    return db_user


@user_routes.patch(
        "/{user_id}/terminate",
        dependencies=[Depends(get_current_active_owner)], # Only owners can terminate a user
        response_model=UserPublicWithoutRoles
)
def terminate_user(*, session:SessionDep, user_id: int, terminate: bool = False):
    '''
    Terminate a user (owners only)
    '''
    db_user = session.get(Users, user_id)
    if not db_user:
        raise exceptions.User_Not_Found()
    
    if terminate:
        db_user.terminated_at = date.today()
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    
    return db_user
    

@user_routes.delete(
        "/{user_id}", 
        dependencies=[Depends(get_current_active_owner)]
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
    
    session.delete(user)
    session.commit()
    
    return Message(message="User deleted successfully!")


##=============================================================================================
## ROLES CRUD ROUTES
##=============================================================================================


roles_routes = APIRouter()


@roles_routes.get(
        "/",
        dependencies=[Depends(get_current_active_admin)], # Only admins can view roles
        response_model=RolesPublic | RolesNames
)
def read_roles(*, session: SessionDep, skip: int = 0, limit: int = 10, just_names: bool = False) -> RolePublic | RolesNames:
    '''
    Retrieve roles
    '''
    # Counting the Roles registered in the db
    count_statement = select(func.count()).select_from(Roles)
    count = session.exec(statement=count_statement).one()
    # Retrieving the Roles (max. 10)
    statement = select(Roles).offset(skip).limit(limit)
    roles = session.exec(statement=statement).all()

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
    Retrieve roles by id
    '''
    role = session.get(Roles, role_id)

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
    db_role = session.get(Roles, role_id)

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
    role = session.get(Roles, role_id)
    if not role:
        raise exceptions.Role_Not_Found()
    
    # Avoid deleting a role if user(s) have it linked.
    if len(role.users) >= 1:
        raise exceptions.Role_In_Use()
    
    session.delete(role)
    session.commit()
    
    return Message(message="Role deleted successfully!")