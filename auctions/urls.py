from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from auctions.globals import (AJAX_DELETE_COMMENT, AJAX_DISMISS_NOTIFICATION,
                              AJAX_GENERATE_COMMENT, AJAX_GENERATE_USER,
                              AJAX_PURGE_MEDIA, AJAX_REPLY_COMMENT,
                              AJAX_UPLOAD_MEDIA, AJAX_WATCH_LISTING)

from . import ajax_controls, views


ajax_urls_include = [
    path(AJAX_DELETE_COMMENT, ajax_controls.ajax_delete_comment, name=AJAX_DELETE_COMMENT),
    path(AJAX_DISMISS_NOTIFICATION, ajax_controls.ajax_dismiss_notification, name=AJAX_DISMISS_NOTIFICATION),
    path(AJAX_GENERATE_COMMENT, ajax_controls.ajax_generate_comment, name=AJAX_GENERATE_COMMENT),
    path(AJAX_GENERATE_USER, ajax_controls.ajax_generate_user, name=AJAX_GENERATE_USER),
    path(AJAX_PURGE_MEDIA, ajax_controls.ajax_purge_media, name=AJAX_PURGE_MEDIA),
    path(AJAX_REPLY_COMMENT, ajax_controls.ajax_reply_comment, name=AJAX_REPLY_COMMENT),
    path(AJAX_UPLOAD_MEDIA, ajax_controls.ajax_upload_media, name=AJAX_UPLOAD_MEDIA),
    path(AJAX_WATCH_LISTING, ajax_controls.ajax_watch_listing, name=AJAX_WATCH_LISTING)
]


urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/<str:username>", views.view_user, name="view_user"),
    path("ajax/", include(ajax_urls_include)),
    path("bid", views.place_bid, name="place_bid"),
    path("cart", views.shopping_cart, name="shopping_cart"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category, name="category"),
    path("comment", views.comment, name="comment"),
    path("create", views.create_listing, name="create_listing"),
    path("create/<int:listing_id>", views.create_listing, name="create_listing"),
    path("delete/<int:listing_id>", views.delete_listing, name="delete_listing"),
    path("edit/<int:listing_id>", views.edit_listing, name="edit_listing"),
    path("listings/", views.listings, name="all_listings"),
    path("listings/view/<int:listing_id>", views.listing_page, name="view_listing"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path('preview/<int:id>', views.preview_listing, name="preview_listing"),
    path("register", views.register, name="register"),
    path("search", views.search, name="search"),
    path("settings", views.settings, name="settings"),
    path("submit/<int:id>", views.submit_listing, name="submit_listing"),
    path("watchlist", views.watchlist, name="watchlist")
    # for testing 
    # path("datetime/", views.datetime, name="datetime"),
    # path("mockup/", views.viewMockup, name="mockup"),
    # path("picsum/", views.picsum, name="picsum"),
    # path("ajax/", views.ajax_test, name="ajax_test"),
    # path("ajax/request/", views.ajax_return, name="ajax_return"),
    # path("bidding/", views.test_bidding, name="test_bidding"),
    # path("testListing/", views.test_listing, name="test_listing")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

