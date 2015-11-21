from unittest import TestCase
import os
import tempfile
from mock import patch
from datetime import datetime

from server import app
from model import connect_to_db, db
from seed import load_regions, load_users, load_bestuses, load_categories
from seed import load_brands, load_products, load_tents, load_filltypes
from seed import load_gendertypes, load_sleepingbags, load_padtypes
from seed import load_sleepingpads, load_ratings, load_histories
from model import User, Brand, Product, Tent, Category, Rating

from make_update_helpers import check_brand, make_brand, get_brand_id
from search_helpers import get_users_in_area, filter_products, convert_string_to_datetime
from search_helpers import get_products_within_dates, categorize_products

from make_update_helpers import calc_avg_star_rating
from search_helpers import search_radius, calc_default_dates


class IntegrationTestCase(TestCase):
    def setUp(self):

        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, "sqlite:////tmp/temp.db")

        db.create_all()

        load_regions()
        load_users()
        load_bestuses()
        load_categories()
        load_brands()
        load_products()
        load_tents()
        load_filltypes()
        load_gendertypes()
        load_sleepingbags()
        load_padtypes()
        load_sleepingpads()
        load_ratings()
        load_histories()

    def tearDown(self):
        # can put in here the python (os) to remove a file r
        db.session.remove()
        os.remove("////tmp/temp.db")


    def test_find_users(self):
        franken = User.query.filter(User.fname == 'Franken').one()
        self.assertEqual(franken.fname, 'Franken')
        self.assertEqual(franken.email, 'franken@berry.com')

    def test_homepage(self):
        result = self.client.get('/')
        self.assertEqual(result.status_code, 200)
        self.assertIn('<p><b>Login Here</b></p>', result.data)

    def test_login(self):

        result = self.client.post('/handle-login', data={'email': 'franken@berry.com',
                                  'password': 'abc'}, follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn('<h2>Your options are the following:</h2>', result.data)

    def test_handle_tent_listing(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = 'franken@berry.com'
                print "\n\nAll Users: %r\n\n" % User.query.all()

            c.set_cookie('localhost', 'MYCOOKIE', 'cookie_value')
            print "\n\nAGAIN All Users: %r\n\n" % User.query.all()
            # load_users()

            result = c.post('/handle-listing/1', data={'category_id': 1,
                    'brand_id': 3, 'modelname': 'Kaiju 6', 
                    'desc': 'Guaranteeing campground fun for the family, blah blah',
                    'cond': 'Excellente', 'avail_start': '2016-11-20',
                    'avail_end': '2016-12-31', 'pricing': 4.5, 'image': None,
                    'user': User.query.get(1), 'bestuse': 2, 'sleep': 6,
                    'seasoncat': 3, 'weight': 200, 'length': 80, 'width': 25,
                    'doors': 3, 'poles':3}, follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn('Listing successfully posted!', result.data)

        product = Product.query.filter(Product.model == 'Kaiju 6').one()

        self.assertEqual(product.model, 'Kaiju 6')
        tent = Tent.query.get(product.prod_id)
        self.assertEqual(tent.sleep_capacity, 6)


    def test_find_product(self):
        prod = Product.query.filter(Product.model == 'Sugar Shack 2').one()
        self.assertEqual(prod.condition, 'Good. Used twice.')
        print "\n\n test find product %s\n\n" % prod.model

        tent = Tent.query.get(prod.prod_id)
        self.assertEqual(tent.sleep_capacity, 2)

    # def test_get_users_in_area(self):
    #     users_in_area = get_users_in_area(['94612'], 1)
    #     users_names = []

    #     for user in users_in_area:
    #         users_names.append(user.fname)

    #     self.assertEqual(sorted(users_names), ['Count', 'Trix'])

    def test_filter_products(self):
        filtered_products = filter_products(Product.query.all(), 1, 1)

        self.assertEqual(filtered_products[0].model, 'Passage 2')

    def test_check_brand(self):
        self.assertEqual(check_brand(3), 3)

    def test_make_brand(self):
        make_brand("ABC")
        self.assertEqual(Brand.query.filter(Brand.brand_name == "ABC").one().brand_name, "ABC")

    def test_get_brand_id(self):
        self.assertEqual(get_brand_id("REI"), 1)


    def test_get_products_within_dates(self):
        start_date = convert_string_to_datetime('2015-10-31')
        end_date = convert_string_to_datetime('2015-11-01')

        products = get_products_within_dates(start_date, end_date, User.query.all())

        self.assertEqual(products[0].prod_id, 1)

    def test_categorize_products(self):
        categories = [Category.query.get(1), Category.query.get(2)]
        products = [Product.query.get(1), Product.query.get(2), Product.query.get(5)]

        inventory = categorize_products(categories, products)

        self.assertEqual(inventory['Tents'][0].prod_id, 1)
        self.assertEqual(inventory['Sleeping Bags'][0].prod_id, 5)



class SearchHelpersTestCase(TestCase):

    # def test_search_radius(self):
    #     searchcenter = '94612'
    #     postalcodes = [('94608',), ('94102',), ('94040',), ('95376',), ('95451',),
    #                     ('92277',), ('10013',), ('02139',)]

    #     within10 = search_radius(searchcenter, postalcodes, 10)
    #     within20 = search_radius(searchcenter, postalcodes, 20)
    #     within50 = search_radius(searchcenter, postalcodes, 50)
    #     within60 = search_radius(searchcenter, postalcodes, 60)
    #     within200 = search_radius(searchcenter, postalcodes, 200)
    #     within600 = search_radius(searchcenter, postalcodes, 600)
    #     within3000 = search_radius(searchcenter, postalcodes, 3000)
    #     shouldbeall = search_radius(searchcenter, postalcodes, 3100)

    #     self.assertEqual(within10, ['94608'])
    #     self.assertEqual(sorted(within20), sorted(['94608', '94102']))
    #     self.assertEqual(sorted(within50), sorted(['94608', '94102', '94040']))
    #     self.assertEqual(sorted(within60), sorted(['94608', '94102', '94040',
    #                                                '95376']))
    #     self.assertEqual(sorted(within200), sorted(['94608', '94102', '94040',
    #                                                 '95376', '95451']))
    #     self.assertEqual(sorted(within600), sorted(['94608', '94102', '94040',
    #                                                 '95376', '95451', '92277']))
    #     self.assertEqual(sorted(within3000), sorted(['94608', '94102', '94040',
    #                                                 '95376', '95451', '92277',
    #                                                 '10013']))
    #     self.assertEqual(sorted(shouldbeall), sorted(['94608', '94102', '94040',
    #                                                   '95376', '95451', '92277',
    #                                                   '10013', '02139']))

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
    def test_create_user_object(self):
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