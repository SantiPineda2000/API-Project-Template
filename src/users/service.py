import datetime
from typing import Any, Type
from sqlmodel import Session, select, SQLModel, func

from src.auth.service import get_password_hash, verify_password
from src.users.models import Users, Roles
from src.users.schemas import UpdateUser, CreateUser, UpdateRole

# Users CRUD
# ---------------------------------------------------------------------------------------------

def create_user(*, session: Session, user_create: CreateUser, role: Roles, img_path: str | None = None) -> Users:
    if img_path:
        db_obj = Users.model_validate(
            user_create, update={"hashed_password": get_password_hash(user_create.password), "roles_id": role.id, "img_path":img_path}
        )
    else:
        db_obj = Users.model_validate(
            user_create, update={"hashed_password": get_password_hash(user_create.password), "roles_id": role.id}
        )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user_by_username(*, session: Session, user_name: str) -> Users | None:
    statement = select(Users).where(Users.user_name == user_name)
    session_user = session.exec(statement).first()
    
    return session_user

def get_user_by_id(*, session: Session, user_id: int) -> Users | None:
    session_user = session.get(Users, user_id)
    return session_user

def update_user(*, session: Session, db_user: Users, user_in: UpdateUser, role: Roles | None = None, img_path:str | None = None) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}

    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password # Save hashed password
    
    # Adding the image path if it is passed 
    if img_path: 
        extra_data["img_path"] = img_path
    
    if role:
        extra_data["role"] = role # Updating the role if it is passed
    
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


def update_hash_password(*, session: Session, db_user: Users, password: str) -> str:
    hashed_password = get_password_hash(password=password)
    db_user.hashed_password = hashed_password
    session.add(db_user)
    session.commit()
    
    return "Password updated successfully!"


def terminate_user(*, session: Session, db_user: Users) -> str:
    db_user.terminated_at = datetime.date.today()
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return f"User '{db_user.user_name}' terminated!"

def delete_user(*, session: Session, db_user: Users) -> str:
    session.delete(db_user)
    session.commit()

    return f"User '{db_user.user_name}' deleted successfully!"


# Roles CRUD
# ---------------------------------------------------------------------------------------------

def create_role(*, session:Session, role_create:Roles):
    role_obj = Roles.model_validate(role_create)
    session.add(role_obj)
    session.commit()
    session.refresh(role_obj)
    
    return role_obj

def get_role_by_name(*, session: Session, role_name: str) -> Roles | None:
    statement = select(Roles).where(Roles.name == role_name)
    session_role = session.exec(statement).first()
    
    return session_role

def get_role_by_id(*, session: Session, role_id: int) -> Roles | None:
    session_role = session.get(Roles, role_id)

    return session_role

def update_role(*, session: Session, db_role: Roles, role_in: UpdateRole) -> Any:
    role_data = role_in.model_dump(exclude_unset=True)
    db_role.sqlmodel_update(role_data) # Update the role with the passed data
    db_role.date_created = datetime.date.today() # Update the creation date
    session.add(db_role)
    session.commit()
    session.refresh(db_role)
    
    return db_role

def delete_role(*, session: Session, db_role: Roles) -> str:
    session.delete(db_role)
    session.commit()
    
    return f"Role '{db_role.name}' deleted successfully!"


# Authentication service
# ---------------------------------------------------------------------------------------------

def authenticate(*, session: Session, user_name: str, password: str) -> Users | None:
    db_user = get_user_by_username(session=session, user_name=user_name)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    
    return db_user


# Authentication service
# ---------------------------------------------------------------------------------------------

def retrieve_count(*, session: Session, model: Type[SQLModel] , skip: int, limit: int) -> tuple[int, Any]:
    '''
    Function that counts and retrieves the records of the passed model.

    Returns:
    ---
    count: number of records in the database.
    records: list of record objects from the database.
    '''
    # Counting the records registered in the db
    count_statement = select(func.count()).select_from(model)
    count = session.exec(statement=count_statement).one()
    # Retrieving the records (max. 10)
    statement = select(model).offset(skip).limit(limit)
    records = session.exec(statement=statement).all()
    
    return count, records