# Models and database for Happy Camper project.
# Version 1
# October 27, 2015

from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

##############################################################


class Region(db.Model):
    """Regions (i.e., states) for user addresses."""

    __tablename__ = "regions"

    region_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region_abbr = db.Column(db.String(2), nullable=False)


class User(db.Model):
    """Happy Camper user"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Per Bert rec: give user option to deactivate account.
    # Make active false when user deactivates.
    active = db.Column(db.Boolean, default=True)
    fname = db.Column(db.String(32), nullable=False)
    lname = db.Column(db.String(32), nullable=False)
    street = db.Column(db.String(32), nullable=False)
    city = db.Column(db.String(32), nullable=False)

    # Made this region_id instead of state per Drew recommendation.
    # ENUM would also work but less flexible.
    region_id = db.Column(db.Integer, db.ForeignKey('regions.region_id'),
                          nullable=False)

    # Changed from INT to string per Drew recommendation. If integer would
    # have to deal with zip codes starting with zeroes. Make 10 long so have
    # option to accept nine-digit zip codes.
    postalcode = db.Column(db.String(10), nullable=False)

    # Use pyzipcode to convert zip code to lat lngs?
    # With pyzip can find zipcodes within a radius of a given zipcode.
    # Make this non nullable once figure out how you're going to do this.
    # Index these since will likely use to search for nearby items.
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    # Drew: phone presents another INT problem.
    # Store as user inputs and then clean up when pull out to use?
    # When make form strongly suggest input format with "()" and "-".
    # Google JS phone checks.
    phone = db.Column(db.Integer, nullable=False)

    # Also check online for JS email check.
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(32), nullable=False)

    def __repr__(self):

        return "<User user_id=%d, name=%s %s, zipcode=%d, email=%s>" % (
            self.user_id, self.fname, self.lname, self.zipcode, self.email)


class Category(db.Model):
    """Product categories used to specify product subset table"""

    __tablename__ = 'categories'

    cat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_name = db.Column(db.String(16), nullable=False, unique=True)

    def __repr__(self):

        return "<Category cat_id=%d, cat_name=%s>" % (self.cat_id, self.cat_name)


class BestUse(db.Model):
    """Best uses for some categories (not all)"""

    __tablename__ = "bestuses"

    use_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    use_name = db.Column(db.String(16), nullable=False, unique=True)

    def __repr__(self):
        return "<BestUse use_id=%d, use_name=%s>" % (self.use_id, self.use_name)


class Brand(db.Model):
    """Brands"""

    __tablename__ = "brands"

    brand_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    brand_name = db.Column(db.String(64), nullable=False, unique=True)

    def __repr__(self):
        return "<Brand brand_id=%d, brand_name=%s>" % (self.brand_id, self.brand_name)


class Product(db.Model):
    """Product parent class."""

    __tablename__ = 'products'

    # Subset tables (e.g., tents) use this same PK so make subset table entry at
    # same time as product entry!  Note PKs automatically get an index.
    prod_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_id = db.Column(db.Integer, db.ForeignKey('categories.cat_id'),
                       nullable=False)

    # Per Bert recommendation put brand name in separate table for more
    # flexibility.
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.brand_id'),
                         nullable=False)

    # Customer ID of item's owner.
    owner_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'),
                              nullable=False)

    # Per Bert rec: make available false when item is borrowed or when owner
    # deactivates account.
    available = db.Column(db.Boolean, default=True)
    model = db.Column(db.String(16), nullable=False)
    condition = db.Column(db.String(128))
    description = db.Column(db.String(128))

    # When user inputs check avail end date is after start date.
    # When show product info, avail start date is later of today and user-inputted
    # start date.
    avail_start_date = db.Column(db.DateTime, nullable=False, default=datetime.date.today())
    avail_end_date = db.Column(db.DateTime, nullable=False, default=datetime.date.today())
    price_per_day = db.Column(db.Float, nullable=False)

    # Do image url now since image upload sounds like it will be complicated.
    image_url = db.Column(db.String(128))

    # Put subset table backrefs here
    tent = db.relationship('Tent', uselist=False, backref='product')

    # Other backrefs
    owner = db.relationship('User', backref='products')
    brand = db.relationship('Brand', backref='products')
    category = db.relationship('Category', backref='products')

    def __repr__(self):
        return "<Product prod_id=%d, cat_id=%d, owner_id=%d, model=%s, condition=%s, avail=%r to %r, price=%r>" % (
            self.prod_id, self.cat_id, self.owner_user_id, self.model, self.condition,
            self.avail_start_date, self.avail_end_date, self.price_per_day)


class Tent(db.Model):
    """Tent is one of the subset tables of Product"""

    __tablename__ = 'tents'

    # Make sure you create the Tent at the same time you create the Product.
    # They share primary keys.
    prod_id = db.Column(db.Integer, db.ForeignKey('products.prod_id'),
                        primary_key=True)
    use_id = db.Column(db.Integer, db.ForeignKey('bestuses.use_id'),
                       nullable=False)
    sleep_capacity = db.Column(db.Integer, nullable=False)
    seasons = db.Column(db.Integer, nullable=False)

    # These are optional.
    min_trail_weight = db.Column(db.Integer)
    floor_width = db.Column(db.Integer)
    floor_length = db.Column(db.Integer)
    num_doors = db.Column(db.Integer)
    num_poles = db.Column(db.Integer)

    def __repr__(self):
        return "<Tent prod_id=%d, use_id=%d, capacity=%d, seasons=%d, weight=%d, length=%d, width=%d, num_doors=%d, num_poles=%d>" % (
            self.prod_id, self.use_id, self.sleep_capacity,
            self.seasons, self.min_trail_weight, self.floor_width,
            self.floor_length, self.num_doors, self.num_poles)


class History(db.Model):
    """Rental histories"""

    __tablename__ = 'histories'

    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Make this index if think will use a lot for search. Check, may already get
    # index since it's a FK.
    prod_id = db.Column(db.Integer, db.ForeignKey('products.prod_id'),
                        nullable=False)
    renter_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'),
                        nullable=False)

    # Bert rec: put this in to make search faster since wouldn't have to join.
    # owner_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'),
    #                     nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    # Ratings are optional
    owner_rate_id = db.Column(db.Integer, db.ForeignKey('ratings.rate_id'))
    renter_rate_id = db.Column(db.Integer, db.ForeignKey('ratings.rate_id'))
    prod_rate_id = db.Column(db.Integer, db.ForeignKey('ratings.rate_id'))


class Rating(db.Model):
    """Renters can rate owner and products, Owners can rate renters."""

    __tablename__ = 'ratings'

    rate_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stars = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.String(128))



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///camper.db'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
