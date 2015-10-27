"""Models and database functions for Happy Camper project."""

from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime - DO I NEED THIS?

# Establish connection to SQLite database
db = SQLAlchemy()

#############################################################################
# Model definitions


class Customer(db.Model):
    """Customer info"""

    __tablename__ = 'customers'

    cust_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(16), nullable=False)
    lname = db.Column(db.String(16), nullable=False)
    street = db.Column(db.String(64), nullable=False)
    city = db.Column(db.String(32), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zipcode = db.Column(db.String(16), nullable=False)



class Product(db.Model):
    """Product parent class."""

    __tablename__ = 'products'

    prod_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_id = db.Column(db.Integer, db.ForeignKey('categories.cat_id'),
                        nullable=False)
    # Record owner of item.
    renter_cust_id = db.Column(db.Integer, db.ForeignKey('customers.cust_id'),
                                nullable=False)
    brand = db.Column(db.String(16), nullable=False)
    model = db.Column(db.String(16), nullable=False)
    condition = db.Column(db.String(128), nullable=False)
    avail_start_date = db.Column(db.DateTime, nullable=False,
                        default=datetime.date.utcnow)
    avail_end_date = db.Column(db.DateTime, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)

    # TODO next round: put in constraints. Need to import CheckConstraint
    # Do these work?
    # __table_args__ = (CheckConstraint(avail_start_date >= datetime.date.utcnow,
    #                   {})
    # __table_args__ = (CheckConstraint(avail_end_date > avail_start_date, {})

