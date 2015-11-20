from unittest import TestCase
from mock import patch
from datetime import datetime

from server import app
from model import connect_to_db, db
from seed import load_regions, load_users, load_bestuses, load_categories
from seed import load_brands, load_products, load_tents, load_filltypes
from seed import load_gendertypes, load_sleepingbags, load_padtypes
from seed import  load_sleepingpads,load_ratings, load_histories
from model import User, Brand, Product, Tent, Category

from make_update_helpers import check_brand, make_brand, get_brand_id
from search_helpers import get_users_in_area, filter_products, convert_string_to_datetime
from search_helpers import get_products_within_dates, categorize_products

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
        load_tents()
        load_filltypes()
        load_gendertypes()
        load_sleepingbags()
        load_padtypes()
        load_sleepingpads()
        load_ratings()
        load_histories()

    def test_find_users(self):
        franken = User.query.filter(User.fname == 'Franken').one()
        self.assertEqual(franken.fname, 'Franken')
        self.assertEqual(franken.email, 'franken@berry.com')

    def test_find_product(self):
        prod = Product.query.filter(Product.model == 'Sugar Shack 2').one()
        self.assertEqual(prod.condition, 'Good. Used twice.')
        print "\n\n test find product %s\n\n" % prod.model

        tent = Tent.query.get(prod.prod_id)
        self.assertEqual(tent.sleep_capacity, 2)

    def test_get_users_in_area(self):
        users_in_area = get_users_in_area(['94612'], 1)
        users_names = []

        for user in users_in_area:
            users_names.append(user.fname)

        self.assertEqual(sorted(users_names), ['Count', 'Trix'])

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

    def test_homepage(self):
        result = self.client.get('/')
        self.assertIn('<p><b>Login Here</b></p>', result.data)

    def test_login(self):
        result = self.client.post('/handle-login', data={'username': 'franken@berry.com',
                                  'password': 'abc'}, follow_redirects=True)
        self.assertEqual(result.status_code, 200)

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

    # def test_handle_tent_listing(self):
    #     result = self.client.post('handle-listing/1', data={'category_id': 1, 'brand_id': 3,
    #         'modelname': 'Kaiju 6', 'desc': 'Guaranteeing campground fun for the family, blah blah',
    #         'cond': 'Excellente', 'avail_start': '2016-11-20', 'avail_end': '2016-12-31',
    #         'pricing': 4.5, 'image': None, 'user': User.query.get(2), 'best_use_id': 2,
    #         'sleep': 6, 'seasoncat': 3, 'weight': 200}, follow_redirects=True)

    #     self.assertEqual(result.status_code, 200)
    #     prod2 = Product.query.filter(Product.model == 'Kaiju 6').one()
    #     self.assertEqual(Product.model, 'Kaiju 6')
    #     tent = Tent.query.get(prod.prod_id)
    #     self.assertEqual(tent.sleep_capacity, 6)












    # def test_tent_listing(self):
    #     result = self.client.post('/handle-listing/1', data={category_id=1,
    #         brand_num = 3







    # def test_get_users_in_area()



    def tearDown(self):
        pass




if __name__ == "__main__":
    import unittest

    unittest.main()
