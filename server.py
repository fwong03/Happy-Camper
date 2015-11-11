"""Happy Camper"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db
from model import User, Region, Product, BestUse, Tent, SleepingBag
from model import Brand, History, Category, Rating
from helpers import get_lat_lngs, search_radius
from helpers import calc_default_dates, convert_string_to_datetime
from helpers import make_product, categorize_products
from helpers import calc_avg_star_rating
from datetime import datetime


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
    # Make username can display for ratings?

    return render_template("login.html")


@app.route('/logout')
def handle_logout():
    """Process logout"""

    session.clear()
    return redirect('/')


@app.route('/handle-login', methods=['POST'])
def handle_login():
    """Process login form"""

    username = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter(User.email == username).one()

    if (user.active) and (user.password == password):
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
    dates = calc_default_dates(7)

    return render_template("success.html", user=customer,
                           p_today=dates['today_string'],
                           p_month=dates['future_string'])


@app.route('/account-info')
def show_account():
    """Where users can check out their account details.

    They can also delete listings, rate stuff, get the emails of people
    renting to or renting from.
    """
    customer = User.query.filter(User.email == session['user']).one()
    state_id = customer.region_id
    st = Region.query.get(state_id).full

    today_date = datetime.today()

    products_all = Product.query.filter(Product.owner_user_id == customer.user_id).all()
    products_avail = []
    products_out = []

    for product in products_all:
        if product.available:
            products_avail.append(product)
        else:
            products_out.append(product)

    rentals = History.query.filter(History.renter_user_id == customer.user_id).all()

    return render_template("account-info.html", user=customer, state=st,
                           products_available=products_avail,
                           products_not_available=products_out,
                           histories=rentals, today=today_date)


@app.route('/confirm-deactivate-account')
def confirm_deactivate_account():
    """Confirm the user wants to deactivate account"""

    return render_template("confirm-deactivate-account.html")


@app.route('/handle-deactivate-account', methods=['POST'])
def deactivate_account():
    """Deactivate user account.

        Sets availablility to each owner's product to false.
        Sets user active to false.
    """
    user = User.query.filter(User.email == session['user']).one()
    products = user.products

    for product in products:
        product.available = 0

    user.active = 0
    db.session.commit()
    session.clear()

    flash("Your account has been deactivated. Thank you for using Happy Camper!")

    return redirect('/')


@app.route('/list-item')
def list_item():
    """List an item page.

    Routes from signed in homepage, which has a button to List an Item.
    Routes to item detail page.
    """
    return render_template("list-item.html")


@app.route('/list-tent')
def list_tent():
    # 11/9: Changed from return list of brand names to just use brand objects.
    # This way can use brand_id has value returned from list-base template.
    # Also changed value of "add new brand" to -1. Per Drew rec.
    all_brands = Brand.query.all()
    dates = calc_default_dates(30)

    # Change so pass in BestUse objects and use best_use_id as value?
    return render_template("list-tent.html", brands=all_brands,
                           submit_route='/handle-tent',
                           p_today=dates['today_string'],
                           p_month=dates['future_string'])


@app.route('/handle-tent', methods=['POST'])
def handle_tent_listing():
    """Handle tent listing.

    First checks if it needs to make a new Brand. If so, makes a new Brand object.

    Then makes Product object. Calls a function where you need to pass it the
    brand_id and cat_id. For tents, cat_id==1.

    Then makes a Tent object. Need to pass it the same primary key of the parent
    Product object.
    """
    # Tent category ID is 1
    cat_id = 1
    # Check if new brand. If so make new brand and add to database.
    brd_id = int(request.form.get("brand_id"))

    if brd_id < 0:
        new_brand_name = request.form.get("new_brand_name")
        brand = Brand(brand_name=new_brand_name)
        db.session.add(brand)
        db.session.commit()
        brd_id = brand.brand_id

    product = make_product(brand_id=brd_id, category_id=cat_id)
    db.session.add(product)
    db.session.commit()

    # Grab info to make a tent.
    best_use_id = int(request.form.get("bestuse"))
    sleep = int(request.form.get("sleep"))
    seasoncat = int(request.form.get("seasoncat"))
    weight = int(request.form.get("weight"))

    best_use = BestUse.query.get(best_use_id)

    # Below are optional values.
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

    tent = Tent(prod_id=product.prod_id, use_id=best_use_id,
                sleep_capacity=sleep, seasons=seasoncat, min_trail_weight=weight,
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

    search_area = request.args.get("search_area")
    search_miles = request.args.get("search_miles")
    search_start_date = request.args.get("search_start_date")
    search_end_date = request.args.get("search_end_date")

    try:
        search_miles = int(search_miles)
    except ValueError:
        flash("Search radius must be an integer. Please try again.")
        return redirect('/success')

    # Convert the dates into datetimes and get the number of days the user is
    # interested in renting an item so we can calculate his or her total rental cost.
    search_start_date = convert_string_to_datetime(search_start_date)
    search_end_date = convert_string_to_datetime(search_end_date)

    # Add the rental dates to the flask session so we can access over multiple
    # pages.
    days = (search_end_date - search_start_date).days + 1

    # Future version maybe save to table last search so default next search to that.

    session['search_start_date'] = search_start_date
    session['search_end_date'] = search_end_date
    session['num_days'] = days
    session['search_area'] = search_area
    session['search_radius'] = search_miles

    # Find distinct postal codes in the database.
    query = db.session.query(User.postalcode).distinct()
    postalcodes = query.all()

    # Get postal codes within the given search radius.
    # Save zipcode pair distances to DB the first time.
    postal_codes = search_radius(search_area, postalcodes, search_miles)

    # Get users within the postal codes.
    users_in_area = User.query.filter(User.postalcode.in_(postal_codes)).all()

    # Take out the currently logged in user, if in the list.
    logged_in_user = User.query.filter(User.email == session['user']).one()

    if logged_in_user in users_in_area:
        users_in_area.remove(logged_in_user)

    # Get categories so can categorize products
    categories = Category.query.all()

    # Separate check if available during dates and categorization
    categorized_products = categorize_products(categories, users_in_area,
                                               session['search_start_date'],
                                               session['search_end_date'])
    sorted_cats = sorted(categorized_products.keys())

    return render_template("searchresults.html", location=search_area,
                           miles=search_miles,
                           start_date_string=session['search_start_date'].date().isoformat(),
                           end_date_string=session['search_end_date'].date().isoformat,
                           sorted_categories=sorted_cats,
                           products=categorized_products)


# @app.route('/product-detail/<int:prod_id>')
# def show_item(prod_id):
#     """Product detail page.

#     Routes either from Search Results page or List Item page.
#     If click on Borrow This, routes to Borrowed version of this page.
#     """
#     # Make a borrowed template version if available = False instead

#     item = Product.query.get(prod_id)

#     return render_template("product-detail.html", product=item)


@app.route('/product-detail/<int:prod_id>')
def show_product(prod_id):
    """Product detail page.

    Routes either from Search Results page or List Item page.
    If click on Borrow This, routes to Borrowed version of this page.
    """
    # Make a borrowed template version if available = False instead

    categories = {1: Tent.query.get(prod_id),
                  2: SleepingBag.query.get(prod_id),
                  # 3: SleepingPad.query.get(prod_id),
                  # 4: Pack.query.get(prod_id),
                  # 5: Stove.query.get(prod_id),
                  # 6: WaterFilter.query.get(prod_id),
                  }

    templates = {1: 'tent.html',
                 2: 'sleeping-bag.html',
                 3: 'sleeping-pad.html',
                 4: 'pack.html',
                 5: 'stove.html',
                 6: 'water-filter.html',
                 }

    parent_product = Product.query.get(prod_id)
    cat_id = parent_product.cat_id

    child_item = categories[cat_id]

    return render_template(templates[cat_id], product=parent_product,
                           item=child_item)


@app.route('/rent-confirm/<int:prod_id>', methods=['POST'])
def confirm_rental(prod_id):
    """When a user clicks to rent on object, this page
    confirms they actually meant to rent the item.
    """

    prod = Product.query.get(prod_id)
    search_start_date_string = session['search_start_date'].date().isoformat()
    search_end_date_string = session['search_end_date'].date().isoformat()

    return render_template("rent-confirm.html", product=prod,
                           start_date_string=search_start_date_string,
                           end_date_string=search_end_date_string)


@app.route('/handle-rental/<int:prod_id>', methods=['POST'])
def handle_rental(prod_id):
    """Process a rental. Create associated History object.

    """
    user = User.query.filter(User.email == session['user']).one()
    product = Product.query.get(prod_id)
    cost = product.price_per_day * session['num_days']

    history = History(prod_id=prod_id, renter_user_id=user.user_id,
                      start_date=session['search_start_date'],
                      end_date=session['search_end_date'],
                      total_cost=cost)

    product.available = False
    db.session.add(history)
    db.session.commit()

    flash("Rental finalized! Check your account page under \"Items Rented\" for info.")

    return redirect('/account-info')


@app.route('/rental-finalized')
def rent_item():
    """Show rental confirmation page to user."""

    return render_template("rent-final.html")


@app.route('/show-owner-ratings/<int:user_id>')
def show_owner_ratings(user_id):
    """Show owner star ratings and any comments.

    Routes from Product detail and Account Info page.
    """

    owner = User.query.get(user_id)
    products = owner.products

    owner_ratings = []

    for product in products:
        # Can do something along lines of .filter(owner_rating.isnot(None))?
        for history in product.histories:
            if history.owner_rating:
                owner_ratings.append(history.owner_rating)

    avg_star_rating = calc_avg_star_rating(owner_ratings)

    return render_template("show-owner-ratings.html", ratings=owner_ratings,
                           average=avg_star_rating, prod=product)


@app.route('/show-renter-ratings/<int:renter_id>')
def show_renter_ratings(renter_id):
    """Show renter star ratings and any comments.

    Routes from account info page.
    """

    histories = History.query.filter(History.renter_user_id == renter_id).all()
    renter = User.query.get(renter_id)
    renter_email = renter.email

    renter_ratings = []

    for history in histories:
        # Can filter out null renter_ratings in line above?
        if history.renter_rating:
            renter_ratings.append(history.renter_rating)

    avg_star_rating = calc_avg_star_rating(renter_ratings)

    return render_template("show-renter-ratings.html", ratings=renter_ratings,
                           average=avg_star_rating, username=renter_email)


@app.route('/show-product-ratings/<int:prod_id>')
def show_product_ratings(prod_id):
    """Show product star ratings and any comments.

    Routes from product detail page.
    """

    item = Product.query.get(prod_id)
    histories = History.query.filter(History.prod_id == prod_id).all()

    product_ratings = []

    for history in histories:
        # Can filter out null renter_ratings in line above?
        if history.product_rating:
            product_ratings.append(history.product_rating)

    avg_star_rating = calc_avg_star_rating(product_ratings)

    return render_template("show-product-ratings.html", ratings=product_ratings,
                           average=avg_star_rating, product=item)


@app.route('/rate-owner/<int:owner_id>-<int:history_id>')
def rate_owner(owner_id, history_id):
    """Page to rate owner.

    """

    owner = User.query.get(owner_id)

    session['history_id_for_rating'] = history_id
    session['owner_username_for_rating'] = owner.email

    return render_template("rate-owner.html",
                           submit_route='/rate-owner-confirm/')


@app.route('/rate-owner-edit/')
def edit_owner_rating():
    """Page to edit rating of owner.

    """

    return render_template("rate-owner.html",
                           submit_route='/rate-owner-confirm/')


@app.route('/rate-owner-confirm/', methods=['POST'])
def confirm_owner_rating():
    """Confirm owner rating before adding to database"""

    stars = request.form.get("stars")
    comments = request.form.get("comments")

    return render_template("rate-owner-confirm.html", num_stars=stars,
                           comments_text=comments,
                           submit_route='/handle-owner-rating')


@app.route('/handle-owner-rating', methods=['POST'])
def handle_owner_rating():
    """Handle owner rating form submission.

    Will (1) create rating object and (2)update associated history object's
    owner_rating_id.
    """

    number_stars = int(request.form.get("number_stars"))
    comments_text = request.form.get("comments_text")

    owner_rating = Rating(stars=number_stars, comments=comments_text)
    db.session.add(owner_rating)
    db.session.commit()

    history = History.query.get(session['history_id_for_rating'])
    history.owner_rating_id = owner_rating.rating_id

    db.session.commit()

    session.pop('history_id_for_rating')
    session.pop('owner_username_for_rating')

    flash("Thank you for your rating!")

    return redirect('/account-info')


@app.route('/rate-product/<int:prod_id>-<int:history_id>')
def rate_product(prod_id, history_id):
    """Page to rate product.

    """

    item = Product.query.get(prod_id)

    session['history_id_for_rating'] = history_id
    session['prod_id_for_rating'] = prod_id
    session['prod_name_for_rating'] = "%s %s" % (item.brand.brand_name, item.model)

    return render_template("rate-product.html", product=item,
                           submit_route='/rate-product-confirm/')


@app.route('/rate-product-edit/')
def edit_product_rating():
    """Page to edit rating of product.

    """

    return render_template("rate-product.html",
                           submit_route='/rate-product-confirm/')


@app.route('/rate-product-confirm/', methods=['POST'])
def confirm_product_rating():
    """Confirm product rating before adding to database"""

    stars = request.form.get("stars")
    comments = request.form.get("comments")

    return render_template("rate-product-confirm.html", num_stars=stars,
                           comments_text=comments,
                           submit_route='/handle-product-rating')


@app.route('/handle-product-rating', methods=['POST'])
def handle_product_rating():
    """Handle product rating form submission.

    Will (1) create rating object and (2) update associated history object's
    prod_rating_id.
    """

    number_stars = int(request.form.get("number_stars"))
    comments_text = request.form.get("comments_text")

    product_rating = Rating(stars=number_stars, comments=comments_text)
    db.session.add(product_rating)
    db.session.commit()

    history = History.query.get(session['history_id_for_rating'])
    history.prod_rating_id = product_rating.rating_id

    db.session.commit()

    session.pop('history_id_for_rating')
    session.pop('prod_name_for_rating')

    flash("Thank you for your rating!")

    return redirect('/account-info')


@app.route('/rate-renter/<int:renter_id>-<int:history_id>')
def rate_renter(renter_id, history_id):
    """Page to rate renter.

    """

    renter = User.query.get(renter_id)

    session['history_id_for_rating'] = history_id
    session['renter_username_for_rating'] = renter.email

    return render_template("rate-renter.html",
                           submit_route='/rate-renter-confirm/')


@app.route('/rate-renter-edit/')
def edit_renter_rating():
    """Page to edit rating of renter.

    """

    return render_template("rate-renter.html",
                           submit_route='/rate-renter-confirm/')


@app.route('/rate-renter-confirm/', methods=['POST'])
def confirm_renter_rating():
    """Confirm renter rating before adding to database"""

    stars = request.form.get("stars")
    comments = request.form.get("comments")

    return render_template("rate-renter-confirm.html", num_stars=stars,
                           comments_text=comments,
                           submit_route='/handle-renter-rating')


@app.route('/handle-renter-rating', methods=['POST'])
def handle_renter_rating():
    """Handle renter rating form submission.

    Will (1) create rating object and (2) update associated history object's
    renter_rating_id.
    """

    number_stars = int(request.form.get("number_stars"))
    comments_text = request.form.get("comments_text")

    renter_rating = Rating(stars=number_stars, comments=comments_text)
    db.session.add(renter_rating)
    db.session.commit()

    history = History.query.get(session['history_id_for_rating'])
    history.renter_rating_id = renter_rating.rating_id

    db.session.commit()

    session.pop('history_id_for_rating')
    session.pop('renter_username_for_rating')

    flash("Thank you for your rating!")

    return redirect('/account-info')


@app.route('/confirm-delist-product/<int:prod_id>')
def confirm_delist_product(prod_id):
    """Confirm the user wants to delist product"""

    item = Product.query.get(prod_id)

    return render_template("confirm-delist-product.html", product=item)


@app.route('/handle-delist-product', methods=['POST'])
def delist_product():
    """Delist product"""

    prod_id = int(request.form.get("prod_id"))
    product = Product.query.get(prod_id)
    product.available = 0
    db.session.commit()

    # Change this to redirect to signedout honepage with flash message.
    # Can then delete finalized-deactivate-account route.
    flash("This product has been delisted.")

    return redirect('/account-info')


@app.route('/relist-product/<int:prod_id>')
def relist_product(prod_id):
    """Relist product"""

    # product = Product.query.get(prod_id)
    # product.available = 1
    # db.session.commit()

    return render_template("relist.html")


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
