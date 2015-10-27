"""Happy Camper"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session 
from flask_debugtoolbar import DebugToolbarExtension

from model import Customer, Category, BestUse, Product, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return "This is the homepage"



@app.route('/login')
def user_list():
    """User login page."""

    return "This will be the user login page"


@app.route('/account')
def show_login():
    """User account overview page"""

    return "This will be the user account overview page"



@app.route('/handle-login', methods=['POST'])
def handle_login():
    """Process login form"""

    pass

    # username = request.form['username']
    # password = request.form['password']

    # user = User.query.filter_by(email = username).first()
    # if user:
    #     if user.password == password:
    #         session['user'] = username
    #         flash("Logged in as %s" % username)
    #         return redirect('user_info/%s' % user.user_id)
    #     else: 
    #         flash("Wrong password!")
    #         return redirect('/')

    # else:
    #     flash("Sorry, this username does not exist!")
    #     return redirect('/')

