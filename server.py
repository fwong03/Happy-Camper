"""Happy Camper"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db
from model import User, Region, Product, BestUse, Tent, Brand, History, Category
from helpers import get_lat_lngs, search_radius
from helpers import calc_default_dates, convert_string_to_datetime
from helpers import make_product, categorize_products, get_brands


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# If you use an undefined variable in Jinja2, it will fails silently. Put this
# in to instead raise an error.
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
            # Add user email to Flask session
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
    dates = calc_default_dates(30)

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

    products_all = Product.query.filter(Product.owner_user_id == user.user_id).all()
    products_avail = []
    products_out = []

    for product in products_all:
        if product.available:
            products_avail.append(product)
        else:
            products_out.append(product)

    rentals = db.session.query(History.history_id, History.start_date,
                               History.end_date, Brand.brand_name, Product.model,
                               History.total_cost).join(Product).join(Brand).filter(History.renter_user_id == user.user_id).all()

    return render_template("accountinfo.html", firstname=fname, lastname=lname,
                           street=staddress, city=cty, state=st, zipcode=zcode,
                           phone=phonenumber, email=session['user'],
                           products_available=products_avail,
                           products_not_available=products_out, histories=rentals)


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
    dates = calc_default_dates(30)

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

    # Grab info to make a tent.
    bestuse = request.form.get("bestuse")
    sleep = int(request.form.get("sleep"))
    seasoncat = request.form.get("seasoncat")
    weight = int(request.form.get("weight"))

    # Get use_id from the BestUses table. This is required to make a tent.
    best_use = BestUse.query.filter(BestUse.use_name == bestuse).one()

    # Set optional values, if any provided
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


@app.route('/searchresults')
def show_results():
    """Search results page.

    Routes from Signed in Home Page.
    Routes to Item Detail page.

    """
    # STILL LEFT TO DO: Return products available within dates given

    search_area = request.args.get("search_area")
    search_miles = request.args.get("search_miles")
    date1 = request.args.get("date1")
    date2 = request.args.get("date2")

    # Convert the dates into datetimes and get the number of days the user is
    # interested in renting an item so we can calculate his or her total rental cost.
    date1 = convert_string_to_datetime(date1)
    date2 = convert_string_to_datetime(date2)

    # Add the rental dates to the flask session so we can access over multiple
    # pages.
    days = (date2 - date1).days + 1

    session['date1'] = date1
    session['date2'] = date2
    session['num_days'] = days

    try:
        search_miles = int(search_miles)
    except ValueError:
        flash("Search radius must be an integer. Please try again.")
        return redirect('/success')

    # Find distinct postal codes in the database. This query returns a list of
    # tuples.
    query = db.session.query(User.postalcode).distinct()
    postalcodes = query.all()

    # Call helper function that returns postal codes within the given
    # search radius.
    postal_codes = search_radius(search_area, postalcodes, search_miles)

    # Now we get the users within the postal codes returned by searcg_radius.
    users_in_area = User.query.filter(User.postalcode.in_(postal_codes)).all()

    # Take out the currently logged in user, if in the users_in_area list
    logged_in_user = User.query.filter(User.email == session['user']).one()

    if logged_in_user in users_in_area:
        users_in_area.remove(logged_in_user)

    categories = Category.query.all()
    categorized_products = categorize_products(categories, users_in_area)
    
    sorted_cats = sorted(categorized_products.keys())

    # Make and call a seprate function that does the following:
    #   Get list of users in area
    #   For each product they have for rent,
    #       1. Check it's available
    #       2. Check it's available for search dates.
    #       3. If yes to both, separate into list of tents, sleeping bags, etc
    #   Return these lists of tents, sleeping bags, etc in separate lists
    # Display these lists in separate section in the search results page.

    return render_template("searchresults.html", location=search_area,
                           miles=search_miles, start_date=date1, end_date=date2,
                           num_days=days, sorted_categories=sorted_cats, products=categorized_products)


@app.route('/product-detail/<int:prod_id>')
def show_item(prod_id):
    """Product detail page.

    Routes either from Search Results page or List Item page.
    If click on Borrow This, routes to Borrowed version of this page.
    """
    # Make this a base template then make separate templates for
    # tents, sleeping bags, etc that extend.
    # Make a separate listing confirmation page for rentees.
    # For potential renters, show total cost.
    # Make a borrowed version if available = False.

    item = Product.query.get(prod_id)

    if item.available:
        return render_template("product-detail.html", product=item)
    else:
        # Make a template for this.
        return "Sorry! T search results he %s %s is no longer available for rent." % (
            item.brand.brand_name, item.model)


@app.route('/rent-confirm/<int:prod_id>', methods=['POST'])
def confirm_rental(prod_id):
    """When a user clicks to rent on object, this page
    confirms they actually meant to rent the item.
    """

    prod = Product.query.get(prod_id)

    # On template provide link to original search results if change their mind.

    return render_template("rent-confirm.html", product=prod,
                           rental_start_date=session['date1'],
                           rental_end_date=session['date2'],
                           num_days=session['num_days'])


@app.route('/handle-rental/<int:prod_id>', methods=['POST'])
def handle_rental(prod_id):
    """Process a rental. Create associated History object.

    """
    user = User.query.filter(User.email == session['user']).one()
    product = Product.query.get(prod_id)
    cost = product.price_per_day * session['num_days']

    history = History(prod_id=prod_id, renter_user_id=user.user_id,
                      start_date=session['date1'], end_date=session['date2'],
                      total_cost=cost)

    product.available = False
    db.session.add(history)
    db.session.commit()

    return redirect('/rental-finalized')


@app.route('/rental-finalized')
def rent_item():
    """Show rental confirmation page to user."""

    return render_template("rent-final.html")


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



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
