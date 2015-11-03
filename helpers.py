# Helper functions for my routes in server.py
from flask import request, session
from model import User, Brand, Category, Product
from model import db
from datetime import datetime, timedelta
from geolocation.google_maps import GoogleMaps
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




