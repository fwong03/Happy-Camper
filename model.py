# Models and database for Happy Camper project.
# Version 1
# October 27, 2015

from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

##############################################################
# Model definitions


class Customer(db.Model):
    """Happy Camper user"""

    __tablename__ = "customers"

    cust_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    active = db.Column(db.Boolean, default=True)
    fname = db.Column(db.String(32), nullable=False)
    lname = db.Column(db.String(32), nullable=False)
    street = db.Column(db.String(32), nullable=False)
    city = db.Column(db.String(32), nullable=False)
    # TODO: for state, constraint in list of two-character state abbreviations
    state = db.Column(db.String(2), nullable=False)
    # TODO: for zipcode, constraint must be 5 numbers long
    zipcode = db.Column(db.Integer, nullable=False)
    # latitude and longitude for geolocation stuff
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    # TODO: for phone, constraint must be 10 numbers long
    phone = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(32), nullable=False)

    def __repr__(self):

        return "<Customer cust_id=%r, name=%r %r, zipcode=%r, email=%r>" % (
            self.cust_id, self.fname, self.lname, self.zipcode, self.email)


class Category(db.Model):
    """Product categories used to specify product subset table"""

    __tablename__ = 'categories'

    cat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_name = db.Column(db.String(16), nullable=False, unique=True)
    # Include category misspellings in search words field
    # cat_search_words = db.Column(db.String(128), nullable=False)

    def __repr__(self):

        return "<Category cat_id=%r, cat_name=%r, search_words=%r>" % (
            self.cat_id, self.cat_name, self.cat_search_words)


class BestUse(db.Model):
    """Best uses for some categories (not all)"""

    __tablename__ = "best_uses"

    use_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    use_name = db.Column(db.String(16), nullable=False, unique=True)

    def __repr__(self):
        return "<BestUse use_id=%r, use_name=%r>" % (self.use_id, self.use_name)


class Brand(db.Model):
    """Brands"""

    __tablename__ = "brands"

    brand_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    brand_name = db.Column(db.String(64), nullable=False, unique=True)

    def __repr__(self):
        return "<Brand brand_id=%r, brand_name=%r>" % (self.brand_id, self.brand_name)


class Product(db.Model):
    """Product parent class."""

    __tablename__ = 'products'

    prod_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_id = db.Column(db.Integer, db.ForeignKey('categories.cat_id'),
                        nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.brand_id'),
                        nullable=False)
    # Record owner of item.
    owner_cust_id = db.Column(db.Integer, db.ForeignKey('customers.cust_id'),
                                nullable=False)
    available = db.Column(db.Boolean, default=True)
    model = db.Column(db.String(16), nullable=False)
    condition = db.Column(db.String(128))
    description = db.Column(db.String(128))
    avail_start_date = db.Column(db.DateTime, nullable=False, default=datetime.date.today())
    avail_end_date = db.Column(db.DateTime, nullable=False, default=datetime.date.today())
    price_per_day = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(128))

    tent = db.relationship('Tent', uselist=False, backref='product')
    owner = db.relationship('Customer', backref='products')
    brand = db.relationship('Brand', backref='products')


    # TODO next round: put in constraints. Need to import CheckConstraint
    # Do these work?
    # __table_args__ = (CheckConstraint(avail_start_date >= datetime.date.utcnow,
    #                   {})
    # __table_args__ = (CheckConstraint(avail_end_date > avail_start_date, {})

    def __repr__(self):
        return "<Product prod_id=%r, cat_id=%r, renter_cust_id=%r, model=%r, condition=%r, avail=%r to %r, price=%r>" % (
            self.prod_id, self.cat_id, self.owner_cust_id, self.model, self.condition,
            self.avail_start_date, self.avail_end_date, self.price_per_day)


# class SearchWord(db.Model):
#     """Hold fields to do text search"""

#     __tablename__ = "search_words"

#     prod_id = db.Column(db.Integer, db.ForeignKey('products.prod_id'),
#                         primary_key=True)
#     search_words = db.Column(db.String(256), nullable=False)

#     def __repr__(self):
#         return "<Search search_id=%r, prod_id=%r, search_words=%r>" % (
#             self.search_id, self.prod_id, self.search_words)


class Tent(db.Model):
    """Tent is one of the subset tables of Product"""

    __tablename__ = 'tents'

    prod_id = db.Column(db.Integer, db.ForeignKey('products.prod_id'),
                        primary_key=True)
    use_id = db.Column(db.Integer, db.ForeignKey('best_uses.use_id'),
                        nullable=False)
    sleep_capacity = db.Column(db.Integer, nullable=False)
    seasons = db.Column(db.Integer, nullable=False)
    min_trail_weight = db.Column(db.Integer)
    floor_width = db.Column(db.Integer)
    floor_length = db.Column(db.Integer)
    num_doors = db.Column(db.Integer)
    num_poles = db.Column(db.Integer)

    def __repr__(self):
        return "<Tent prod_id=%r, use_id=%r, capacity=%r, seasons=%r, weight=%r, length=%r, width=%r, num_doors=%r, num_poles=%r>" % (
            self.prod_id, self.use_id, self.sleep_capacity,
            self.seasons, self.min_trail_weight, self.floor_width,
            self.floor_length, self.num_doors, self.num_poles)


class History(db.Model):
    """Rental histories"""

    __tablename__ = 'histories'

    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prod_id = db.Column(db.Integer, db.ForeignKey('products.prod_id'),
                        nullable=False)
    renter_cust_id = db.Column(db.Integer, db.ForeignKey('customers.cust_id'),
                        nullable=False)
    # owner_cust_id = db.Column(db.Integer, db.ForeignKey('customers.cust_id'),
    #                     nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
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