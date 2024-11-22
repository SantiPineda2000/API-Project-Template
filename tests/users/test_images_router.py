import pytest
import pathlib

from sqlmodel import Session
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from pathlib import Path

from src.main import app
from src.config import settings
from src.users.service import get_user_by_username
from tests.users.utils import create_random_user

##=============================================================================================
## IMAGES ROUTER TESTS
##=============================================================================================

@pytest.mark.anyio
async def test_fetch_image_file(
        client: TestClient,
        normal_user_token_headers: dict[str, str],
        super_user_token_headers: dict[str, str],
        png_accepted_size_image_file: pathlib.Path, 
        db: Session
) -> None:
    # Create a user
    credentials = create_random_user(db=db)
    user_up = get_user_by_username(session=db, user_name=credentials["username"])
    image_file = open(png_accepted_size_image_file, mode="rb")
    # Adding an image to the user
    r = client.patch(
        url=f"{settings.API_V1_STR}/users/{user_up.id}",
        headers=super_user_token_headers,
        files={"user_image":("test_img.png", image_file, "image/png")}
    )
    user_db = r.json()
    og_file_name = user_db["img_path"].split("/")[-1]
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            url=f"{settings.API_V1_STR}/files/images",
            headers=normal_user_token_headers,
            params={"path":user_db["img_path"]}
            )
    headers = response.headers
    file_name = headers.get("content-disposition")
    assert response.status_code == 200
    assert headers["content-type"] == "image/png"
    assert og_file_name in file_name # <- making sure the file returned is the one expected


@pytest.mark.anyio
async def test_fetch_image_not_user() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
         response = await ac.get(
            url=f"{settings.API_V1_STR}/files/images",
            params={"path":"invalid/path"}
            )
    message = response.json()
    assert response.status_code > 400
    assert message["detail"]


@pytest.mark.anyio
async def test_fetch_image_file_not_found(
        normal_user_token_headers: dict[str, str],
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            url=f"{settings.API_V1_STR}/files/images",
            headers=normal_user_token_headers,
            params={"path":"invalid/path"}
            )
    message = response.json()
    assert response.status_code == 400
    assert message["detail"] == "File not found."


@pytest.mark.anyio
async def test_fetch_image_file_not_supported(
    normal_user_token_headers: dict[str, str],
    bmp_accepted_size_image_file: Path
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            url=f"{settings.API_V1_STR}/files/images",
            headers=normal_user_token_headers,
            params={"path":bmp_accepted_size_image_file}
            )
    message = response.json()
    assert response.status_code == 415
    assert message["detail"] == "Unsupported file type."