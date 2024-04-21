from datetime import date
from unittest.mock import MagicMock, Mock, patch, AsyncMock

from tests.conftest import test_user

test_contact = {"name": "test_contact", "last_name": "test_contact", "email": "test_email@gmail.com",
                "phone_number": "123456789", "birthday": "2022-01-01"}


def test_get_me(client, get_access_token, mock_rate_limiter):
    token = get_access_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("rest_api/users/me", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == test_user["email"]
    assert "id" in data


def test_upload_avatar_from_cloudinary(client, get_access_token, mock_rate_limiter, monkeypatch):
    token = get_access_token
    headers = {"Authorization": f"Bearer {token}"}
    uploader_mock = MagicMock()
    monkeypatch.setattr("cloudinary.uploader.upload", uploader_mock)
    uploader_mock.return_value = {"url": "cloudinary_avatar_url"}

    response = client.patch("rest_api/users/avatar", headers=headers, files={"file": ("filename", "image/jpeg")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data[
               "avatar"] == ("https://res.cloudinary.com/fastapihw13/image/upload/c_fill,h_250,"
                             "w_250/v1/FastAPI_contacts/deadpool%40example.com")
