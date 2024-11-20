from sqlmodel import Session

from src.users.service import get_user_by_username

##=============================================================================================
## USERS UTILITY FUNCTIONS
##=============================================================================================


def user_clean_up_tests(*, user_name: str, db:Session) -> None:
    '''
    Deletes the passed user_name, to clean up tests
    '''
    db_user = get_user_by_username(session=db, user_name=user_name)
    db.delete(db_user)
    db.commit()