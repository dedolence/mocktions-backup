from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from . import ajax_controls, views


ajax_urls_include = [
    path('build/image_thumbnail/', ajax_controls.ajax_build_image_thumbnail, name="ajax_build_image_thumbnail"),
    path('comment/delete/', ajax_controls.ajax_delete_comment, name='ajax_delete_comment'),
    path('notification/dismiss', ajax_controls.ajax_dismiss_notification, name='ajax_dismiss_notification'),
    path('comment/generate/', ajax_controls.ajax_generate_comment, name='ajax_generate_comment'),
    path('media/purge/', ajax_controls.ajax_purge_media, name='ajax_purge_media'),
    path('comment/reply/', ajax_controls.ajax_reply_comment, name='ajax_reply_comment'),
    path('media/upload/', ajax_controls.ajax_upload_media, name='ajax_upload_media'),
    path('listing/watch/', ajax_controls.ajax_watch_listing, name='ajax_watch_listing')
]


urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/", include('django.contrib.auth.urls')),
    path("accounts/profile/<str:username>/", views.view_user, name="view_user"),
    path("accounts/profile/", views.view_all_users, name="view_all_users"),
    path("ajax/", include(ajax_urls_include)),
    path("bid", views.place_bid, name="place_bid"),
    path("cart", views.shopping_cart, name="shopping_cart"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category, name="category"),
    path("comment", views.comment, name="comment"),
    path("create", views.create_listing, name="create_listing"),
    path("create/<int:listing_id>", views.create_listing, name="create_listing"),
    path("delete/<int:listing_id>", views.delete_listing, name="delete_listing"),
    path("listings/drafts", views.drafts, name="drafts"),
    path("edit/", views.edit_listing, name="edit_listing"),
    path("edit/<int:listing_id>", views.edit_listing, name="edit_listing"),
    path("listings/", views.listings, name="all_listings"),
    path("listings/view/<int:listing_id>", views.listing_page, name="view_listing"),
    #path("login", views.login_view, name="login"),
    #path("logout", views.logout_view, name="logout"),
    #path('preview/', views.preview_listing, name="preview_listing"), OBSOLETE
    path("register", views.register, name="register"),
    path("search", views.search, name="search"),
    path("settings", views.settings, name="settings"),
    path("submit/<int:listing_id>", views.submit_listing, name="submit_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    # for testing 
    # path("bootstrap/", views.test_view, name="test_view")
    # path("datetime/", views.datetime, name="datetime"),
    # path("mockup/", views.viewMockup, name="mockup"),
    # path("picsum/", views.picsum, name="picsum"),
    # path("ajax/", views.ajax_test, name="ajax_test"),
    # path("ajax/request/", views.ajax_return, name="ajax_return"),
    # path("bidding/", views.test_bidding, name="test_bidding"),
    # path("testListing/", views.test_listing, name="test_listing")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

