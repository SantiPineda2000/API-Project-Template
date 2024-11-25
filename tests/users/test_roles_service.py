import pytest

from sqlmodel import Session

from src.config import settings
 
from src.users.service import create_role, update_role, delete_role, get_role_by_name, get_role_by_id
from src.users.schemas import UpdateRole
from src.users.models import Roles

from tests.users.utils import create_random_role

##=============================================================================================
## ROLES SERVICE TESTS
##=============================================================================================

# Create roles tests
# ---------------------------------------------------------------------------------------------

# Test creating a role
def test_create_role(db: Session):
    role_data = Roles(name="Manager")
    created_role = create_role(session=db, role_create=role_data)

    assert created_role.id is not None
    assert created_role.name == "Manager"

# Retrieve roles by name tests
# ---------------------------------------------------------------------------------------------

# Test retrieving a role by name (existing role)
def test_get_role_by_name_found(db:Session):
    role = get_role_by_name(session=db, role_name=settings.FIRST_ROLE)
    assert role is not None
    assert role.name == settings.FIRST_ROLE

# Test retrieving a role by name (nonexistent role)
def test_get_role_by_name_not_found(db:Session):
    role = get_role_by_name(session=db, role_name="NonexistentRole")
    assert role is None

# Retrieve roles by id tests
# ---------------------------------------------------------------------------------------------

# Test retrieving a role by ID (existing role)
def test_get_role_by_id_found(db:Session):
    role_name = create_random_role(db=db)
    role_og = get_role_by_name(session=db, role_name=role_name)

    role = get_role_by_id(session=db, role_id=role_og.id)
    assert role is not None
    assert role.id == role_og.id

# Test retrieving a role by ID (nonexistent role)
def test_get_role_by_id_not_found(db:Session):
    role = get_role_by_id(session=db, role_id=9999)
    assert role is None


# Updating roles tests
# ---------------------------------------------------------------------------------------------

# Test updating a role
def test_update_role(db:Session):
    role_name = create_random_role(db=db)
    role_og = get_role_by_name(session=db, role_name=role_name)

    update_data = UpdateRole(name="SuperAdmin")
    updated_role = update_role(session=db, db_role=role_og, role_in=update_data)

    assert updated_role.name == "SuperAdmin"


# Deleting roles tests
# ---------------------------------------------------------------------------------------------

# Test deleting a role (existing role)
def test_delete_role(db:Session):
    role_name = create_random_role(db=db)
    role_og = get_role_by_name(session=db, role_name=role_name)

    response = delete_role(session=db, db_role=role_og)

    assert response == f"Role '{role_og.name}' deleted successfully!"
    assert get_role_by_id(session=db, role_id=role_og.id) is None