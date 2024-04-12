import unittest
from typing import Sequence
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.contact import ContactSchema
from src.entity.models import User, Contact
from src.repository.contacts import (get_contact, get_contacts,
                                     get_birthdays, create_contact,
                                     update_contact, delete_contact, search_contacts)


class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user = User(id=1, username='test_user')
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [Contact(id=1, name='test', user=self.user),
                    Contact(id=2, name='test2', user=self.user)]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, user=self.user)
        self.assertEqual(result, contacts)
        self.session.execute.assert_called_once()

    async def test_get_contact(self):
        contact = Contact(id=1, name='test', user=self.user)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(contact.id, self.session, user=self.user)
        self.assertEqual(result, contact)
        self.session.execute.assert_called_once()

    async def test_create_contact(self):
        body = ContactSchema(name="Tsiri", last_name="Plushka",
                             email="I_am_cat_not@catmail.com",
                             phone_number="kss_kss_kss",
                             birthday="2023-09-01")
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(body.last_name, result.last_name)
        self.assertEqual(body.birthday, result.birthday)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        self.session.add.assert_called_once()

    async def test_update_contact(self):
        body = ContactSchema(name="Tsiri", last_name="Pluhen_Morden",
                             email="I_am_cat_not@catmail.com",
                             phone_number="+380_kss_kss_kss",
                             birthday="2023-09-01")
        mock_contact = MagicMock()
        mock_contact.scalar_one_or_none.return_value = Contact(id=1, name="Tsiri",
                                                               last_name="Pluchka",
                                                               email="I_am_cat_not@catmail.com",
                                                               phone_number="+380_kss_kss_kss",
                                                               birthday="2023-09-01", user=self.user)

        self.session.execute.return_value = mock_contact
        result = await update_contact(1, body, self.session, user=self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.last_name, body.last_name)
        self.session.execute.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        mock_contact.scalar_one_or_none.assert_called_once()

    async def test_delete_contact(self):
        mock_contact = MagicMock()
        mock_contact.scalar_one_or_none.return_value = Contact(id=1, name="Tsiri",
                                                               last_name="Pluchka",
                                                               email="I_am_cat_not@catmail.com",
                                                               phone_number="+380_kss_kss_kss",
                                                               birthday="2023-09-01", user=self.user)
        self.session.execute.return_value = mock_contact
        result = await delete_contact(1, self.session, user=self.user)
        self.assertEqual(result, mock_contact.scalar_one_or_none.return_value)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertIsInstance(result, Contact)
        self.session.execute.assert_called_once()
        mock_contact.scalar_one_or_none.assert_called_once()

    async def test_get_birthdays(self):
        contacts = [Contact(id=1, name='test', user=self.user),
                    Contact(id=2, name='test2', user=self.user)]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_birthdays(self.session, self.user)
        self.session.execute.assert_called_once()
        self.assertIsInstance(result, Sequence)

    async def test_search_contacts(self):
        search_string = ""
        contacts = [Contact(id=1, name='test', user=self.user),
                    Contact(id=2, name='test2', user=self.user)]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await search_contacts(search_string,self.session, self.user)
        self.session.execute.assert_called_once()
        self.assertIsInstance(result, Sequence)
        self.assertEqual(result, contacts)



