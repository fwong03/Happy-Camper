from model import Product
from datetime import datetime

def load_products():
    """Load fake products data"""

    print "Products"

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

        print a


load_products()
