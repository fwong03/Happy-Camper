# Models and database for Happy Camper project.
# Version 1
# October 27, 2015

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

##############################################################


class Region(db.Model):
    """Regions (i.e., states) for user addresses."""

    __tablename__ = "regions"

    region_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    abbr = db.Column(db.String(2), nullable=False, unique=True)
    full = db.Column(db.String(16), nullable=False, unique=True)

    user = db.relationship('User', backref='region')

    def __repr__(self):
        return "<Region region_id=%d, abbreviation=%s, fullname=%s>" % (
            self.region_id, self.abbr, self.full)


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

    # Get rid of these? Don't need anymore?
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

    renter = db.relationship('History', backref='renter')

    def __repr__(self):

        return "<User user_id=%d, name=%s %s, postalcode=%s, email=%s>" % (
            self.user_id, self.fname, self.lname, self.postalcode, self.email)


class Category(db.Model):
    """Product categories used to specify product subset table"""

    __tablename__ = 'categories'

    cat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_name = db.Column(db.String(16), nullable=False, unique=True)
    # add display name attribute

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
    # CHANGE: pricing is some amount first day then another amount per day 
    # following not counting pickup or dropoff date (REI model)

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
    avail_start_date = db.Column(db.DateTime, nullable=False)
    avail_end_date = db.Column(db.DateTime, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)

    # Do image url now since image upload sounds like it will be complicated.
    image_url = db.Column(db.String(128))

    # Put subset table backrefs here
    tent = db.relationship('Tent', uselist=False, backref='product')
    sleepingbag = db.relationship('SleepingBag', uselist=False, backref='product')

    # Other backrefs
    owner = db.relationship('User', backref='products')
    brand = db.relationship('Brand', backref='products')
    category = db.relationship('Category', backref='products')
    histories = db.relationship('History', backref='product')

    def __repr__(self):
        return "<Product prod_id=%d, cat_id=%d, owner_id=%d, model=%s, description=%s, condition=%s, avail=%r to %r, price=%r>" % (
            self.prod_id, self.cat_id, self.owner_user_id, self.model,
            self.description, self.condition, self.avail_start_date, self.avail_end_date, self.price_per_day)


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
    min_trail_weight = db.Column(db.Integer, nullable=False)
    # These are optional
    floor_width = db.Column(db.Integer)
    floor_length = db.Column(db.Integer)
    num_doors = db.Column(db.Integer)
    num_poles = db.Column(db.Integer)

    def __repr__(self):
        return "<Tent prod_id=%d, use_id=%d, capacity=%d, seasons=%d, weight=%d, length=%r, width=%r, num_doors=%r, num_poles=%r>" % (
            self.prod_id, self.use_id, self.sleep_capacity,
            self.seasons, self.min_trail_weight, self.floor_width,
            self.floor_length, self.num_doors, self.num_poles)


class FillType(db.Model):
    """Fill types for sleeping bags and sleeping pads."""

    __tablename__ = 'filltypes'

    # D for down, S for synthetic
    fill_code = db.Column(db.String(1), primary_key=True)
    fill_name = db.Column(db.String(16), unique=True)


class Gender(db.Model):
    """Pull gender out so future tables can reference and have option to easily
    find all women's stuff.

    """
    __tablename__ = 'genders'
    gender_code = db.Column(db.String(1), primary_key=True)
    gender_name = db.Column(db.String(8), nullable=False, unique=True)

    def __repr__(self):
        return "<Gender gender_code=%s gender_name=%s>" % (self.gender_code,
                                                           self.gender_name)

    #TO DO: Make gender seed table, change sleepingbagdata


class SleepingBag(db.Model):
    """Sleeping bags is one of the subset tables of Product"""

    __tablename__ = 'sleepingbags'

    prod_id = db.Column(db.Integer, db.ForeignKey('products.prod_id'),
                        primary_key=True)
    fill_code = db.Column(db.String(1), db.ForeignKey('filltypes.fill_code'),
                          nullable=False)
    temp_rating = db.Column(db.Integer, nullable=False)

    # These are optional.
    weight = db.Column(db.Integer)
    length = db.Column(db.Integer)
    # F, M, or U for female, male, unisex
    gender_code = db.Column(db.String(1), db.ForeignKey('genders.gender_code'))


    def __repr__(self):
        return "<Sleeping Bag prod_id=%d, fill_code=%s, temp_rating=%d, weight=%d, length=%d, gender=%s>" % (
            self.prod_id, self.fill_code, self.temp_rating, self.weight,
            self.length, self.gender)


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
    total_cost = db.Column(db.Float, nullable=False)

    # Ratings are optional
    owner_rating_id = db.Column(db.Integer, db.ForeignKey('ratings.rating_id'))
    renter_rating_id = db.Column(db.Integer, db.ForeignKey('ratings.rating_id'))
    prod_rating_id = db.Column(db.Integer, db.ForeignKey('ratings.rating_id'))

    # http://docs.sqlalchemy.org/en/latest/orm/join_conditions.html
    owner_rating = db.relationship('Rating', foreign_keys='History.owner_rating_id', backref='ohistory')
    renter_rating = db.relationship('Rating', foreign_keys='History.renter_rating_id', backref='rhistory')
    product_rating = db.relationship('Rating', foreign_keys='History.prod_rating_id', backref='phistory')

    def __repr__(self):
        return "<History history_id=%d, prod_id=%d, renter_user_id=%r, owner_rating_id=%r, renter_rating_id=%r, prod_rating_id=%r>" % (
            self.history_id, self.prod_id, self.renter_user_id,
            self.owner_rating_id, self.renter_rating_id, self.prod_rating_id)


class Rating(db.Model):
    """Renters can rate owner and products, Owners can rate renters."""

    __tablename__ = 'ratings'

    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stars = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.String(128))


    def __repr__(self):
        return "<Rating rating_id=%d, stars=%d, comments=%s>" % (self.rating_id,
                self.stars, self.comments)


##############################################################################

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///camper.db'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # This allows direct database interaction if this module is run interactively.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
