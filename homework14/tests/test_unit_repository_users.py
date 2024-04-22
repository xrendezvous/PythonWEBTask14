import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import User
from src.repository.users import update_avatar
from fastapi import HTTPException


class TestUserRepository(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock(spec=Session)
        self.email = "user@example.com"
        self.new_avatar_url = "http://example.com/new-avatar.jpg"

    def test_update_avatar_user_found(self):
        user = User(email=self.email, avatar_url="http://example.com/old-avatar.jpg")
        self.db.query.return_value.filter.return_value.first.return_value = user

        updated_user = update_avatar(self.email, self.new_avatar_url, self.db)

        self.db.commit.assert_called_once()
        self.assertEqual(updated_user.avatar_url, self.new_avatar_url)

    def test_update_avatar_user_not_found(self):
        self.db.query.return_value.filter.return_value.first.return_value = None

        with self.assertRaises(HTTPException) as context:
            update_avatar(self.email, self.new_avatar_url, self.db)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "User not found")
        self.db.commit.assert_not_called()


if __name__ == '__main__':
    unittest.main()
