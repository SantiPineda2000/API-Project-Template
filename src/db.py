from sqlmodel import Session, create_engine, select

from src.config import settings
from src.users.models import Users, Roles
from src.users.schemas import CreateUser, CreateRole
from src.users import service

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28

def init_db(session: Session) -> None:
    # Initialize the database session
    role = session.exec(
        select(Roles).where(Roles.name == settings.FIRST_ROLE)
    ).first()
    # If the role is not created, create it
    if not role:
        role_in = CreateRole(
            name=settings.FIRST_ROLE
        )
        role = service.create_role(session=session, role_create=role_in)

    user = session.exec(
        select(Users).where(Users.user_name == settings.FIRST_SUPERUSER)
    ).first()
    # If the superuser is not created, create it
    if not user:
        user_in = CreateUser( 
            first_name=settings.FIRST_SUPERUSER_FIRST_NAME,
            last_name=settings.FIRST_SUPERUSER_LAST_NAME,
            phone_number=settings.FIRST_SUPERUSER_PHONENUMBER,
            email=settings.FIRST_SUPERUSER_EMAIL,
            user_name=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_admin=True,
            is_owner=True,
            salary=0.0,
            birthday=settings.FIRST_SUPERUSER_BIRTHDAY
        )
        user = service.create_user(session=session, user_create=user_in, role=role)