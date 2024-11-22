import random
from sqlmodel import Session
from fastapi.testclient import TestClient

from src.config import settings
from src.users.service import get_role_by_name, get_user_by_username
from tests.users.utils import role_clean_up_test, create_random_role, create_random_user
from tests.utils import random_lower_string

##=============================================================================================
## ROLES ROUTER TESTS
##=============================================================================================

# Tests for route "/"
# ---------------------------------------------------------------------------------------------

def test_get_all_roles_super_user(
        client: TestClient, super_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        url=f"{settings.API_V1_STR}/roles/",
        headers=super_user_token_headers
    )
    response = r.json()
    assert r.status_code == 200
    assert type(response["data"]) == list
    assert response["count"] == 1
    assert type(response["data"][0]) == dict


def test_get_all_roles_admin_user(
        client: TestClient, admin_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        url=f"{settings.API_V1_STR}/roles/",
        headers=admin_user_token_headers
    )
    response = r.json()
    assert r.status_code == 200
    assert type(response["data"]) == list
    assert response["count"] == 1


def test_get_all_roles_normal_user(
        client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        url=f"{settings.API_V1_STR}/roles/",
        headers=normal_user_token_headers
    )
    response = r.json()
    assert r.status_code == 403
    assert response["detail"] == "The user doesn't have enough privileges"


def test_get_all_roles_names(
        client: TestClient, super_user_token_headers: dict[str,str]
) -> None:
    r = client.get(
        url=f"{settings.API_V1_STR}/roles/",
        headers=super_user_token_headers,
        params={"just_names":True}
    )
    response = r.json()
    assert r.status_code == 200
    assert type(response["role_names"]) == list


def test_create_role_super_user(
        client:TestClient, super_user_token_headers:dict[str, str], db: Session
) -> None:
    role_name = random_lower_string()
    role_description = random_lower_string()
    role_in = {
        "name":role_name, 
        "description":role_description,
    }
    r = client.post(
        url=f"{settings.API_V1_STR}/roles/",
        headers=super_user_token_headers,
        json=role_in
    )
    response = r.json()
    assert r.status_code == 200
    assert response["name"] == role_name
    assert response["description"] == role_description
    role_clean_up_test(db=db, role_name=role_name)


def test_create_role_admin_user(
        client:TestClient, admin_user_token_headers:dict[str, str], db: Session
) -> None:
    role_name = random_lower_string()
    role_description = random_lower_string()
    role_in = {
        "name":role_name, 
        "description":role_description,
    }
    r = client.post(
        url=f"{settings.API_V1_STR}/roles/",
        headers=admin_user_token_headers,
        json=role_in
    )
    response = r.json()
    assert r.status_code == 200
    assert response["name"] == role_name
    assert response["description"] == role_description
    role_clean_up_test(db=db, role_name=role_name)


def test_create_role_normal_user(
        client:TestClient, normal_user_token_headers:dict[str, str]
) -> None:
    role_name = random_lower_string()
    role_description = random_lower_string()
    role_in = {
        "name":role_name, 
        "description":role_description,
    }
    r = client.post(
        url=f"{settings.API_V1_STR}/roles/",
        headers=normal_user_token_headers,
        json=role_in
    )
    response = r.json()
    assert r.status_code == 403
    assert response["detail"] == "The user doesn't have enough privileges"


def test_create_role_conflicting_name(
        client:TestClient, super_user_token_headers: dict[str, str], db: Session
) -> None:
    # Create a random role
    role_name = create_random_role(db=db)
    role_in = {
        "name":role_name, 
    }
    r = client.post(
        url=f"{settings.API_V1_STR}/roles/",
        headers=super_user_token_headers,
        json=role_in
    )
    response = r.json()
    assert r.status_code == 409
    assert response["detail"] == "Role with this name already exists"
    role_clean_up_test(db=db, role_name=role_name)


# Tests for route "/{role_id}"
# ---------------------------------------------------------------------------------------------

def test_read_role_super_user(
        client: TestClient, super_user_token_headers:dict[str, str], db: Session
) -> None:
    # Getting the role 
    role_db = get_role_by_name(session=db, role_name=settings.TEST_ROLE)
    r = client.get(
        url=f"{settings.API_V1_STR}/roles/{role_db.id}",
        headers=super_user_token_headers,
    )
    response = r.json()
    assert r.status_code == 200
    assert type(response) == dict
    assert "users" in response.keys()
    assert type(response["users"]) == list


def test_read_role_admin_user(
        client: TestClient, admin_user_token_headers:dict[str, str], db: Session
) -> None:
    # Getting the role 
    role_db = get_role_by_name(session=db, role_name=settings.TEST_ROLE)
    r = client.get(
        url=f"{settings.API_V1_STR}/roles/{role_db.id}",
        headers=admin_user_token_headers,
    )
    response = r.json()
    assert r.status_code == 200
    assert type(response) == dict
    assert "users" in response.keys()
    assert type(response["users"]) == list


def test_read_role_normal_user(
        client: TestClient, normal_user_token_headers:dict[str, str], db: Session
) -> None:
    # Getting the role 
    role_db = get_role_by_name(session=db, role_name=settings.TEST_ROLE)
    r = client.get(
        url=f"{settings.API_V1_STR}/roles/{role_db.id}",
        headers=normal_user_token_headers,
    )
    response = r.json()
    assert r.status_code == 403
    assert response["detail"] == "The user doesn't have enough privileges"


def test_read_not_existing_role(
        client: TestClient, super_user_token_headers:dict[str, str], db: Session
) -> None:
    r = client.get(
        url=f"{settings.API_V1_STR}/roles/{random.randint(20, 50)}",
        headers=super_user_token_headers,
    )
    response = r.json()
    assert r.status_code == 404
    assert response["detail"] == "The role provided does not exist in the system."


def test_update_role_super_user(
         client: TestClient, super_user_token_headers:dict[str, str], db: Session
) -> None:
    # Creating a random role
    role_first_name = create_random_role(db=db)
    # Getting the role 
    role_db = get_role_by_name(session=db, role_name=role_first_name)
    # Update Data
    role_name = random_lower_string()
    role_description = random_lower_string()
    role_update = {
            "name": role_name,
            "description": role_description
        }
    r = client.patch(
        url=f"{settings.API_V1_STR}/roles/{role_db.id}",
        headers=super_user_token_headers,
        json=role_update
    )
    response = r.json()
    assert r.status_code == 200
    assert type(response) == dict
    assert response["name"] == role_name
    assert response["description"] == role_description
    role_clean_up_test(db=db, role_name=role_name)


def test_update_role_admin_user(
         client: TestClient, admin_user_token_headers:dict[str, str], db: Session
) -> None:
    # Creating a random role
    role_first_name = create_random_role(db=db)
    # Getting the role 
    role_db = get_role_by_name(session=db, role_name=role_first_name)
    # Update Data
    role_name = random_lower_string()
    role_description = random_lower_string()
    role_update = {
            "name": role_name,
            "description": role_description
        }
    r = client.patch(
        url=f"{settings.API_V1_STR}/roles/{role_db.id}",
        headers=admin_user_token_headers,
        json=role_update
    )
    response = r.json()
    assert r.status_code == 200
    assert type(response) == dict
    assert response["name"] == role_name
    assert response["description"] == role_description
    role_clean_up_test(db=db, role_name=role_name)


def test_update_role_normal_user(
         client: TestClient, normal_user_token_headers:dict[str, str], db: Session
) -> None:
    # Creating a random role
    role_first_name = create_random_role(db=db)
    # Getting the role 
    role_db = get_role_by_name(session=db, role_name=role_first_name)
    # Update Data
    role_name = random_lower_string()
    role_description = random_lower_string()
    role_update = {
            "name": role_name,
            "description": role_description
        }
    r = client.patch(
        url=f"{settings.API_V1_STR}/roles/{role_db.id}",
        headers=normal_user_token_headers,
        json=role_update
    )
    response = r.json()
    assert r.status_code == 403
    assert response["detail"] == "The user doesn't have enough privileges"


def test_update_role_not_found(
         client: TestClient, super_user_token_headers:dict[str, str], db: Session
) -> None:
    # Update Data
    role_name = random_lower_string()
    role_description = random_lower_string()
    role_update = {
            "name": role_name,
            "description": role_description
        }
    r = client.patch(
        url=f"{settings.API_V1_STR}/roles/{random.randint(20,50)}",
        headers=super_user_token_headers,
        json=role_update
    )
    response = r.json()
    assert r.status_code == 404
    assert response["detail"] == "The role provided does not exist in the system."


def test_update_role_conflicting_name(
         client: TestClient, super_user_token_headers:dict[str, str], db: Session
) -> None:
    # Creating a random role
    role_first_name = create_random_role(db=db)
    # Getting the role 
    role_db = get_role_by_name(session=db, role_name=role_first_name)
    # Update Data
    role_name = settings.FIRST_ROLE
    role_description = random_lower_string()
    role_update = {
            "name": role_name,
            "description": role_description
        }
    r = client.patch(
        url=f"{settings.API_V1_STR}/roles/{role_db.id}",
        headers=super_user_token_headers,
        json=role_update
    )
    response = r.json()
    assert r.status_code == 400
    assert response["detail"] == "This role already exists in the system."


def test_delete_role_super_user(
        client: TestClient, super_user_token_headers:dict[str, str], db: Session
) -> None:
    # Creating a random role
    role_name = create_random_role(db=db)
    # Getting the role 
    role_db = get_role_by_name(session=db, role_name=role_name)
    r = client.delete(
        url=f"{settings.API_V1_STR}/roles/{role_db.id}",
        headers=super_user_token_headers,
    )
    response = r.json()
    assert r.status_code == 200
    assert response["message"] == f"Role '{role_name}' deleted successfully!"


def test_delete_role_admin_user(
        client: TestClient, admin_user_token_headers:dict[str, str], db: Session
) -> None:
    # Creating a random role
    role_name = create_random_role(db=db)
    # Getting the role 
    role_db = get_role_by_name(session=db, role_name=role_name)
    r = client.delete(
        url=f"{settings.API_V1_STR}/roles/{role_db.id}",
        headers=admin_user_token_headers,
    )
    response = r.json()
    assert r.status_code == 200
    assert response["message"] == f"Role '{role_name}' deleted successfully!"


def test_delete_role_normal_user(
        client: TestClient, normal_user_token_headers:dict[str, str], db: Session
) -> None:
    # Creating a random role
    role_name = create_random_role(db=db)
    # Getting the role 
    role_db = get_role_by_name(session=db, role_name=role_name)
    r = client.delete(
        url=f"{settings.API_V1_STR}/roles/{role_db.id}",
        headers=normal_user_token_headers,
    )
    response = r.json()
    assert r.status_code == 403
    assert response["detail"] == "The user doesn't have enough privileges"
    role_clean_up_test(db=db, role_name=role_name)


def test_delete_role_not_found(
        client: TestClient, super_user_token_headers:dict[str, str],
) -> None:
    r = client.delete(
        url=f"{settings.API_V1_STR}/roles/{random.randint(20, 50)}",
        headers=super_user_token_headers,
    )
    response = r.json()
    assert r.status_code == 404
    assert response["detail"] == "The role provided does not exist in the system."


def test_delete_role_linked_user(
        client: TestClient, super_user_token_headers: dict[str, str], db: Session
) -> None:
    # Creating a random role
    role_name = create_random_role(db=db)
    role_db = get_role_by_name(session=db, role_name=role_name)
    # Creating a random user linked to the role
    random_user = create_random_user(db=db)
    user_db = get_user_by_username(session=db, user_name=random_user["username"])
    # Linking the user to the role
    client.patch(
        url=f"{settings.API_V1_STR}/users/{user_db.id}",
        headers=super_user_token_headers,
        data={"role_name":role_name}
    )
    # Deleting the role
    r = client.delete(
        url=f"{settings.API_V1_STR}/roles/{role_db.id}",
        headers=super_user_token_headers
    )
    response = r.json()
    assert r.status_code == 400
    assert response["detail"] == "Role cannot be deleted because it is linked to user(s)."