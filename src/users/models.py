from datetime import date
from pydantic_extra_types.phone_numbers import PhoneNumber
from pydantic import EmailStr

from sqlmodel import Field, Relationship
from sqlmodel import SQLModel

##=============================================================================================
## SQLMODELS
##=============================================================================================

# Users

class BaseUser(SQLModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    birthday: date
    phone_number: PhoneNumber
    email: EmailStr = Field(max_length=50, nullable=False)

class Users(BaseUser, table=True):
    id: int | None = Field(default=None, primary_key=True)
    terminated_at: date | None = Field(default=None)
    img_path: str | None = Field(default=None)
    user_name: str = Field(max_length=50)
    hashed_password: str
    is_admin: bool | None = Field(default=False)
    is_owner: bool | None = Field(default=False)
    salary: float
    register_date: date | None = Field(default_factory=lambda: date.today())

    # Relationships
    roles_id: int = Field(foreign_key="roles.id", ondelete="RESTRICT")
    role: "Roles" = Relationship(back_populates="users")


# Roles

class BaseRolDep(SQLModel):
    name: str = Field(max_length=50)
    description: str | None = Field(default=None, max_length=255)

class Roles(BaseRolDep, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date_created: date | None = Field(default_factory=lambda: date.today())

    # Relationships
    users: list[Users] = Relationship(back_populates="role")
 