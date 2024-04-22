import unittest
from unittest.mock import MagicMock
from datetime import date
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate
from src.repository.contacts import (
    get_contact,
    get_contacts,
    create_contact,
    update_contact,
    delete_contact,
    get_contacts_by_search,
    get_birthdays
)


class TestContactsRepository(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock(spec=Session)
        self.contact_data_create = ContactCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            birthday=date.today(),
            additional_info="No additional info"
        )
        self.contact_data_update = ContactUpdate(
            first_name="Jane",
            last_name="Doe"
        )
        self.contact = Contact(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            birthday=date.today(),
            additional_info="No additional info"
        )

    def test_get_contact_found(self):
        self.db.query().filter().first.return_value = self.contact
        contact = get_contact(db=self.db, contact_id=1)
        self.assertTrue(self.db.query.called)
        self.assertEqual(contact, self.contact)

    def test_get_contact_not_found(self):
        self.db.query().filter().first.return_value = None
        contact = get_contact(db=self.db, contact_id=99)
        self.assertIsNone(contact)

    def test_get_contacts(self):
        self.db.query().offset().limit().all.return_value = [self.contact]
        contacts = get_contacts(db=self.db, skip=0, limit=10)
        self.assertTrue(self.db.query.called)
        self.assertEqual(contacts, [self.contact])

    def test_create_contact(self):
        self.db.add = MagicMock()
        self.db.commit = MagicMock()
        self.db.refresh = MagicMock()
        contact = create_contact(db=self.db, contact_data=self.contact_data_create)
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()

    def test_update_contact_found(self):
        self.db.query().filter().first.return_value = self.contact
        updated_contact = update_contact(db=self.db, contact_id=1, contact_data=self.contact_data_update)
        self.assertIsNotNone(updated_contact)
        self.db.commit.assert_called_once()
        self.assertEqual(updated_contact.first_name, "Jane")

    def test_update_contact_not_found(self):
        self.db.query().filter().first.return_value = None
        updated_contact = update_contact(db=self.db, contact_id=99, contact_data=self.contact_data_update)
        self.assertIsNone(updated_contact)

    def test_delete_contact_found(self):
        self.db.query().filter().first.return_value = self.contact
        self.db.delete = MagicMock()
        self.db.commit = MagicMock()
        result = delete_contact(db=self.db, contact_id=1)
        self.db.delete.assert_called_once()
        self.db.commit.assert_called_once()
        self.assertTrue(result)

    def test_delete_contact_not_found(self):
        self.db.query().filter().first.return_value = None
        result = delete_contact(db=self.db, contact_id=99)
        self.assertFalse(result)

    def test_get_contacts_by_search(self):
        self.db.query().filter().all.return_value = [self.contact]
        contacts = get_contacts_by_search(db=self.db, query="Doe")
        self.assertEqual(contacts, [self.contact])

    def test_get_birthdays(self):
        self.db.query().filter().all.return_value = [self.contact]
        contacts = get_birthdays(db=self.db)
        self.assertEqual(contacts, [self.contact])


if __name__ == '__main__':
    unittest.main()


