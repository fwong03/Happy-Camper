from flask import request, session
from model import User, Region, Brand, Product, Tent
from model import SleepingBag, SleepingPad
from model import db
from datetime import datetime

# Helper functions for server make and update routes.Also threw in one rating
# helper function at end.
# Twelve functions.


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

    # print "\n\nsession user: %s\n\n" % session['user']

    # print "\n\nAll Users: %r \n\n" % User.query.all()

    user = User.query.filter(User.email == session['user']).one()

    product = Product(cat_id=category_id, brand_id=brand_id,
                      owner_user_id=user.user_id, model=modelname,
                      description=desc, condition=cond,
                      avail_start_date=avail_start, avail_end_date=avail_end,
                      price_per_day=pricing, image_url=image)

    print "\n\nMake Parent Product model: %r" % product.model

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

    print "\n\nMake Tent: %r" % tent

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
                               use_id=best_use_id, r_value=r_val,
                               weight=pad_weight,
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

    print "\n\nTent updated: id=%d capacity=%d seasons=%d weight=%d\n\n" % (
                                                                    tent.prod_id,
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
        sleeping_bag.length = None

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

# This is not related to making or updating objects. Threw it in here because
# it is the only rating-related helper function.
def calc_avg_star_rating(ratings):
    """Takes a list of ratings and returns average star rating as a
        float. If no star ratings, returns -1.

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
