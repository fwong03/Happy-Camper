# Helper functions for my routes in server.py
from flask import request, session
from model import User, Brand, Category, Product
from model import db
from datetime import datetime, timedelta
from geolocation.google_maps import GoogleMaps
from geolocation.distance_matrix import const
import os


def get_lat_lngs(address):
    """Takes address as string, returns a list of latitude and
        longitude as floats.
    """

    google_maps = GoogleMaps(api_key=os.environ['GOOGLE_API_KEY'])

    location = google_maps.search(location=address)

    user_location = location.first()

    latitude = user_location.lat
    longitude = user_location.lng

    return [latitude, longitude]


def search_radius(search_center, postalcodes, radius):
    """Takes in search center as a string, postalcodes as a list of tuples,
        and search radius in miles as an int. The function returns the list of
        postal codes in the given list that are within the given radius.

    """

    # TO DO: Break this search_radius down into smaller functions that
    # will be easier to test.

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


def calc_dates(deltadays):
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


def convert_strings_to_datetimes(date1_string, date2_string):
    """Takes two dates as string in format "yyyy-mm-dd" (e.g. "2015-11-04"
        for November 4, 2015) and returns a list of them as datetime objects.
    """

    date1 = datetime.strptime(date1_string, "%Y-%m-%d")
    date2 = datetime.strptime(date2_string, "%Y-%m-%d")

    return [date1, date2]


def calc_num_days(date1_string, date2_string):
    """Takes two dates as string in format "yyyy-mm-dd" (e.g. "2015-11-04"
        for November 4, 2015) and returns number of days between them as an
        integer.

        Subtracts date1 from date2.

    """

    dates = convert_strings_to_datetimes(date1_string, date2_string)
    date1 = dates[0]
    date2 = dates[1]
    days = (date2 - date1).days + 1

    return days


def get_brands():
    """Takes no arguments and returns a list of all brands in the database.
    """
    brands = Brand.query.all()
    names = []

    for brand in brands:
        names.append(brand.brand_name)

    return names


def make_brand(brandname):
    """Adds a new brand to the database."""

    brand = Brand(brand_name=brandname)

    db.session.add(brand)
    db.session.commit()


def get_brand_id(brandname):
    """Takes brand name as a string and returns brand id as an integer"""

    brand = Brand.query.filter(Brand.brand_name == brandname).one()
    return brand.brand_id


def make_product():
    """Takes no arguments and returns a Product object.

    Will take a listing form submission to make a parent Product object.
    Make this before a child (e.g. Tent, Sleeping Bag) object.
    """

    brandname = request.form.get("brand")
    modelname = request.form.get("modelname")
    desc = request.form.get("desc")
    cond = request.form.get("cond")
    avail_start = request.form.get("avail_start")
    avail_end = request.form.get("avail_end")
    pricing = float(request.form.get("pricing"))
    image = request.form.get("image")

    avail_start = datetime.strptime(avail_start, "%Y-%m-%d")
    avail_end = datetime.strptime(avail_end, "%Y-%m-%d")

    if brandname == "addbrand":
        newbrandname = request.form.get("newbrandname")
        make_brand(newbrandname)
        brandname = newbrandname

    user = User.query.filter(User.email == session['user']).one()
    category = Category.query.filter(Category.cat_name == 'tents').one()
    brand = Brand.query.filter(Brand.brand_name == brandname).one()

    product = Product(cat_id=category.cat_id, brand_id=brand.brand_id,
                      owner_user_id=user.user_id, model=modelname,
                      description=desc, condition=cond,
                      avail_start_date=avail_start, avail_end_date=avail_end,
                      price_per_day=pricing, image_url=image)

    return product




