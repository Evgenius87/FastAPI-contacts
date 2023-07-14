import unittest
from datetime import date, datetime
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contacts, User
from src.schemas import ContactsModel, ContactsUpdate, ContactsStatusUpdate
from src.repository.contacts import (
    get_contact,
    get_contacts,
    create_contact,
    remove_contact,
    update_contact,
    update_status_contact,
    get_contacts_with_birthdays,
)

class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contacts(), Contacts(), Contacts()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=3, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contacts()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactsModel(
            first_name="Taras",
            last_name="Shevchenko",
            email="hfhghgc@gmail.com",
            phone_number="803123123",
            born_date=date(2005, 2, 3)
        )
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.born_date, body.born_date)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_contact_found(self):
        body = ContactsModel(
            first_name="Taras",
            last_name="Shevchenko",
            email="hfhghgc@gmail.com",
            phone_number="803123123",
            born_date=date(2005, 2, 3)
        )
        contact = ContactsModel(
            first_name="Andriy",
            last_name="Shevchenko",
            email="hfhghgc@gmail.com",
            phone_number="803123123",
            born_date=date(2005, 2, 3)
        )
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactsModel(
            first_name="Taras",
            last_name="Sevchenko",
            email="hfhghgc@gmail.com",
            phone_number="803123123",
            born_date=date(2005, 2, 3)
        )
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_remove_contact_found(self):
        contact = Contacts()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_contact_by_birthday_found(self):
        contact = [Contacts(born_date=date(datetime.now().year, datetime.now().month, datetime.now().day))]
        self.session.query().filter().all.return_value = contact
        result = await get_contacts_with_birthdays(db=self.session, user=self.user)
        self.assertNotEqual(result, contact)



if __name__ == '__main__':
    unittest.main()