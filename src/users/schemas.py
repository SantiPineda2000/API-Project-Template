from datetime import date
from pydantic_extra_types.phone_numbers import PhoneNumber
from pydantic import EmailStr
from sqlmodel import SQLModel, Field

from src.users.models import BaseRolDep, BaseUser

##=============================================================================================
## SCHEMAS RECIEVED BY THE API
##=============================================================================================

# ON CREATION
# ---------------------------------------------------------------------------------------------

# Users

class CreateUser(BaseUser):
    user_name: str = Field(max_length=50)
    password: str = Field(min_length=8, max_length=40)
    is_admin: bool | None = Field(default=False)
    is_owner: bool | None = Field(default=False)
    salary: float

class NewPassword(SQLModel): # New pass
    token: str
    new_password: str = Field(min_length=8, max_length=40)

# Roles

class CreateRole(BaseRolDep):
    pass


# ON UPDATE (all optional)
# ---------------------------------------------------------------------------------------------

# Users

class UpdateUser(SQLModel):
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    username: str | None = Field(default=None, max_length=50)
    phone_number: PhoneNumber | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    user_name: str | None = Field(default=None, max_length=50)
    birthday: date | None = Field(default=None)
    password: str | None= Field(default=None, min_length=8, max_length=40)
    is_admin: bool | None = Field(default=False)
    salary: float | None = Field(default=None)
    role_name: str | None = Field(default=None)

class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)

class UserUpdateMe(SQLModel):
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    username: str | None = Field(default=None, max_length=50)
    birthday: date | None = Field(default=None)
    password: str | None= Field(default=None, min_length=8, max_length=40)
    phone_number: PhoneNumber | None = Field(default=None)

# Roles

class UpdateRole(SQLModel):
    name: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=255)


##=============================================================================================
## SCHEMAS RETURNED BY THE API
##=============================================================================================

# Users

class UserPublicWithRoles(BaseUser): # User with roles
    id: int
    register_date: date | None
    terminated_at: date | None
    img_path: str | None
    user_name: str
    is_admin: bool
    is_owner: bool
    salary: float
    role: BaseRolDep

class UserPublicWithoutRoles(BaseUser): # User without roles
    id: int
    register_date: date | None
    terminated_at: date | None
    img_path: str | None
    user_name: str
    is_admin: bool
    is_owner: bool
    salary: float

class UsersPublic(SQLModel): # List of users with roles
    data: list[UserPublicWithRoles]
    count: int

# Roles

class RolePublic(BaseRolDep): # Role with users without roles
    id: int
    users: list[UserPublicWithoutRoles]

class RolePublicWithoutUsers(BaseRolDep):
    id: int

class RolesPublic(SQLModel): # List of RolePublic objects
    data: list[RolePublic]
    count: int

class RolesNames(SQLModel): # List of Role's names
    role_names: list[str]
