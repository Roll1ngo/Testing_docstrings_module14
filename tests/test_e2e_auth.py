from unittest.mock import MagicMock

import pytest
from sqlalchemy import select

from src.entity.models import User
from tests.conftest import TestingSessionLocal
from src.conf import messages

user_data = {"username": "Tsiri", "email": "catnota@catmail.com", "password": "meowmeow"}


def test_signup(client, monkeypatch):
    monkeypatch.setattr("src.services.email.send_email", MagicMock())
    mock_gravatar = MagicMock()
    mock_gravatar.get_image.return_value = "some_avatar"
    monkeypatch.setattr("src.repository.users.Gravatar", lambda _: mock_gravatar)
    response = client.post("rest_api/auth/signup", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["avatar"] == "some_avatar"
    assert data["email"] == user_data["email"]
    assert "password" not in data
    assert "avatar" in data


def test_repeat_signup(client):
    response = client.post("rest_api/auth/signup", json=user_data)
    data = response.json()
    assert response.status_code == 409
    assert data["detail"] == messages.ACCOUNT_EXIST


def test_login_not_verify_email(client):
    response = client.post("rest_api/auth/login",
                           data={"username": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    data["detail"] = messages.EMAIL_NOT_VERIFY


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).filter(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.email_verified = True
            await session.commit()

    response = client.post("rest_api/auth/login",
                           data={"username": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


#
def test_login_wrong_email(client):
    response = client.post("rest_api/auth/login",
                           data={"username": "wrong_email", "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_EMAIL


def test_login_wrong_pass(client):
    response = client.post("rest_api/auth/login",
                           data={"username": user_data.get("email"), "password": "wrong_password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_PASSWORD


# def test_confirm_email(client, monkeypatch, get_access_token, mock_rate_limiter, get_email_token):
#     monkeypatch.setattr("src.services.email.send_email", Mock())
#
#     with patch.object(auth_service, 'get_email_from_token') as get_mail_mock:
#         get_mail_mock.return_value = test_user.get("email")
#     email_token = get_email_token
#     token = get_access_token
#     headers = {"Authorization": f"Bearer {email_token}"}
#
#     response = client.post(f"rest_api/auth/confirmed_email/{token}",
#                            headers=headers)
#
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["detail"] == messages.EMAIL_VERIFY


def test_request_email_if_user_verified(client):
    response = client.post("rest_api/auth/resent_email", json={"email": user_data.get("email")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {"message": messages.EMAIL_VERIFY}


@pytest.mark.asyncio
async def test_request_email_if_user_not_verified(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).filter(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.email_verified = False
            await session.commit()
            await session.refresh(current_user)

    response = client.post("rest_api/auth/resent_email", json={"email": user_data.get("email")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {"message": messages.CHECK_EMAIL}
