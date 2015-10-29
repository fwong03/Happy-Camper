from model import Customer
from model import connect_to_db, db
from server import app


def load_customers():
    print "Customers"
    Customer.query.delete()

    for row in open("data/customerdata"):
        row = row.strip()
        firstn, lastn, staddress, cty, sta, zcode, phn, login, pword = row.split("|")

        customer = Customer(fname=firstn, lname=lastn, street=staddress,
                            city=cty, state=sta, zipcode=zcode, phone=phn,
                            email=login, password=pword)

        db.session.add(customer)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_customers()
