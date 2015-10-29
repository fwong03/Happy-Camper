from model import Customer, BestUse, Brand
from model import connect_to_db, db
from server import app


def load_customers():
    """Load fake customer data"""

    print "Customers"
    # Delete rows of existing table, if any
    Customer.query.delete()

    for row in open("data/customerdata"):
        row = row.strip()
        firstn, lastn, staddress, cty, sta, zcode, phn, login, pword = row.split("|")

        customer = Customer(fname=firstn, lname=lastn, street=staddress,
                            city=cty, state=sta, zipcode=zcode, phone=phn,
                            email=login, password=pword)

        db.session.add(customer)

    db.session.commit()


def load_bestuses():
    """Load best use categories"""

    print "BestUses"
    BestUse.query.delete()

    for row in open("data/bestusesdata"):
        use = row.strip()

        bestuse = BestUse(use_name=use)

        db.session.add(bestuse)

    db.session.commit()


def load_brands():
    """Load brand names"""

    print "Brands"
    Brand.query.delete()

    for row in open("data/brandsdata"):
        name = row.strip()

        b = Brand(brand_name=name)

        db.session.add(b)

    db.session.commit()





if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_customers()
    load_bestuses()
    load_brands()
