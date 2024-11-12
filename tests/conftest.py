from collections.abc import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.dependencies import get_db

DATABASE_URL = "sqlite:///:memory:" # In memory TEST database

# Engine settings for connecting to the in memory database
test_engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool
)

TestSessionLocal = sessionmaker(class_=Session ,autocommit=False, autoflush=False, bind=test_engine)

client = TestClient(app)

# Testing session dependency 
def override_get_db() -> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Overriding the get_db() dependency with the testing one [override_get_db()]
app.dependency_overrides[get_db] = override_get_db