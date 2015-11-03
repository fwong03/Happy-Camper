"""Happy Camper"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db
from model import User, Region, Product, BestUse, Tent
# Category
from helpers import get_lat_lngs, make_product, get_brands, calc_dates
from datetime import datetime


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Signed out homepage."""
    # Is there a way to deal with login with if/else Get vs Post request?

    return render_template("signedout.html")


@app.route('/login')
def login():
    """User login page."""

    return render_template("login.html")


@app.route('/logout')
def handle_logout():
    """Process logout"""

    session.pop('user')
    return redirect('/')


@app.route('/handle-login', methods=['POST'])
def handle_login():
    """Process login form"""

    username = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter(User.email == username).one()

    if user:
        if user.password == password:
            session['user'] = username
            flash("Welcome! Logged in as %s" % username)
            return redirect('/success')
        else:
            flash("Login failed. Please try again.")
            return redirect('/')


@app.route('/createaccount')
def create_account():
    """Where new users create an account"""

    return render_template("createaccount.html")



@app.route('/handle-createaccount', methods=['POST'])
def handle_createaccount():
    """Process create account form.

    To create the user, this function calls the
    get_lat_lngs function from helpers.py.

    """

    password = request.form.get('pword')
    confirm_pword = request.form.get('confirm_pword')

    if password != confirm_pword:
        flash("Passwords don't match. Try again.")
        return redirect('/createaccount')
    else:
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        staddress = request.form.get('staddress')
        cty = request.form.get('cty')
        state = request.form.get('state')
        zipcode = request.form.get('zipcode')
        phonenumber = int(request.form.get('phonenumber'))
        username = request.form.get('username')

        # Get region id from the Regions table
        region = Region.query.filter(Region.abbr == state).one()
        state_id = region.region_id

        # Get latitude and longitude from helper function
        lat_lng = get_lat_lngs(staddress + " " + zipcode)
        latitude = lat_lng[0]
        longitude = lat_lng[1]

        user = User(fname=firstname, lname=lastname, street=staddress,
                    city=cty, region_id=state_id, postalcode=zipcode,
                    lat=latitude, lng=longitude, phone=phonenumber,
                    email=username, password=password)

        db.session.add(user)
        db.session.commit()

        session['user'] = username
        flash("Successfully created account! Logged in as %s" % username)

        return redirect('/success')



@app.route('/success')
def enter_site():
    """Signed in home page."""

    customer = User.query.filter(User.email == session['user']).one()
    dates = calc_dates(30)

    return render_template("success.html", user=customer,
                            p_today=dates['today_string'],
                            p_month=dates['future_string'])




@app.route('/account-info')
def show_account():
    """Where users can check out their account details.

    They can also delete listings, rate stuff, get the emails of people
    renting to or renting from.
    """
    user = User.query.filter(User.email == session['user']).one()
    fname = user.fname
    lname = user.lname
    staddress = user.street
    cty = user.city
    state_id = user.region_id
    st = Region.query.get(state_id).full
    zcode = user.postalcode
    phonenumber = user.phone

    inventory = Product.query.filter(Product.owner_user_id == user.user_id).all()

    return render_template("accountinfo.html", firstname=fname, lastname=lname,
                           street=staddress, city=cty, state=st, zipcode=zcode,
                           phone=phonenumber, email=session['user'],
                           products=inventory)


@app.route('/list-item')
def list_item():
    """List an item page.

    Routes from signed in homepage, which has a button to List an Item.
    Routes to item detail page.
    """
    return render_template("list-item.html")


@app.route('/list-tent')
def list_tent():
    allbrands = get_brands()
    dates = calc_dates(30)

    return render_template("list-tent.html", brands=allbrands,
                           submit_route='/handle-tent',
                           p_today=dates['today_string'],
                           p_month=dates['future_string'])


@app.route('/handle-tent', methods=['POST'])
def handle_tent_listing():
    """Handle tent listing. Makes a parent Product object, adds it to the database
    so you have a PK, then make the assoicated Tent object.
    """
    # Make associated parent Product object.
    product = make_product()
    # Add and commit product to database so you can use its PK to make a tent.
    db.session.add(product)
    db.session.commit()

    # print product

    # Grab info to make a tent.
    bestuse = request.form.get("bestuse")
    sleep = int(request.form.get("sleep"))
    seasoncat = request.form.get("seasoncat")
    weight = int(request.form.get("weight"))

    # Get use_id from the BestUses table. This is required to make a tent.
    best_use = BestUse.query.filter(BestUse.use_name == bestuse).one()

    # Set optional values, if any

    try:
        width = int(request.form.get("width"))
    except ValueError:
        width = None

    try:
        length = int(request.form.get("length"))
    except ValueError:
        length = None

    try:
        doors = int(request.form.get("doors"))
    except ValueError:
        doors = None

    try:
        poles = int(request.form.get("poles"))
    except ValueError:
        poles = None

    tent = Tent(prod_id=product.prod_id, use_id=best_use.use_id,
                sleep_capacity=sleep, seasons=3, min_trail_weight=weight,
                floor_width=width, floor_length=length, num_doors=doors,
                num_poles=poles)

    db.session.add(tent)
    db.session.commit()

    flash("Listing successfully posted!")
    return redirect('/product-detail/%d' % product.prod_id)

@app.route('/list-sleepingbag')
def list_sleepingbag():
    return "This is where you'll list a sleeping bag."


@app.route('/list-sleepingpad')
def list_sleepingpad():
    return "This is where you'll list a sleeping pad."


@app.route('/list-pack')
def list_pack():
    return "This is where you'll list a pack."


@app.route('/list-stove')
def list_stove():
    return "This is where you'll list a stove."


@app.route('/list-waterfilter')
def list_waterfilter():
    return "This is where you'll list a water filter."



@app.route('/product-detail/<int:prod_id>')
def show_item(prod_id):
    """Product detail page.

    Routes either from Search Results page or List Item page.
    If click on Borrow This, routes to Borrowed version of this page.
    """
    # If item available = True, show regular product detail page.
    # If item available = False, show BOROWED version of page, which
    # doesn't allow you to borrow the item.
    # Show this BORROWED version after a user clicks "borrow this"
    # SHOW TOTAL COST given the date range the user gave in search

    item = Product.query.get(prod_id)

    if item.available:
        return render_template("product-detail.html", product=item)
    else:
        return "Sorry! The %s %s is no longer available for rent." % (
            item.brand.brand_name, item.model)


@app.route('/rent/<int:prod_id>')
def rent_item(prod_id):

    # Make rental confirmation page inbetween product detail and this one.
    # Create History object

    product = Product.query.get(prod_id)
    product.available = False
    db.session.commit()


    flash("You've succcessfully rented %s %s!" % (product.brand.brand_name, product.model))

    return "Prod_id=%d, available=%r" % (product.prod_id, product.available)


@app.route('/searchresults')
def show_results():
    """Search results page.

    Routes from Signed in Home Page.
    Routes to Item Detail page.

    """
    # For now find users in same zipcode
    # Then find products in same zipcode
    # Then find products in same zip code available within search dates.
    # Then expand to zipcode within radius
    search_area = request.args.get("search_area")
    date1 = request.args.get("date1")
    date2 = request.args.get("date2")

    date1 = datetime.strptime(date1, "%Y-%m-%d")
    date2 = datetime.strptime(date2, "%Y-%m-%d")


    # Test with just zipcode for now
    users_in_area = User.query.filter(User.postalcode == search_area).all()

    return render_template("searchresults.html", location=search_area,
        start_date=date1, end_date=date2, users=users_in_area)


@app.route('/renter_rate')
def renter_rate():
    """Rating page for renter.

    Here they can rent the owner and the product.
    Routes from Account page and routes to Account Page with flashed message
    thanking them for their rating."""

    return "Here renters can rate the owner and the product they rented."


@app.route('/owner_rate')
def owner_rate():
    """Rating page for owner.

    Owners rate renters. They access this page from their account page, and
    this routes to the account page with a flashed message thanking them."""

    return "Here owners can rate renters."





if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
