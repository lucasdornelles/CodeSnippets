from unittest import TestCase
from database import User, Tagmap, Tag, Bookmark, Snippet
from sqlite3 import OperationalError


class TestDatabase(TestCase):

    def test_check_password(self):
        user = User(name='name', password='password')
        self.assertTrue(user.check_password(password='password'))
        self.assertFalse(user.check_password(password='pass'))
