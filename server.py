"""Happy Camper"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from sqlalchemy.orm.exc import NoResultFound

from model import connect_to_db, db
from model import User, Region, Product, Tent, SleepingBag, SleepingPad, BestUse
from model import Brand, History, Category, Rating, Gender, FillType, PadType
from helpers import make_user
from helpers import search_radius, get_users_in_area
from helpers import calc_default_dates, convert_string_to_datetime
from helpers import make_parent_product, make_tent, make_sleeping_bag, make_sleeping_pad
from helpers import update_parent_product, update_tent, update_sleeping_bag, update_sleeping_pad
from helpers import check_brand
from helpers import filter_products, categorize_products, get_products_within_dates
from helpers import calc_avg_star_rating
from datetime import datetime


app = Flask(__name__)

# Required to use Flask sessions alongd the debug toolbar
app.secret_key = "ABC"

# If you use an undefined variable in Jinja2, it will fails silently. Put this
# in to instead raise an error.
app.jinja_env.undefined = StrictUndefined


######################## User stuff ###################################
@app.route('/')
def index():
    """Signed out homepage."""

    return render_template("signedout.html")


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

    # http://docs.sqlalchemy.org/en/latest/orm/exceptions.html
    try:
        user = User.query.filter(User.email == username).one()
    except NoResultFound:
        flash("The email %s does not exist in our records. Please try again." % username)
        return redirect("/")

    if (user.active) and (user.password == password):
        session['user'] = username
        flash("Welcome! Logged in as %s" % username)
        return redirect('/success')
    else:
        flash("Login failed. Please try again.")
        return redirect('/')


@app.route('/create-account')
def create_account():
    """Where new users create an account"""

    return render_template("create-account.html")


@app.route('/handle-create-account', methods=['POST'])
def handle_createaccount():
    """Process create account form.

    Creates a User object using a helper function.

    """

    password = request.form.get('pword')
    confirm_pword = request.form.get('confirm_pword')

    if password != confirm_pword:
        flash("Passwords don't match. Try again.")
        return redirect('/create-account')
    else:
        user = make_user(password)

        db.session.add(user)
        db.session.commit()

        session['user'] = user.email
        flash("Successfully created account! Logged in as %s" % user.email)

        return redirect('/success')


@app.route('/success')
def enter_site():
    """Signed in home page."""

    customer = User.query.filter(User.email == session['user']).one()
    dates = calc_default_dates(7)

    categories = Category.query.all()
    brands = Brand.query.all()

    return render_template("success.html", user=customer,
                           today=dates['today_string'],
                           future=dates['future_string'],
                           product_categories=categories,
                           product_brands=brands)


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
    products_histories = set([])

    for product in products_all:
        if product.available:
            products_avail.append(product)
        else:
            products_out.append(product)

    rentals = History.query.filter(History.renter_user_id == customer.user_id).all()

    for product in products_all:
        if product.histories:
            products_histories.add(product)

    star_categories = {4: "4: Awesome! Would be happy to work with this person again.",
                       3: "3: It was fine. Wouldn't mind working with this person again.",
                       2: "2: Meh. MIGHT say hi I saw him or her on the street.",
                       1: "1: Awful. I hope I never interact with this person again.",
                      }

    star_values = sorted(star_categories.keys(), reverse=True)

    return render_template("account-info.html", user=customer, state=st,
                           all_products=products_all,
                           products_available=products_avail,
                           products_not_available=products_out,
                           products_with_histories=products_histories,
                           histories=rentals, today=today_date,
                           star_ratings=star_categories,
                           star_rating_values=star_values)


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


######################## Listing stuff ###################################
@app.route('/list-item-choices')
def list_item():
    """List an item page.

    Routes from signed in homepage, which has a button to List an Item.
    Routes to item detail page.
    """
    all_categories = Category.query.all()

    return render_template("list-item-choices.html", categories=all_categories)


@app.route('/list-product/<int:category_id>')
def list_product(category_id):
    # Also changed value of "add new brand" to -1. Per Drew rec.

    all_brands = Brand.query.all()
    dates = calc_default_dates(30)

    templates = {1: 'list-tent.html',
                 2: 'list-sleeping-bag.html',
                 3: 'list-sleeping-pad.html',
                 # 4: 'list-pack.html',
                 # 5: 'list-stove.html',
                 # 6: 'list-water-filter.html',
                 }

    # Tent
    if category_id == 1:
        all_best_uses = BestUse.query.all()
        season_categories = {2: "2-season",
                             3: "3-season",
                             4: "4-season",
                             5: "5-season"}

        return render_template(templates[category_id],
                               brands=all_brands,
                               submit_route='/handle-listing/%d' % category_id,
                               p_today=dates['today_string'],
                               p_month=dates['future_string'],
                               best_uses=all_best_uses,
                               seasons=season_categories)
    # Sleeping Bag
    elif category_id == 2:
        all_fill_types = FillType.query.all()
        all_gender_types = Gender.query.all()

        return render_template(templates[category_id],
                               brands=all_brands,
                               submit_route='/handle-listing/%d' % category_id,
                               p_today=dates['today_string'],
                               p_month=dates['future_string'],
                               fill_types=all_fill_types,
                               genders=all_gender_types)
     # Sleeping Pad
    elif category_id == 3:
        all_pad_types = PadType.query.all()
        all_best_uses = BestUse.query.all()

        return render_template(templates[category_id],
                               brands=all_brands,
                               submit_route='/handle-listing/%d' % category_id,
                               p_today=dates['today_string'],
                               p_month=dates['future_string'],
                               pad_types=all_pad_types,
                               best_uses=all_best_uses)
    else:
        return "not yet implemented"


@app.route('/handle-listing/<int:category_id>', methods=['POST'])
def handle_listing(category_id):
    """Handle rental listing.

    First checks if it needs to make a new Brand. If so, makes a new Brand object.
    Then makes parent Product object and then child category object.

    Need to pass it the same primary key of the parent
    Product object.
    """

    # Check if new brand. If so make new brand and add to database.
    brand_num = int(request.form.get("brand_id"))
    brand_num = check_brand(brand_num)

    parent_product = make_parent_product(brand_id=brand_num, category_id=category_id)

    db.session.add(parent_product)
    db.session.commit()

    if category_id == 1:
        child_product = make_tent(parent_product.prod_id)
    elif category_id == 2:
        child_product = make_sleeping_bag(parent_product.prod_id)
    elif category_id == 3:
        child_product = make_sleeping_pad(parent_product.prod_id)
    else:
        pass

    db.session.add(child_product)
    db.session.commit()

    flash("Listing successfully posted!")
    return redirect('/product-detail/%d' % parent_product.prod_id)


###################### Editing stuff ################################
@app.route('/edit-listing/<int:prod_id>')
def edit_listing(prod_id):

    categories = {1: Tent.query.get(prod_id),
                  2: SleepingBag.query.get(prod_id),
                  3: SleepingPad.query.get(prod_id),
                  # 4: Pack.query.get(prod_id),
                  # 5: Stove.query.get(prod_id),
                  # 6: WaterFilter.query.get(prod_id),
                  }

    templates = {1: 'edit-tent.html',
                 2: 'edit-sleeping-bag.html',
                 3: 'edit-sleeping-pad.html',
                 # 4: 'edit-pack.html',
                 # 5: 'edit-stove.html',
                 # 6: 'edit-water-filter.html',
                 }

    parent_product = Product.query.get(prod_id)
    category_id = parent_product.cat_id
    child_product = categories[category_id]

    all_brands = Brand.query.all()

    if category_id == 1:
        all_best_uses = BestUse.query.all()
        season_categories = {2: "2-season",
                             3: "3-season",
                             4: "4-season",
                             5: "5-season"}

        return render_template(templates[category_id], parent=parent_product,
                               child=child_product, brands=all_brands,
                               best_uses=all_best_uses, seasons=season_categories)
    elif category_id == 2:
        all_fill_types = FillType.query.all()
        all_genders = Gender.query.all()

        return render_template(templates[category_id], parent=parent_product,
                               child=child_product, brands=all_brands,
                               fill_types=all_fill_types, genders=all_genders)
    elif category_id == 3:
        all_pad_types = PadType.query.all()
        all_best_uses = BestUse.query.all()

        return render_template(templates[category_id], parent=parent_product,
                               child=child_product, brands=all_brands,
                               pad_types=all_pad_types, best_uses=all_best_uses)

    else:
        return "Yet to be implemented."


@app.route('/handle-edit-listing/<int:prod_id>', methods=['POST'])
def handle_edit_listing(prod_id):

    # categories = {1: Tent.query.get(prod_id),
    #               2: SleepingBag.query.get(prod_id),
    #               3: SleepingPad.query.get(prod_id),
    #               # 4: Pack.query.get(prod_id),
    #               # 5: Stove.query.get(prod_id),
    #               # 6: WaterFilter.query.get(prod_id),
    #               }

    # templates = {1: 'tent.html',
    #              2: 'sleeping-bag.html',
    #              3: 'sleeping-pad.html',
    #              # 4: 'pack.html',
    #              # 5: 'stove.html',
    #              # 6: 'water-filter.html',
    #              }

    parent_product = Product.query.get(prod_id)
    category_id = parent_product.cat_id
    # child_item = categories[category_id]

    brand_num = int(request.form.get("brand_id"))
    brand_num = check_brand(brand_num)

    update_parent_product(prod_id=prod_id, brand_id=brand_num)

    if category_id == 1:
        update_tent(prod_id)
        flash("Your tent listing has been updated!")
    elif category_id == 2:
        update_sleeping_bag(prod_id)
        flash("Your sleeping bag listing has been updated!")
    elif category_id == 3:
        update_sleeping_pad(prod_id)
        flash("Your sleeping pad listing has been updated!")
    else:
        return "This is unimplemented"

    return redirect("/account-info")


######################## Searching stuff ###################################
@app.route('/search-results')
def show_results():
    """Search results page.

    Routes from Signed in Home Page.
    Routes to Item Detail page.

    """

    try:
        search_miles = int(request.args.get("search_miles"))
    except ValueError:
        flash("Search radius must be an integer. Please try again.")
        return redirect('/success')

    try:
        search_start_date = convert_string_to_datetime(request.args.get("search_start_date"))
    except ValueError:
        flash("Search dates must be formatted YYYY-mm-dd. Please try again.")
        return redirect('/success')

    try:
        search_end_date = convert_string_to_datetime(request.args.get("search_end_date"))
    except ValueError:
        flash("Search dates must be formatted YYYY-mm-dd. Please try again.")
        return redirect('/success')

    search_area = request.args.get("search_area")
    category_id = int(request.args.get("category_id"))
    brand_id = int(request.args.get("brand_id"))

    days = (search_end_date - search_start_date).days + 1

    # Future version: save this search to table so default to last search next
    # time the user logs in.

    # Now put all this search info into the session so we can refer to it in
    # future pages.

    session['search_start_date'] = search_start_date
    session['search_end_date'] = search_end_date
    session['num_days'] = days
    session['search_area'] = search_area
    session['search_radius'] = search_miles
    session['search_category_id'] = category_id
    session['search_brand_id'] = brand_id

    # Find distinct postal codes in the database.
    query = db.session.query(User.postalcode).distinct()
    postalcodes = query.all()

    # Get zipcodes in the database that are within the search radius.
    postal_codes = search_radius(search_center=search_area,
                                 postalcodes=postalcodes, radius=search_miles)
    # Get users are in those zipcodes.
    users_in_area = get_users_in_area(postal_codes)

    # Get products those users have listed for rent and are currently available
    # within the search dates.
    available_products = get_products_within_dates(start_date=search_start_date,
                                                   end_date=search_end_date,
                                                   users=users_in_area)
    # Filter out products based on selected category and brand filters.
    filtered_products = filter_products(available_products, category_id=category_id,
                                        brand_id=brand_id)

    # Get categories of interest
    if category_id < 0:
        search_categories = Category.query.all()
    else:
        search_categories = [Category.query.get(category_id)]

    # Make a dictionary of available products with categories as the keys of the
    # dictionary).
    products_by_category = categorize_products(categories=search_categories,
                                               products=filtered_products)

    # Create a list of sorted category names to display categories on the page
    # in some kind of consisent order.
    sorted_category_names = sorted(products_by_category.keys())

    # For the saerch filter on top of the page, we need all categories and brands.
    all_categories = Category.query.all()
    all_brands = Brand.query.all()

    return render_template("search-results.html", location=search_area,
                           miles=search_miles,
                           search_categories=sorted_category_names,
                           products=products_by_category,
                           # Below are for for search filter,
                           product_categories=all_categories,
                           product_brands=all_brands)


######################## Showing stuff ###################################
@app.route('/product-detail/<int:prod_id>')
def show_product(prod_id):
    """Product detail page.

    Routes either from Search Results page or List Item page.
    If click on Borrow This, routes to Borrowed version of this page.
    """
    # Make a borrowed template version if available = False instead

    categories = {1: Tent.query.get(prod_id),
                  2: SleepingBag.query.get(prod_id),
                  3: SleepingPad.query.get(prod_id),
                  # 4: Pack.query.get(prod_id),
                  # 5: Stove.query.get(prod_id),
                  # 6: WaterFilter.query.get(prod_id),
                  }

    templates = {1: 'show-tent.html',
                 2: 'show-sleeping-bag.html',
                 3: 'show-sleeping-pad.html',
                 # 4: 'show-pack.html',
                 # 5: 'show-stove.html',
                 # 6: 'show-water-filter.html',
                 }

    parent_product = Product.query.get(prod_id)

    print "\n\nurl: %s\n\n" % parent_product.image_url
    category_id = parent_product.cat_id

    child_product = categories[category_id]
    print "Template: ", templates[category_id]

    try:
        search_start_date = session['search_start_date']
    except KeyError:
        search_start_date = 0

    return render_template(templates[category_id], product=parent_product,
                           item=child_product, have_searched=search_start_date)


######################## Renting stuff ###################################
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


######################## Rating stuff ###################################
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
        # Get error: AttributeError: type object 'History' has no attribute
        # 'owner_ratings'

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
        if history.product_rating:
            product_ratings.append(history.product_rating)

    avg_star_rating = calc_avg_star_rating(product_ratings)

    return render_template("show-product-ratings.html", ratings=product_ratings,
                           average=avg_star_rating, product=item)


@app.route('/rate-user-modal/<int:user_id>-<int:history_id>-<int:owner_is_true>')
def rate_user(user_id, history_id, owner_is_true):
    """Modal popup to rate owner or renter.

    """
    # owner_is_true used to determine if show rate owner or rate renter
    # forms. 0 is renter, 1 is owner
    star_categories = [{1: "1: Awful. Would not rent to this person again.",
                        2: "2: Worse than expected, but not awful. Might rent to this person again.",
                        3: "3: As expected. Would rent to this person again.",
                        4: "4: Awesome! Would be happy to rent to this person again."
                        },

                        {1: "1: Awful. Would not rent from this person again.",
                         2: "2: Not as good as expected, but might rent from again.",
                         3: "3: As expected. Would rent from again.",
                         4: "4: Awesome! Would rent from again.",
                         }]

    star_keys_reversed = sorted(star_categories[0].keys(), reverse=True)


    user_to_rate = User.query.get(user_id)

    print "\n\n User: %d \n\n" % user_id

    return render_template("rate-user-modal.html",
                           user=user_to_rate,
                           submit_route='/handle-user-rating',
                           star_ratings=star_categories[owner_is_true],
                           star_values=star_keys_reversed,
                           is_owner=owner_is_true,
                           hist_num=history_id)


@app.route('/handle-user-rating', methods=['POST'])
def handle_owner_rating():
    """Handle owner rating form submission.

    Will (1) create rating object and (2)update associated history object's
    owner_rating_id.
    """

    number_stars = int(request.form.get("num_stars"))
    comments_text = request.form.get("comments")
    is_owner = int(request.form.get("is_owner"))
    history_id = int(request.form.get("hist_id"))

    rating = Rating(stars=number_stars, comments=comments_text)

    db.session.add(rating)
    db.session.commit()

    history = History.query.get(history_id)

    print "\n\nhistory id is %d\n\n" % history.history_id

    if is_owner:
        history.owner_rating_id = rating.rating_id
        print "\n\nOwner rating: updating history id %d with rating id %d\n\n" % (
                                          history.history_id, rating.rating_id)
    else:
        history.renter_rating_id = rating.rating_id
        print "\n\nRenter rating: updating history id %d with rating id %d\n\n" % (
                                          history.history_id, rating.rating_id)

    db.session.commit()

    return "History id=%d, Rating id=%d" % (history_id, rating.rating_id)


@app.route('/rate-product-modal/<int:prod_id>-<int:history_id>')
def rate_product(prod_id, history_id):
    """Page to rate product.

    """
    star_rating_categories = {
                                1: '1: Awful. Would not rent again',
                                2: '2: Not as good as expected, but might rent again if in a pinch.',
                                3: '3: As expected. Would not mind renting again if needed.',
                                4: '4: Great! Even better than expected. Would be happy to rent again if needed.',
                              }

    item = Product.query.get(prod_id)
    star_keys_reversed = sorted(star_rating_categories.keys(), reverse=True)


    return render_template("rate-product-modal.html",
                           product=item,
                           star_ratings=star_rating_categories,
                           submit_route='/handle-product-rating',
                           star_values=star_keys_reversed,
                           hist_num=history_id)


@app.route('/handle-product-rating', methods=['POST'])
def handle_product_rating():
    """Handle product rating form submission.

    Will (1) create rating object and (2) update associated history object's
    prod_rating_id.
    """

    history_id = int(request.form.get("hist_id"))
    number_stars = int(request.form.get("num_stars"))
    comments_text = request.form.get("comments")

    product_rating = Rating(stars=number_stars, comments=comments_text)
    db.session.add(product_rating)
    db.session.commit()

    history = History.query.get(history_id)
    history.prod_rating_id = product_rating.rating_id

    db.session.commit()

    return "Product rating id=%d submitted for history_id=%d" % (
                                          product_rating.rating_id, history_id)


######################## Delisting stuff ###################################
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


######################################################################
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
