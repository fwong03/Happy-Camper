from unittest import TestCase
from mock import patch
from datetime import datetime

from server import app
from model import connect_to_db, db
from seed import load_regions, load_users, load_bestuses, load_categories
from seed import load_brands, load_products
from model import User

class IntegrationTestCase(TestCase):
    def setUp(self):
        self.client = app.test_client()
        connect_to_db(app, "sqlite:///")

        db.create_all()

        load_regions()
        load_users()
        load_bestuses()
        load_categories()
        load_brands()
        load_products()

    def test_find_users(self):
        franken = User.query.filter(User.fname == 'Franken').one()
        self.assertEqual(franken.fname, 'Franken')
        self.assertEqual(franken.email, 'franken@berry.com')



    def test_homepage(self):
        test_client = app.test_client()

        result = test_client.get('/')
        self.assertIn('<p><b>Login Here</b></p>', result.data)

    def tearDown(self):
        pass




if __name__ == "__main__":
    import unittest

    unittest.main()
