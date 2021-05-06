from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("categories", views.categories, name="categories"),
    path("listing_by_category/<str:category>", views.listing_by_category, name="listing_by_category"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing_page/<int:listing_id>", views.listing_page, name="listing_page"),
    path("create_bid_comment_watchlist/<int:listing_id>", views.create_bid_comment_watchlist, name="create_bid_comment_watchlist"),
    path("closed_listing", views.closed_listing, name="closed_listing"),
    path("closed_listing_page/<int:listing_id>", views.closed_listing_page, name="closed_listing_page"),
]
