
from sqlmodel import Session

from src.users import service
from src.auth.service import verify_password
from src.users.models import Users
from src.users.schemas import CreateUser

##=============================================================================================
## USERS TESTS
##=============================================================================================

