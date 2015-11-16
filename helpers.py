# Helper functions for my routes in server.py
from flask import request, session
from model import User, Brand, Category, Product, Tent, Rating, Region
from model import SleepingBag, SleepingPad
from model import db
from datetime import datetime, timedelta
from geolocation.google_maps import GoogleMaps
from geolocation.distance_matrix import const
import os


######################## User stuff ###################################
def make_user(password):
    """Create User object. Called by route /handle-createaccount"""

    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    staddress = request.form.get('staddress')
    cty = request.form.get('cty')
    state = request.form.get('state')
    zipcode = request.form.get('zipcode')
    phonenumber = int(request.form.get('phonenumber'))
    username = request.form.get('username')

    # Get region id from the Regions table
    region = Region.query.filter(Region.abbr == state).one()
    state_id = region.region_id

    user = User(fname=firstname, lname=lastname, street=staddress,
                city=cty, region_id=state_id, postalcode=zipcode,
                phone=phonenumber, email=username, password=password)

    return user

######################## Listing stuff ###################################
def make_brand(brandname):
    """Adds a new brand to the database."""

    brand = Brand(brand_name=brandname)

    db.session.add(brand)
    db.session.commit()


def get_brand_id(brandname):
    """Takes brand name as a string and returns brand id as an integer"""

    brand = Brand.query.filter(Brand.brand_name == brandname).one()
    return brand.brand_id


def make_parent_product(brand_id, category_id):
    """Takes ints brand_id and category_id and returns Product object.

    Will take a listing form submission to make a parent Product object.
    Make this before a child (e.g. Tent, Sleeping Bag) object.
    """

    modelname = request.form.get("modelname")
    desc = request.form.get("desc")
    cond = request.form.get("cond")
    avail_start = request.form.get("avail_start")
    avail_end = request.form.get("avail_end")
    pricing = float(request.form.get("pricing"))
    image = request.form.get("image")

    avail_start = datetime.strptime(avail_start, "%Y-%m-%d")
    avail_end = datetime.strptime(avail_end, "%Y-%m-%d")

    user = User.query.filter(User.email == session['user']).one()

    product = Product(cat_id=category_id, brand_id=brand_id,
                      owner_user_id=user.user_id, model=modelname,
                      description=desc, condition=cond,
                      avail_start_date=avail_start, avail_end_date=avail_end,
                      price_per_day=pricing, image_url=image)

    return product


def make_tent(product_id):
    """Make child tent object given the corresponding product ID.

    """
    best_use_id = int(request.form.get("bestuse"))
    sleep = int(request.form.get("sleep"))
    seasoncat = int(request.form.get("seasoncat"))
    weight = int(request.form.get("weight"))

    # Deal with optional values.
    try:
        width = int(request.form.get("width"))
    except ValueError:
        width = None
    try:
        length = int(request.form.get("length"))
    except ValueError:
        length = None
    try:
        doors = int(request.form.get("doors"))
    except ValueError:
        doors = None
    try:
        poles = int(request.form.get("poles"))
    except ValueError:
        poles = None

    tent = Tent(prod_id=product_id, use_id=best_use_id,
                sleep_capacity=sleep, seasons=seasoncat, min_trail_weight=weight,
                floor_width=width, floor_length=length, num_doors=doors,
                num_poles=poles)
    return tent


def make_sleeping_bag(product_id):
    """Make child sleeping bag object given the corresponding product ID.

    """
    filltype = request.form.get("filltype")
    temp = int(request.form.get("temp"))
    bag_weight = int(request.form.get("bag_weight"))

    # Deal with optional values.
    try:
        length = int(request.form.get("length"))
    except ValueError:
        length = None
    try:
        gender = request.form.get("gender")
    except ValueError:
        gender = None

    sleeping_bag = SleepingBag(prod_id=product_id, fill_code=filltype,
                               temp_rating=temp, weight=bag_weight, length=length,
                               gender_code=gender)

    return sleeping_bag


def make_sleeping_pad(product_id):
    """Make child sleeping pad object given the corresponding product ID.

    """
    padtype = request.form.get("padtype")
    best_use_id = int(request.form.get("bestuse"))
    r_val = float(request.form.get("r_val"))
    pad_weight = int(request.form.get("pad_weight"))
    pad_length = int(request.form.get("pad_length"))

    # Deal with optional values.
    try:
        pad_width = int(request.form.get("pad_length"))
    except ValueError:
        pad_width = None

    sleeping_pad = SleepingPad(prod_id=product_id, type_code=padtype,
                   use_id=best_use_id, r_value=r_val, weight=pad_weight,
                   length=pad_length, width=pad_width)

    return sleeping_pad


###################### Editing stuff ################################
def update_parent_product(prod_id, brand_id):
    """Takes ints brand_id and category_id and updates Product object.

    """

    product = Product.query.get(prod_id)

    product.available = True
    product.brand_id = brand_id
    product.model = request.form.get("modelname")
    product.description = request.form.get("desc")
    product.condition = request.form.get("cond")
    product.price_per_day = float(request.form.get("pricing"))
    product.image_url = request.form.get("image")

    avail_start = request.form.get("avail_start")
    avail_end = request.form.get("avail_end")

    avail_start = datetime.strptime(avail_start, "%Y-%m-%d")
    avail_end = datetime.strptime(avail_end, "%Y-%m-%d")

    product.avail_start_date = avail_start
    product.avail_end_end = avail_end

    db.session.commit()

    print "\n\nProduct updated: id=%d name= %s %s\n\n" % (product.prod_id,
                                                   product.brand.brand_name,
                                                   product.model)
    return


def update_tent(prod_id):
    """Update tent object given product id"""

    tent = Tent.query.get(prod_id)

    tent.use_id = int(request.form.get("bestuse"))
    tent.sleep_capacity = int(request.form.get("sleep"))
    tent.seasons = int(request.form.get("seasoncat"))
    tent.min_trail_weight = int(request.form.get("weight"))

    # Deal with optional values.
    try:
        tent.floor_width = int(request.form.get("width"))
    except ValueError:
        tent.floor_width = None

    try:
        tent.floor_length = int(request.form.get("length"))
    except ValueError:
        tent.floor_length = None

    try:
        tent.num_doors = int(request.form.get("doors"))
    except ValueError:
        tent.num_doors = None

    try:
        tent.num_poles = int(request.form.get("poles"))
    except ValueError:
        tent.num_poles = None

    db.session.commit()

    print "\n\nTent updated: id=%d capacity=%d seasons=%d weight=%d\n\n" % (tent.prod_id,
                                                   tent.sleep_capacity,
                                                   tent.seasons,
                                                   tent.min_trail_weight)
    return


def update_sleeping_bag(prod_id):
    """Update sleeping bag object given product id"""

    sleeping_bag = SleepingBag.query.get(prod_id)

    sleeping_bag.fill_code = request.form.get("filltype")
    sleeping_bag.temp_rating = int(request.form.get("temp"))

    # Deal with optional values.
    try:
        sleeping_bag.weight = int(request.form.get("bag_weight"))
    except ValueError:
        sleeping_bag.weight = None

    try:
        sleeping_bag.length = int(request.form.get("length"))
    except ValueError:
        sleeping_pad.length = None

    gender = request.form.get("gender")

    if gender == "Z":
        sleeping_bag.gender_code = None
    else:
        sleeping_bag.gender_code = gender

    db.session.commit()

    print "\n\nSleeping Bag updated: id=%d fill_type=%s temp=%d weight=%r\n\n" % (
                                                   sleeping_bag.prod_id,
                                                   sleeping_bag.fill_code,
                                                   sleeping_bag.temp_rating,
                                                   sleeping_bag.weight)
    return


def update_sleeping_pad(prod_id):
    """Update sleeping pad object given product id"""

    sleeping_pad = SleepingPad.query.get(prod_id)

    sleeping_pad.type_code = request.form.get("padtype")
    sleeping_pad.use_id = int(request.form.get("bestuse"))
    sleeping_pad.r_value = float(request.form.get("r_val"))
    sleeping_pad.weight = int(request.form.get("pad_weight"))
    sleeping_pad.length = int(request.form.get("pad_length"))

    # Deal with optional values.
    try:
        sleeping_pad.width = int(request.form.get("pad_width"))
    except ValueError:
        sleeping_pad.width = None

    db.session.commit()

    print "\n\nSleeping Pad updated: id=%d type=%s use_id=%d r-val=%r\n\n" % (
                                                   sleeping_pad.prod_id,
                                                   sleeping_pad.type_code,
                                                   sleeping_pad.use_id,
                                                   sleeping_pad.r_value)
    return


######################## Searching stuff ###################################
def search_radius(search_center, postalcodes, radius):
    """Takes in search center as a string, postalcodes as a list of tuples,
        and search radius in miles as an int. The function returns the list of
        postal codes in the given list that are within the given radius.

    """

    # TO DO: Break this search_radius down into smaller functions that
    # will be easier to test? Use sets instad of lists? Need to return a list though.

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

def check_brand(brand_id):
    """Takes int brand_id and returns int brand_id.

        Check if need to add a new brand to database. If given brand_id is
        less than zero, it makes a new brand and returns the brand_id of that
        newly created brand.
    """

    if brand_id < 0:
        new_brand_name = request.form.get("new_brand_name")
        brand = Brand(brand_name=new_brand_name)
        db.session.add(brand)
        db.session.commit()
        brand_id = brand.brand_id

    return brand_id

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


######################## Rating stuff ###################################
def calc_avg_star_rating(ratings):
    """Takes a list of ratings and returns average star rating as a
        float. If no star ratings, returns -1.

        >>> rating1 = Rating(rating_id=1, stars=4, comments="abc")
        >>> rating2 = Rating(rating_id=3, stars=2, comments="def")
        >>> rating3 = Rating(rating_id=3, stars=1, comments="ghi")
        >>> ratings = [rating1, rating2, rating3]
        >>> calc_avg_star_rating(ratings)
        2.3333333333333335

    """
    avg_star_rating = -1

    if ratings:
        sum_stars = 0
        count_star_ratings = 0

        for rating in ratings:
            if rating.stars:
                sum_stars += rating.stars
                count_star_ratings += 1

        avg_star_rating = float(sum_stars) / count_star_ratings

    return avg_star_rating