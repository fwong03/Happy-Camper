from flask import session
from model import User
from datetime import datetime, timedelta
from geolocation.google_maps import GoogleMaps
from geolocation.distance_matrix import const
import os

 # Helper functions for server.py search-related routes
 # Seven function total

def search_radius(search_center, postalcodes, radius):
    """Takes in search center as a string, postalcodes as a list of tuples,
        and search radius in miles as an int. The function returns the list of
        postal codes in the given list that are within the given radius.

    """

    google_maps = GoogleMaps(api_key=os.environ['GOOGLE_API_KEY'])

    # Put search center in a list because that is how the the geolocation
    # distance module takes it as a parameter
    search_center = [search_center]

    # Convert the list of tuples to a list of strings.
    distinct_postalcodes = []
    for postalcode in postalcodes:
        distinct_postalcodes.append(postalcode[0])

    # Now we can calculate distances.
    items = google_maps.distance(search_center, distinct_postalcodes).all()

    # Items is list of distance matrix object thingies. Each has an origin (here,
    # the search area), destination (here, the user zipcode), and distance
    # between them. First we'll take out the matrix thingies within the search
    # radius of the given search center.

    matrixthingies = []
    for item in items:
        # print "Processing", item.destination, item.distance.miles
        if (item.distance.miles <= radius):
            # print "adding %r" % item.destination
            matrixthingies.append(item)

    # Now we pull out the user location info from the matrixthingies. This info
    # has the city, state, zipcode and country.
    destinations = []
    for thingy in matrixthingies:
        destinations.append(thingy.destination)

    # print "destinations: ", destinations

    # Now we pull out the zipcode from the list of destinations.
    postalcodes = []
    for destination in destinations:
        line = destination.split()
        postalcode = line[-2].replace(",", "")
        postalcodes.append(postalcode)
    #     print line
    # print "postal codes: ", postalcodes

    # We return this list of postal codes.
    return postalcodes


def get_users_in_area(postal_codes):
    """Give a list of postal with searching user taken out"""

    users_in_area = User.query.filter(User.postalcode.in_(postal_codes)).all()
    logged_in_user = User.query.filter(User.email == session['user']).one()

    if logged_in_user in users_in_area:
        users_in_area.remove(logged_in_user)

    return users_in_area


def filter_products(products, category_id, brand_id):
    """Takes in list of products, category_id as int and brand_id as int and
        returns products with those category and brand IDs.
    """

    if category_id < 0 and brand_id < 0:
        return products
    else:
        filtered_products = []

        if category_id > 0 and brand_id < 0:
            for product in products:
                if product.cat_id == category_id:
                    filtered_products.append(product)
        elif (category_id < 0) and (brand_id > 0):
            for product in products:
                if product.brand_id == brand_id:
                    filtered_products.append(product)
        else:
            for product in products:
                if (product.cat_id == category_id) and (product.brand_id == brand_id):
                    filtered_products.append(product)

    return filtered_products


def get_products_within_dates(start_date, end_date, users):
    """Takes in list of User objects and returns a list of Product objects
        those users have available for rent within the specified start and
        end dates (inclusive).

    """

    available_products = []

    for user in users:
        if user.active:
            for product in user.products:
                if product.available and (product.avail_start_date <= start_date) and (product.avail_end_date >= end_date):
                    available_products.append(product)

    return available_products


def categorize_products(categories, products):
    """Takes in lists of Category and Product objects and returns dictionary of
        Products objects organized by category name.

    """
    inventory = {}

    for category in categories:
        inventory[category.cat_name] = []

    for product in products:
        inventory[product.category.cat_name].append(product)

    return inventory


def calc_default_dates(deltadays):
    """Takes an integer and returns two datetimes and two strings:
            today: datetime of today
            future: datetime of today plus the number of days
            today_string': string version of 'today' in isoformat and of date
                       only ('yyyy-mm-dd')
            future_string: datetime object of future, isoformat and date only
    """
    dates = {}
    today = datetime.today()
    future = today + timedelta(days=deltadays)

    dates['today'] = today
    dates['future'] = future
    dates['today_string'] = today.date().isoformat()
    dates['future_string'] = future.date().isoformat()

    return dates


def convert_string_to_datetime(date_string):
    """Takes in date as string in format "yyyy-mm-dd" (e.g. "2015-11-04"
        for November 4, 2015) and returns datetime object.
    """

    date = datetime.strptime(date_string, "%Y-%m-%d")

    return date