from model import Customer
from model import connect_to_db, db
from server import app

fnames = ['Jerrell', 'Tiffany', 'Drusilla', 'Collis', 'Dreama',
        'Cross', 'Evonne', 'Baggs', 'Laurene', 'Wolfenbarger',
        'Leeanne', 'Hord', 'Edwardo', 'Puff','Phillip',
        'Lemaire', 'Erma', 'Pledger', 'Cruz', 'Wolf']

lnames = ['Nelda', 'Hehn', 'Terrilyn', 'Schneider', 'Dylan',
        'Marsala', 'Tambra','Scales', 'Jennell', 'Sudduth',
        'Felisa', 'Henson', 'Dede', 'Surita', 'Colene',
        'Delcid', 'Jere', 'Wee', 'Vaughn', 'Zickefoose']

street_addresses = ['666 Ashley Court', '304 Mulberry Court ', '812 Madison Court',
'851 Main Street North', '891 Church Street North',
    '666 Ashley Court','304 Mulberry Court ', '812 Madison Court',
'851 Main Street North','891 Church Street North',
    '666 Ashley Court', '304 Mulberry Court ','812 Madison Court',
'851 Main Street North', '891 Church Street North',
    '666 Ashley Court', '304 Mulberry Court ', '812 Madison Court',
'851 Main Street North', '891 Church Street North']

cities = ['Oakland', 'San Francisco', 'Mountain View', 'Tracy',
'Oakland', 'San Francisco', 'Mountain View', 'Tracy',
'Oakland', 'San Francisco', 'Mountain View', 'Tracy',
'Oakland', 'San Francisco', 'Mountain View', 'Tracy',
'Oakland', 'San Francisco', 'Mountain View', 'Tracy']

zipcodes= [94612, 94109, 94043, 95376,
94612, 94109, 94043, 95376,
94612, 94109, 94043, 95376,
94612, 94109, 94043, 95376,
94612, 94109, 94043, 95376]


def load_users(fnames, lnames, street_addresses, cities, zipcodes):
    print "Customers"
    Customer.query.delete()

    for i in range(len(fnames)):
        firstname = fnames[i]
        lastname = lnames[i]
        staddress = street_addresses[i]
        cy = cities[i]
        zcode = zipcodes[i]
        login = "%s@%s.com" % (firstname, lastname)

        customer = Customer(fname=firstname, lname=lastname,
            active=True, street=staddress, city=cy, state='CA',
            zipcode=zcode, phone=5555555555, email=login,
            password='abc')

        db.session.add(customer)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users(fnames, lnames, street_addresses, cities, zipcodes)

