import unittest
from server import app

from model import Region, User, Category, BestUse, Brand, Product, Tent, FillType
from model import Gender, SleepingBag, PadType, SleepingPad, History

from mock import patch
from datetime import datetime
from helpers import convert_string_to_datetime, calc_default_dates, calc_avg_star_rating
from model import Rating


class SearchHelpersTestCase(unittest.TestCase):

    # http://www.robotswillkillusall.org/posts/how-to-mock-datetime-in-python/
    # https://pypi.python.org/pypi/mock
    @patch('helpers.datetime')
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


class MakeUpdateTestCase(unittest.TestCase):
    def test_make_user(self):
        user1 = User(fname='Michelle', lname='Tanner', street='1709 Broderick Street',
                     city='San Francisco', region_id=1, postalcode='94115',
                     phone=4155556666, email='michelle@tanner.com', password='123')

        self.assertEqual(user1.email, 'michelle@tanner.com')


# class RoutesTestCase(unittest.TestCase):
#     def setUp(self):
#         self.client = app.test_client()
#         connect_to_db(app, "sqlite:///")

#         db.create_all()


#     def test_homepage(self):
#         test_client = server.app.test_client()

#         result = test_client.get('/')
#         self.assertIn('<p><b>Login Here</b></p>', result.data)





if __name__ == "__main__":
    unittest.main()
