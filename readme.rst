=============
Happy Camper
=============

The goal of Happy Camper is to be the Airbnb of gear. We want to
connect folks who want to rent gear with those who have the gear and want to rent it out
to make some extra cash. Cause gear is spensive.

This is a project for the fall 2015 cohort of coding camp Hackbright
Academy. Our session ends mid-December 2015. 


Technology Stack
================
Application: Python, SQLite, Flask, Flask-SQLAlchemy, Jinja

APIs: GoogleMaps (geolocation-python 0.2.0)


Main Features
================
 .. image:: /static/img/readme_list_or_search.jpg

You can currently list three kinds of gear: tents, sleeping bags, and sleeping pads.

To list an item, click one of the three images at the top of the signed-in home page.

To search for gear, enter search criteria in the form below. You can search for gear within a given search radius of a location and optionally filter by category and brand.

The search form is pre-populated with a search radius of 20 miles and the search center set to the postal code you entered when you created your account.


.. image:: /static/img/readme_search_results.jpg

On the search results page, you can re-search using the form on top of the page.

To see product details, click on an image in the search results.


.. image:: /static/img/readme_productdetail.jpg

The product detail page shows specs for the item and rental cost info for the search criteria you entered.


.. image:: /static/img/readme_ownerratings.jpg
.. image:: /static/img/readme_productratings.jpg

You can click on links in the bottom left of the product detail page to see owner and product ratings.


.. image:: /static/img/readme_accountinfo.jpg

Your Account Info page is where you'll manage your inventory and check out your rental history. To access your account info, click on the "Your Account" link in the top right of the navigation bar.

The top table under "Manage Your Inventory" shows inventory you have listed and are available. These items will show up in search results.


.. image:: /static/img/readme_second_and_third_tables.jpg

The second table called "Stuff no longer available for rent" shows products you have listed in the past and are no longer available, either because you delisted them or they were recently rented out. These will not show up in search results. 

To make the product show up in search results again, click on the "Relist/Edit listing" link under Actions Available.


.. image:: /static/img/readme_renterrating.jpg

The third table, called "Stuff You've Rented Out", shows all the histories of every product you have ever rented out, sorted in descending order by the rental request submission date. 

Here you can check out ratings of renters.


.. image:: /static/img/readme_raterenter.jpg

You can also rate your experience with a renter by clicking on the "Rate Renter" button.


.. image:: /static/img/readme_fourthtable.jpg

The fourth and last table on your Account Info page shows your history as a renter. Here you can rate your experience with owners and products.


.. image:: /static/img/readme_liststuff.jpg

Going back to listing stuff, if the brand of the item you want to list is not in the drop-down menu, select "Add a new brand" and type in the new brand name in the input box immediately below.


