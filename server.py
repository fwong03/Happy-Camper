"""Happy Camper"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User
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

    return render_template("signedout.html")

@app.route('/createaccount')
def create_account():
    """Where new users create an account"""

    return "New users will create an account here."


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
            # session['account_lat'] = user.lat
            # session['account_lng'] = user.lng
            flash("Logged in as %s" % username)
            return redirect('/success')
        else:
            flash("Login failed. Please try again.")
            return redirect('/')


@app.route('/success')
def success():
    """Signed in home page."""

    render_template("success.html")


@app.route('/list_item')
def list_item():
    """List an item page. 

    Routes from signed in homepage, which has a button to List an Item.
    Routes to item detail page.
    """

    return "Where you can list an item to rent out."

@app.route('/product/<int:prod_id>')
def item_detail(prod_id):
    """Item detail page.

    Routes either from Search Results page or List Item page.
    If click on Borrow This, routes to Borrowed version of this page.
    """
    # If item is available, show regular product detail page.
    # If item is not available, show BOROWED version of page.
    # Allows you to borrow only if Available is True.

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
