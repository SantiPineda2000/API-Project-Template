import logging

from sqlmodel import Session

from src.db import engine, init_db

# Setting up logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Silence passlib logging errors, because passlib is no longer mantained 
logging.getLogger('passlib').setLevel(logging.ERROR)

def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()