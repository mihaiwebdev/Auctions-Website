from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-listing", views.create_listing, name="create_listing"),
    path("watchlist", views.user_watchlist, name="watchlist"),
    path("categories/<str:category>", views.listing_categories, name="categories"),
    path("<int:listing_id>", views.listing_page, name="listing_page"),
    path("<int:listing_id>/added", views.add_to_watchlist, name="add_to_watchlist"),
    path("<int:listing_id>/removed", views.remove_from_watchlist,
         name="remove_from_watchlist"),
    path("<int:listing_id>/bid", views.bid, name="bid"),
    path("<int:listing_id>/closed", views.closed_auction, name="closed_auction"),
]
