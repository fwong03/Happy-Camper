from unittest import TestCase
from mock import patch
from datetime import datetime

from server import app
from seed import load_regions, load_users, load_bestuses, load_categories
from seed import load_brands, load_products

from model import connect_to_db, db
from model import Rating, User

from make_update_helpers import make_user, check_brand, make_parent_product
from make_update_helpers import make_tent, make_sleeping_bag, make_sleeping_pad
from make_update_helpers import update_parent_product, update_tent
from make_update_helpers import update_sleeping_bag, update_sleeping_pad
from make_update_helpers import calc_avg_star_rating
from search_helpers import search_radius, get_users_in_area, filter_products
from search_helpers import get_products_within_dates, categorize_products
from search_helpers import calc_default_dates, convert_string_to_datetime


class SearchHelpersTestCase(TestCase):

    def test_search_radius(self):
        searchcenter = '94612'
        postalcodes = [('94608',), ('94102',), ('94040',), ('95376',), ('95451',),
                        ('92277',), ('10013',), ('02139',)]

        within10 = search_radius(searchcenter, postalcodes, 10)
        within20 = search_radius(searchcenter, postalcodes, 20)
        within50 = search_radius(searchcenter, postalcodes, 50)
        within60 = search_radius(searchcenter, postalcodes, 60)
        within200 = search_radius(searchcenter, postalcodes, 200)
        within600 = search_radius(searchcenter, postalcodes, 600)
        within3000 = search_radius(searchcenter, postalcodes, 3000)
        shouldbeall = search_radius(searchcenter, postalcodes, 3100)

        self.assertEqual(within10, ['94608'])
        self.assertEqual(sorted(within20), sorted(['94608', '94102']))
        self.assertEqual(sorted(within50), sorted(['94608', '94102', '94040']))
        self.assertEqual(sorted(within60), sorted(['94608', '94102', '94040',
                                                   '95376']))
        self.assertEqual(sorted(within200), sorted(['94608', '94102', '94040',
                                                    '95376', '95451']))
        self.assertEqual(sorted(within600), sorted(['94608', '94102', '94040',
                                                    '95376', '95451', '92277']))
        self.assertEqual(sorted(within3000), sorted(['94608', '94102', '94040',
                                                    '95376', '95451', '92277',
                                                    '10013']))
        self.assertEqual(sorted(shouldbeall), sorted(['94608', '94102', '94040',
                                                      '95376', '95451', '92277',
                                                      '10013', '02139']))

    def test_get_users_in_area(self):
        users_in_area = get_users_in_area(['94612'], 1)
        users_names = []

        for user in users_in_area:
            users_names.append(user.fname)

        self.assertEqual(sorted(users_names), ['Count', 'Trix'])

    # http://www.robotswillkillusall.org/posts/how-to-mock-datetime-in-python/
    # https://pypi.python.org/pypi/mock
    @patch('search_helpers.datetime')
    def test_calc_default_dates(self, mock_dt):
        expected = {'future': datetime(2015, 12, 18),
                    'today_string': '2015-11-18',
                    'today': datetime(2015, 11, 18),
                    'future_string': '2015-12-18'}

        mock_dt.today.return_value = datetime(2015, 11, 18)
        self.assertEqual(calc_default_dates(30), expected)

    def test_convert_string_to_datetime(self):
        test_date = convert_string_to_datetime("2015-11-18")
        self.assertEqual(test_date, datetime(2015, 11, 18))


    def test_calc_avg_star_rating(self):
        rating1 = Rating(rating_id=1, stars=4, comments="abc")
        rating2 = Rating(rating_id=3, stars=2, comments="def")
        rating3 = Rating(rating_id=3, stars=3, comments="ghi")
        ratings = [rating1, rating2, rating3]

        self.assertEqual(calc_avg_star_rating(ratings), 3)





class MakeUpdateTestCase(TestCase):
    def test_make_user(self):
        user1 = User(fname='Michelle', lname='Tanner', street='1709 Broderick Street',
                     city='San Francisco', region_id=1, postalcode='94115',
                     phone=4155556666, email='michelle@tanner.com', password='123')

        user2 = User(fname='Grumpy', lname='Grandpa', street='54 Elizabeth Street #31',
                     city='New York', region_id=2, postalcode='10013',
                     phone=2125556666, email='grumpy@grandpa.com', password='123')

        self.assertEqual(user1.email, 'michelle@tanner.com')
        self.assertEqual(user2.email, 'grumpy@grandpa.com')
        self.assertEqual(user1.region_id, 1)
        self.assertEqual(user2.region_id, 2)



if __name__ == "__main__":
    import unittest

    unittest.main()
