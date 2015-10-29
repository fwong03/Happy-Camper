from model import Customer, BestUse, Category, Brand, Product, Tent
from model import connect_to_db, db
from server import app
from datetime import datetime


def load_customers():
    """Load fake customer data"""

    print "Customers"
    # Delete rows of existing table, if any
    Customer.query.delete()

    for row in open("data/customerdata"):
        row = row.strip()
        row= row.split("|")

        firstn = row[0]
        lastn = row[1]
        staddress = row[2]
        cty = row[3]
        sta = row[4]
        zcode = row[5]
        latde = row[6]
        lontde = row[7]
        phn = row[8]
        login = row[9]
        pword = row[10]

        zcode = int(zcode)
        latde = float(latde)
        lontde = float(lontde)
        phn = int(phn)

        a = Customer(fname=firstn, lname=lastn, street=staddress,
                            city=cty, state=sta, zipcode=zcode, lat=latde,
                            lng=lontde, phone=phn, email=login, password=pword)

        db.session.add(a)

    db.session.commit()


def load_bestuses():
    """Load best use categories"""

    print "BestUses"
    BestUse.query.delete()

    for row in open("data/bestusesdata"):
        use = row.strip()

        a = BestUse(use_name=use)

        db.session.add(a)

    db.session.commit()


def load_categories():
    """Load product categories"""

    print "Categories"
    Category.query.delete()

    for row in open("data/categoriesdata"):
        name = row.strip()

        a = Category(cat_name=name)

        db.session.add(a)

    db.session.commit()


def load_brands():
    """Load brand names"""

    print "Brands"
    Brand.query.delete()

    for row in open("data/brandsdata"):
        name = row.strip()

        a = Brand(brand_name=name)

        db.session.add(a)

    db.session.commit()


def load_products():
    """Load fake products data"""

    print "Products"
    Product.query.delete()

    for row in open("data/productsdata"):
        row = row.strip()
        row = row.split("|")

        print row

        category = row[0]
        brand = int(row[1])
        owner = row[2]
        mname = row[3]
        con = row[4]
        desc = row[5]
        date1 = row[6]
        date2 = row[7]
        dollarz = float(row[8])


        date1 = datetime.strptime(date1, "%Y-%m-%d")
        date2 = datetime.strptime(date2, "%Y-%m-%d")

        a = Product(cat_id=category, brand_id=brand,
                            owner_cust_id=owner, model=mname, condition=con,
                            description=desc, avail_start_date=date1,
                            avail_end_date=date2, price_per_day=dollarz)

        db.session.add(a)

    db.session.commit()


def load_tents():
    """Load fake tents data"""

    print "Tents"
    Tent.query.delete()

    for row in open("data/tentsdata"):
        row = row.strip()
        row = row.split("|")

        product = int(row[0])
        use = int(row[1])
        capacity = int(row[2])
        num_sea = int(row[3])
        weight = int(row[4])
        width = int(row[5])
        length = int(row[6])
        doors = int(row[7])
        poles = int(row[8])

        a = Tent(prod_id=product, use_id=use,
                            sleep_capacity=capacity, seasons=num_sea,
                            min_trail_weight=weight, floor_width=width,
                            floor_length=length, num_doors=doors,
                            num_poles=poles)

        db.session.add(a)

    db.session.commit()



if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_customers()
    load_bestuses()
    load_categories()
    load_brands()
    load_products()
    load_tents()
