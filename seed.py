from model import Region, User, BestUse, Category, Brand, Product, Tent
from model import FillType, Gender, SleepingBag, History
from model import connect_to_db, db
from server import app
from datetime import datetime
from helpers import get_lat_lngs
# from geolocation.google_maps import GoogleMaps
import os


def load_regions():
    """Load regions, i.e. states, for user addresses"""

    print "Regions"
    Region.query.delete()

    for row in open("data/regionsdata"):
        row = row.strip()
        abbr, full = row.split("|")

        a = Region(abbr=abbr, full=full)

        db.session.add(a)

    db.session.commit()


def load_users():
    """Load user data"""

    print "Users"
    # Delete rows of existing table, if any
    User.query.delete()

    for row in open("data/customerdata"):
        row = row.strip()
        row = row.split("|")

        firstn = row[0]
        lastn = row[1]
        staddress = row[2]
        cty = row[3]
        region = row[4]
        zcode = row[5]
        latde = row[6]
        lontde = row[7]
        phn = int(row[8])
        login = row[9]
        pword = row[10]

        lat_lngs = get_lat_lngs(staddress + " " + zcode)
        latde = lat_lngs[0]
        lontde = lat_lngs[1]

        a = User(fname=firstn, lname=lastn, street=staddress,
                 city=cty, region_id=region, postalcode=zcode, lat=latde,
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
    """Load products data"""

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

        a = Product(cat_id=category, brand_id=brand, owner_user_id=owner,
                    model=mname, condition=con, description=desc,
                    avail_start_date=date1, avail_end_date=date2,
                    price_per_day=dollarz)

        db.session.add(a)

    db.session.commit()


def load_tents():
    """Load tents data"""

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

        a = Tent(prod_id=product, use_id=use, sleep_capacity=capacity,
                 seasons=num_sea, min_trail_weight=weight, floor_width=width,
                 floor_length=length, num_doors=doors, num_poles=poles)

        db.session.add(a)

    db.session.commit()


def load_filltypes():
    """Load sleeping bag fill types"""

    print "Fill Types"
    FillType.query.delete()

    for row in open("data/filltypesdata"):
        row = row.strip()
        code, name = row.split("|")

        a = FillType(fill_code=code, fill_name=name)

        db.session.add(a)

    db.session.commit()


def load_gendertypes():
    """Load gender types"""

    print "Gender Types"
    Gender.query.delete()

    for row in open("data/gendersdata"):
        row = row.strip()
        code, name = row.split("|")

        a = Gender(gender_code=code, gender_name=name)

        db.session.add(a)

    db.session.commit()


def load_sleepingbags():
    """Load sleeping bags data"""

    print "Sleeping Bags"
    SleepingBag.query.delete()

    for row in open("data/sleepingbagsdata"):
        row = row.strip()
        row = row.split("|")

        product = int(row[0])
        fill = row[1]
        temp = int(row[2])
        wt = int(row[3])
        lgth = int(row[4])
        ger = row[5]

        a = SleepingBag(prod_id=product, fill_code=fill, temp_rating=temp,
                        weight=wt, length=lgth, gender_code=ger)

        db.session.add(a)

    db.session.commit()

def load_histories():
    """Load history data"""

    print "Histories"
    History.query.delete()

    for row in open("data/historiesdata"):
        row = row.strip()
        row = row.split("|")
        print row

        product = int(row[0])
        renter = int(row[1])
        date1 = row[2]
        date2 = row[3]
        cost = float(row[4])

        try:
            owner_rate = int(row[5])
        except ValueError:
            owner_rate = None
        try:
            renter_rate = int(row[6])
        except ValueError:
            renter_rate = None
        try:
            prod_rate = int(row[7])
        except ValueError:
            prod_rate = None

        date1 = datetime.strptime(date1, "%Y-%m-%d")
        date2 = datetime.strptime(date2, "%Y-%m-%d")

        a = History(prod_id=product, renter_user_id=renter, start_date=date1,
                 end_date=date2, total_cost=cost, owner_rate_id=owner_rate,
                 renter_rate_id=renter_rate, prod_rate_id=prod_rate)

        db.session.add(a)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Seed data
    load_regions()
    load_users()
    load_bestuses()
    load_categories()
    load_brands()
    load_products()
    load_tents()
    load_filltypes()
    load_gendertypes()
    load_sleepingbags()
    load_histories()
