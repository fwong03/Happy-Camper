from model import User
from datetime import datetime, timedelta
from geolocation.google_maps import GoogleMaps
from geolocation.distance_matrix import const
import os

 # Helper functions for server.py search-related routes
 # Seven function total

def search_radius(search_center, postalcodes, radius):
    """ Finds zipcodes in the database that are within a search radius of a
        location.
        These zipcodes are then returned so we can find users with those zipcodes
        and display their products in search results.

        This uses the python library geolocation-python, which uses the
        GoogleMaps API.

        Takes in search center as a string, postalcodes as a list of tuples
        (because that is the format returned from the database), and search
        radius in miles as an int. The function returns the list of
        postal codes in the given list that are within the given radius.

    """
    # Put this in for now to prevent eof error from hitting Google Maps API too
    # frequently.
    dist_from_94612 = {'94109': 11.2468, '94612': 0.0006, '94040': 45.4221,
                       '94115': 13.2973, '95376': 53.1893, '94043': 39.0842}

    # Convert the list of tuples to a list of strings.
    postalcodes_in_db = []

    for postalcode in postalcodes:
        postalcodes_in_db.append(postalcode[0])

    print "\n\n\n\n\nSearch radius is: ", radius
    print "Search center is", search_center
    print "Distinct Postalcodes is: ", postalcodes_in_db

    postalcodes_within_radius = []
    postalcodes_to_remove = []

    for postalcode in postalcodes_in_db:
        print "checking postalcode: %s" % postalcode
        if postalcode in dist_from_94612:
            if dist_from_94612[postalcode] <= radius:
                postalcodes_within_radius.append(postalcode)
                print "Added %s with distance %r" % (postalcode, dist_from_94612[postalcode])
                print "postalcodes to return is now: ", postalcodes_within_radius
            else:
                print "not wihtin search radius."
            postalcodes_to_remove.append(postalcode)
            print "postalcodes to remove is now: ", postalcodes_to_remove


    print "zipcodes to remove: ", postalcodes_to_remove

    if len(postalcodes_in_db) > len(postalcodes_to_remove):

        distinct_postalcodes = [postalcode for postalcode in postalcodes_in_db if postalcode not in postalcodes_to_remove]

        print "Distinct postalcodes sent to Google Maps API: ", distinct_postalcodes
        print "Postalcodes to return is now: %r\n\n\n" % postalcodes_within_radius

        # Run if there are still things left in distinct_postalcodes
        if distinct_postalcodes:
            print "Now running Google Maps API"

            google_maps = GoogleMaps(api_key=os.environ['GOOGLE_API_KEY'])

            # Put search center in a list because that is how the the geolocation
            # distance module takes it as a parameter
            search_center = [search_center]

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

            for destination in destinations:
                line = destination.split()
                postalcode = line[-2].replace(",", "")
                postalcodes_within_radius.append(postalcode)
            #     print line
            # print "postal codes: ", postalcodes

            # We return this list of postal codes.

    print "Returning postalcodes: %r\n\n\n" % postalcodes_within_radius
    return postalcodes_within_radius


# def get_user_distances(zipcode, postalcodes):
#     """ Gets distance a given zipcode of a particular user is from all other
#         zipcodes in the database.

#         Made this to prevent eof error getting from search, which may by due to
#         hitting the GoogleMaps API too frequently wihin a given time period.
#         Use this until add zipcode table to database to store distance searches
#         in above search_radius.

#         This is basically a version of the search_radius function above.

#         Takes in zipcode as an integer and distinct postal code query result
#         and returns a dictionary of zipcode as key and distance as value.
#     """

#     search_center = [zipcode]

#     # query = db.session.query(User.postalcode).distinct()
#     # postalcodes = query.all()
#     distinct_postalcodes = []

#     for postalcode in postalcodes:
#         distinct_postalcodes.append(postalcode[0])

#     google_maps = GoogleMaps(api_key=os.environ['GOOGLE_API_KEY'])
#     matrixthingies = google_maps.distance(search_center, distinct_postalcodes).all()
#     distances_from_user = {}

#     for thingy in matrixthingies:
#         print "Processing matrixthingy with destination: %r and miles: %r" % (thingy.destination, thingy.distance.miles)
#         line = thingy.destination.split()
#         postalcode = line[-2].replace(",", "")

#         distances_from_user[postalcode] = thingy.distance.miles

#     print "distances from user :", distances_from_user

#     return distances_from_user


def get_users_in_area(postal_codes, user_id):
    """Finds users in the database that live in one of the given zipcodes.

        (Here I also passed in the use_id to make it easier to test. This was before
        Jackie showed me how to set cookies in tests.)

    t"""

    users_in_area = User.query.filter(User.postalcode.in_(postal_codes)).all()
    logged_in_user = User.query.get(user_id)

    if logged_in_user in users_in_area:
        users_in_area.remove(logged_in_user)

    return users_in_area


def filter_products(products, category_id, brand_id):
    """ Filters a given list of products for a given category and brand.

        Takes in list of products, category_id as int and brand_id as integers
        and returns a list of products.
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
    """Finds products that are available within a given date range.

        Takes in list of users and returns a list of products
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
    """Organizes products by categories.

        Takes in lists of Category and Product objects and returns dictionary of
        Products objects with category names as keys.

    """
    inventory = {}

    for category in categories:
        inventory[category.cat_name] = []

    for product in products:
        inventory[product.category.cat_name].append(product)

    return inventory


def calc_default_dates(deltadays):
    """Calculates default dates to pre-populate the search area.

        Takes an integer and returns two datetimes and two strings:
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
    """Converts the date supplied as a string on an HTML form into a datetime.

        Takes in date as string in format "yyyy-mm-dd" (e.g. "2015-11-04"
        for November 4, 2015) and returns datetime object.

    """

    date = datetime.strptime(date_string, "%Y-%m-%d")

    return date
