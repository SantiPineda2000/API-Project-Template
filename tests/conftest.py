import pytest

from collections.abc import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from src.main import app
from src.config import settings
from src.db import init_db, engine
from src.users.models import Users, Roles
from tests.utils import get_superuser_token_headers, authentication_token_from_username

# Starting a session with the in memory database
@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(Users)
        session.exec(statement)
        statement = delete(Roles)
        session.exec(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def super_user_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client=client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_username(
        client=client, user_name=settings.USERNAME_TEST_USER, db=db, role_name=settings.TEST_ROLE
    )