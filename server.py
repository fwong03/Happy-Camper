"""Happy Camper"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Region, calc_dates
# Category, BestUse, Brand, Product, Tent



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


@app.route('/createaccount')
def create_account():
    """Where new users create an account"""

    return render_template("createaccount.html")


@app.route('/handle-createaccount', methods=['POST'])
def handle_createaccount():
    """Process create account form"""
    # TO DO: Put in checks.
    # Use dictionary for now to look up lat lngs. Meeting with
    # Heather Monday to discuss geolocation options.

    lat_lngs = {'94612': (37.806238, -122.268918),
                '94109': (37.791434, -122.420053),
                '95376': (37.739651, -121.425224),
                }

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
        phonenumber = request.form.get('phonenumber')
        username = request.form.get('username')

        region = Region.query.filter(Region.abbr == state).one()
        state_id = region.region_id
        lat_lng = lat_lngs[zipcode]
        latitude = lat_lng[0]
        longitude = lat_lng[1]

        phonenumber = int(phonenumber)

        # return "User: %s %s, Address: %s, %s %s %s, Region_id: %d, Phone: %d, email: %s, password: %s, lat: %r, lng: %r" % (
        #     firstname, lastname, staddress, cty, state, zipcode, state_id, phonenumber,
        #     username, password, latitude, longitude)

        user = User(fname=firstname, lname=lastname, street=staddress,
                    city=cty, region_id=state_id, postalcode=zipcode,
                    lat=latitude, lng=longitude, phone=phonenumber,
                    email=username, password=password)

        # return "User: %s %s" % (user.fname, user.lname)
        db.session.add(user)
        db.session.commit()

        session['user'] = username
        flash("Logged in as %s" % username)
        return redirect('/success')


@app.route('/login')
def login():
    """User login page."""

    return render_template("login.html")


@app.route('/handle-login', methods=['POST'])
def handle_login():
    """Process login form"""

    username = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter(User.email == username).one()

    if user:
        if user.password == password:
            session['user'] = username
            # Use below to set default location in search form
            # session['account_lat'] = user.lat
            # session['account_lng'] = user.lng
            flash("Logged in as %s" % username)
            return redirect('/success')
        else:
            flash("Login failed. Please try again.")
            return redirect('/')


@app.route('/logout')
def handle_logout():
    """Process logout"""

    username = session['user']
    print username
    session.pop('user')
    return redirect('/')


@app.route('/success')
def enter_site():
    """Signed in home page."""

    return render_template("success.html")


@app.route('/list-item')
def list_item():
    """List an item page.

    Routes from signed in homepage, which has a button to List an Item.
    Routes to item detail page.
    """
    return render_template("list-item.html")


# Make sure all these are form action POST.


@app.route('/list-tent')
def list_tent():
    dates = calc_dates()

    date1 = dates['today']
    date2 = dates['thirty']
    p_date1 = dates['today_print']
    p_date2 = dates['thirty_print']


    return render_template("list-tent.html",
                           submit_route='/handle-tent',
                           today=date1, p_today=p_date1,
                           month=date2, p_month=p_date2)

@app.route('/handle-tent', methods=['POST'])
def handle_tent_listing():
    
    return "Tent item listing will be processed here."


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


@app.route('/handle-listing', methods=['POST'])
def handle_listing():
    pass


@app.route('/product/<int:prod_id>')
def item_detail(prod_id):
    """Item detail page.

    Routes either from Search Results page or List Item page.
    If click on Borrow This, routes to Borrowed version of this page.
    """
    # If item available = True, show regular product detail page.
    # If item available = False, show BOROWED version of page, which
    # doesn't allow you to borrow the item.
    # Show this BORROWED version after a user clicks "borrow this"

    return "Where you can view item details for %d" % prod_id


@app.route('/searchresults')
def show_results():
    """Search results page.

    Routes from Signed in Home Page.
    Routes to Item Detail page.

    """

    return "This will be the search results."


@app.route('/customers/<int:user_id>')
def show_account(user_id):
    """Where users can check out their account details.

    They can also delete listings, rate stuff, get the emails of people
    renting to or renting from.

    Routes from account link in nav bar. Always accessible.
    """

    return "This will be the users account detail page."


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
