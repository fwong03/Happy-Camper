=============
Happy Camper
=============

The goal of Happy Camper is to be the Airbnb of gear. We want to
connect folks who want to rent gear with the those who have the gear and
want to rent it out. Cause gear is spensive.

This is a project for the fall 2015 cohort of coding camp Hackbright
Academy (session ends December 2015). 


Technology Stack
================
Application: Python, Flask, Jinja, SQLAlchemy, SQLite
APIs: Google Maps (for geolocation-python 0.2.0 library)


Main Features
================
 .. image:: /static/img/readme_list_or_search.jpg

You can currently list three types of gear: tents, sleeping bags, and sleeping pads.

To list items, click one of the three images at the top of signed-in home page.


.. image:: /static/img/readme_search_results.jpg

You can search for gear within a given search radius of a location and optionally filter by category and brand.

The form is pre-populated with the postal code entered when you created an account as the search center and 20 miles as the search radius.

Once on the search results, you can re-search using the form on top of the page.


.. image:: /static/img/readme_productdetail.jpg

To see product details, click on an image in the search results.


.. image:: /static/img/readme_ownerratings.jpg
.. image:: /static/img/readme_productratings.jpg

On the product detail page, you can click on links to see owner and product ratings.


.. image:: /static/img/readme_accountinfo.jpg

Your Account Info page (link is in the top right of the nav bar) is where you'll manage your inventory and check out your rental history.

The top table shows stuff you have listed and that are available (i.e., will show up in search results).


.. image:: /static/img/readme_second_and_third_tables.jpg

The second table shows products that you have listed and are no longer available, either because you delisted the item or it was recently rented out. These will not show up in search results. To make the product show up in search results again, click on the "Relist/Edit listing" link under Actions Available.


.. image:: /static/img/readme_raterenter.jpg

The third table shows all the histories of every product you have ever rented out, sorted in descending order by the rental request date. Here you can check out ratings of the renter. You can also rate your experience with the renter by clicking on the "Rate Renter".


.. image:: /static/img/readme_fourthtable.jpg

The fourth and last table on your Account Info page shows your history as a renter. Here you can rate your experience with owners and products.


.. image:: /static/img/readme_liststuff.jpg

Going back to listing stuff, if the brand of the item you want to list is not in the drop down, select "Add a new brand" and type in the new brand in the input box immediately below.


Database Structure
=================
.. image:: /static/img/HappyCamper_database_structure.jpg






   

