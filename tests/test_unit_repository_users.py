import unittest
from typing import Sequence
from unittest.mock import MagicMock, AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user import UserSchema, UserResponse
from src.entity.models import User
from src.repository.users import get_user_by_email, create_user, email_verified, update_token, update_avatar_url


class TestAsyncUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user = User(id=1, username='Tsiri',
                         email='I_am_cat_not@catmail.com',
                         email_verified=False,
                         refresh_token='refresh_token',
                         avatar = "base_avatar")
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_user_by_email(self):
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_user
        result = await get_user_by_email(self.user.email, self.session)
        self.assertEqual(result, self.user)
        self.session.execute.assert_called_once()

    @patch('src.repository.users.Gravatar')
    async def test_create_user(self, mock_gravatar):
        body = UserSchema(username="Tsiri", password="12345", email="I_am_cat_not@catmail.com")
        mock_gravatar.return_value.get_image.return_value = 'gravatar_url'
        result = await create_user(body, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(body.username, result.username)
        self.assertEqual(body.email, result.email)
        self.assertEqual(result.avatar, 'gravatar_url')
        mock_gravatar.return_value.get_image.assert_called_once()
        mock_gravatar.assert_called_once_with(body.email)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        self.session.add.assert_called_once()

    @patch('src.repository.users.get_user_by_email')  #
    async def test_email_verified(self, mock_get_user_by_email):
        mock_get_user_by_email.return_value = self.user
        await email_verified(self.user.email, self.session)
        self.assertEqual(self.user.email_verified, True)
        mock_get_user_by_email.assert_called_once_with(self.user.email, self.session)
        self.session.commit.assert_called_once()

    async def test_update_token(self):
        new_token = 'new_token'
        await update_token(self.user, new_token, self.session)
        self.assertEqual(self.user.refresh_token, new_token)
        self.session.commit.assert_called_once()

    @patch('src.repository.users.get_user_by_email')  #
    async def test_update_avatar_url(self, mock_get_user_by_email):
        url = "new_avatar"
        mock_get_user_by_email.return_value = self.user
        await update_avatar_url(self.user.email, url, self.session)
        self.assertEqual(self.user.avatar, url)
        mock_get_user_by_email.assert_called_once_with(self.user.email, self.session)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
