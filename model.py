# Models and database for Happy Camper project.
# Version 1
# October 27, 2015

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

##############################################################
# Model definitions

class Customer(db.Model):
    """Happy Camper user"""

    __tablename__ = "customers"

    cust_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(32), nullable=False)
    lname = db.Column(db.String(32), nullable=False)
    street = db.Column(db.String(32), nullable=False)
    city = db.Column(db.String(32), nullable=False)
    # TODO: for state, constraint in list of two-character state abbreviations
    state = db.Column(db.String(2), nullable=False)
    # TODO: for zipcode, constraint must be 5 numbers long
    zipcode = db.Column(db.Integer, nullable=False)
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
    cat_name = db.Column(db.String(8), nullable=False, unique=True)
    # Include category misspellings in search words field
    cat_search_words = db.Column(db.String(128), nullable=False)





class Product(db.Model):
    """Product parent class"""

    __tablename__ = 'products'


