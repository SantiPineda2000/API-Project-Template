import pytest

from collections.abc import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy import StaticPool

from src.main import app
from src.config import settings
from src.initial_data import init_db
from src.dependencies import get_db

from tests.utils import (
    get_superuser_token_headers, 
    authentication_token_from_username, 
    terminated_user_authentication_headers_and_password,
    get_admin_token_headers
    )

##=============================================================================================
## CONFIGURATIONS FOR TESTING
##=============================================================================================


# Specifying a testing environment
@pytest.fixture(scope="session", autouse=True)
def set_testing_env():
    settings.TEST = True
    yield
    settings.TEST = False

# Creating a fake in memory data base
SQL_MOCK_DATA_BASE = "sqlite:///:memory:"

engine = create_engine(
    SQL_MOCK_DATA_BASE, 
    connect_args={
        "check_same_thread": False
    },
    poolclass= StaticPool,
)

# Creating a test session
TestingSessionLocal = sessionmaker(
    class_=Session, # Ensure it is compatible with SQLModel
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# Overriding the get_db() function in the main app
def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    yield db
    db.close()

app.dependency_overrides[get_db] = override_get_db

# Starting a session with the in memory database
@pytest.fixture(scope='module', autouse=True)
def db() -> Generator[Session, None, None]:
    # Creating the tables in the in-memory data base
    SQLModel.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    # Creating the initial data for testing
    init_db(session=db_session)
    # Run the init_db()
    yield db_session
    SQLModel.metadata.drop_all(bind=engine)


@pytest.fixture(scope='module')
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope='module')
def super_user_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client=client)


@pytest.fixture(scope='module')
def normal_user_token_headers(client: TestClient, db: Session, super_user_token_headers: dict[str, str]) -> dict[str, str]:
    return authentication_token_from_username(
        client=client, user_name=settings.USERNAME_TEST_USER, db=db, role_name=settings.TEST_ROLE, super_user_token_headers=super_user_token_headers
    )


@pytest.fixture(scope='module')
def admin_user_token_headers(client: TestClient, super_user_token_headers:dict[str, str]) -> dict[str, str]:
    return get_admin_token_headers(client=client, super_user_token_headers=super_user_token_headers)


@pytest.fixture(scope='module')
def terminated_user_token_headers_password(client: TestClient, db: Session, super_user_token_headers:dict[str, str]) -> dict[str, str]:
    return terminated_user_authentication_headers_and_password(client=client, db=db, super_user_token_headers=super_user_token_headers)
