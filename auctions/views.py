import decimal
from io import BytesIO, StringIO
import random
from datetime import timedelta
from math import floor
import tempfile
import uuid

import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.core import files
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import \
    csrf_exempt
from PIL import Image

from . import namelist, wordlist
from .ajax_controls import *
from .forms import ContactForm, NewImageForm, NewListingForm, RegistrationForm, ShippingInformation
from .globals import *
from .models import Bid, Category, Comment, TempListing, UserImage, Listing, Notification, User
from .notifications import *
from .strings import *

# for testing
# from .testing import *


# //////////////////////////////////////////////////////
# URL PATH VIEWS
#   -ajax
#   -category
#   -categories
#   -comment
#   -create_listing
#   -delete_listing
#   -edit_listing
#   -index
#   -listing_page
#   -listings
#   -login
#   -logout_view
#   -place_bid
#   -register
#   -search
#   -shopping_cart
#   -view_all_users
#   -view_user
# //////////////////////////////////////////////////////


@csrf_exempt
def ajax(request, action, id=None):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse("index"))
    else:
        response = {}
        if not request.user.is_authenticated and not action == 'generate_random_user':
            response["message"] = MESSAGE_GENERIC_LOGIN_REQUIRED 
            response["button_text"] = MESSAGE_WATCHLIST_PROMPT
            response["undo"] = True
        else:
            if action == "upload_image":
                response = ajax_upload_images(request, response)
            elif action == 'watch_listing':
                response = ajax_watch_listing(request, response)
            elif action == 'dismiss':
                response = ajax_dismiss_notification(request, response)
            elif action == 'generate_comment':
                response = ajax_generate_comment(request, response)
            elif action == 'delete_comment':
                response = ajax_delete_comment(request, response)
            elif action == 'reply_comment':
                response = ajax_reply_comment(request, response)
            elif action == 'generate_random_user':
                response = ajax_generate_user(request, response)
            elif action == 'purge_image':
                response = ajax_purge_media(request, response)
        return JsonResponse(response, safe=False)


def category(request, category_id):
    category_title = Category.objects.get(id=category_id)
    category_listings_raw = Listing.objects.filter(category_id=category_id)
    page_tuple = get_page(request, category_listings_raw)
    return render(request, "auctions/category.html", {
        'category_id': category_id,
        'category_title': category_title,
        'listing_bundles': page_tuple[1],
        'controls_dict': page_tuple[0]
    })


def categories(request):
    return render(request, "auctions/categories.html", {
        'categories': Category.objects.all()
    })


def comment(request):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse("index"))
    else:
        # need to perform some kinda validation on the input here
        content = request.POST["content"]
        listing = Listing.objects.get(pk=request.POST["listing_id"])
        user = request.user
        
        # this will only be set if creating a new reply to another comment
        original_comment_id = request.POST.get("original_comment_id", None)
        if original_comment_id:
            replyTo = Comment.objects.get(pk=original_comment_id)
            content = request.POST["reply_content"]
        else:
            replyTo = None

        # this will only be set if editing an existing comment
        comment_id = request.POST.get("comment_id", None)
        if comment_id:
            comment = Comment.objects.get(pk=comment_id)
            comment.content = content
            comment.save()
        else:
            Comment.objects.create(
                content=content,
                listing=listing,
                user=user,
                replyTo=replyTo
            )
        
        return HttpResponseRedirect(
            reverse("view_listing", args=[request.POST["listing_id"]])
            )


@login_required
def create_listing(request, listing_id=None):
    if request.method == "GET":
        temp = TempListing.objects.create(owner=request.user)
        form = NewListingForm(instance=temp)
        form_mode = 'create_new'
    else:
        # accessing a draft
        temp = TempListing.objects.get(pk=listing_id)
        if temp.owner != request.user:
            # no editing other people's drafts!
            notification = NotificationTemplate()
            notification.build(
                request.user,
                TYPE_INFO,
                ICON_GENERIC,
                MESSAGE_LISTING_CREATION_INVALID_USER,
                True
            )
            return HttpResponseRedirect(reverse('index'))
        else:
            form = NewListingForm(request.POST, instance=temp)
            form_mode = 'preview'
    return render(request, 'auctions/createListing.html', {
        'form': form,
        'listing_id': temp.id,
        'form_mode': form_mode
    })




@login_required
def delete_listing(request, listing_id):
    listing_bundle = get_listing(request, id=listing_id)
    notification = NotificationTemplate()
    notification.build(
        request.user,
        TYPE_DANGER,
        ICON_DANGER,
        MESSAGE_USER_DELETE_PROHIBITED,
        True
    )
    if request.user != listing_bundle["listing"].owner:
        notification.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        if request.method == "GET":
            return render(request, 'auctions/deleteListing.html', {
                'listing_bundle': listing_bundle
            })
        else:
            listing = Listing.objects.get(pk=listing_id)
            listing.delete()
            notification.set_type = TYPE_INFO
            notification.set_message(
                ICON_GENERIC,
                MESSAGE_USER_LISTING_DELETED.format(listing.title)
            )
            notification.save()
            return HttpResponseRedirect(reverse("index"))


@login_required
def edit_listing(request, listing_id):
    raw_listing = Listing.objects.get(id=listing_id)
    listing_bundle = get_listing(request, None, raw_listing)
    notification = NotificationTemplate()
    notification.build(
        request.user,
        TYPE_DANGER,
        ICON_DANGER,
        '',
        True,
        reverse('index')
    )
    if request.user != raw_listing.owner:
        notification.set_message(
            ICON_DANGER, 
            MESSAGE_LISTING_EDIT_PROHIBITED.format(raw_listing.title)
            )
        notification.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        # When first accessed, must check to make sure editing is allowed.
        if request.method == "GET":
            highest_bid = get_highest_bid(raw_listing)
            if (
                (highest_bid and 
                highest_bid.amount != raw_listing.starting_bid)
            ):
                notification.set_message(
                    ICON_DANGER, 
                    MESSAGE_LISTING_EDIT_PROHIBITED.format(raw_listing.title)
                    )
                notification.set_page(reverse('view_listing', args=[listing_id]))
                notification.save()
                return HttpResponseRedirect(
                    reverse("view_listing", args=[listing_id])
                    )
            
            else:
                edit_form = NewListingForm(instance=raw_listing)
                listing_bundle = get_listing(request, None, raw_listing)
                return render(request, 'auctions/editListing.html', {
                    'listing_bundle': listing_bundle,
                    'edit_listing_form': edit_form
                })
        
        else:
            edited_form = NewListingForm(request.POST, instance=raw_listing)
            if not edited_form.is_valid():
                return render(request, "auctions/editListing.html", {
                    'listing_bundle': listing_bundle,
                    'edit_listing_form': edited_form
                })
            
            else:
                edited_form.save()
                notification.build(
                    request.user,
                    TYPE_SUCCESS,
                    ICON_SUCCESS,
                    MESSAGE_LISTING_EDIT_SUCCESSFUL.format(raw_listing.title),
                    True,
                    reverse('view_listing', args=[listing_id]))
                notification.save()
                return HttpResponseRedirect(
                    reverse("view_listing", args=[raw_listing.id]))


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    else:
        # purge listings that have expired
        purge_listings(request)
        notifications = get_notifications(request.user, reverse('index'))
        active_listings_raw = Listing.objects.filter(owner=request.user)
        listing_page_tuple = get_page(request, active_listings_raw)
        return render(request, "auctions/index.html", {
            'listing_controls': listing_page_tuple[0],
            'listing_bundles': listing_page_tuple[1],
            'notifications': notifications
        })


def listing_page(request, listing_id):
    notifications = get_notifications(
        request.user, 
        reverse('view_listing', args=[listing_id])
    )
    listing_bundle = get_listing(request, listing_id)
    comments = listing_bundle["listing"].listings_comments.all().order_by('-timestamp')
    return render(request, "auctions/viewListing.html", {
        'listing_bundle': listing_bundle,
        'comments': comments,
        'notifications': notifications
    })


@csrf_exempt
def listings(request):
    all_listings = Listing.objects.all()
    page_tuple = get_page(request, all_listings)
    return render(request, "auctions/listings.html", {
        'controls_dict': page_tuple[0],
        'listing_bundles': page_tuple[1]
    })


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # page to redirect to
        if 'next' in request.POST:
            next = request.POST['next']
        else:
            next = reverse('index')

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(next)
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html", {
            'message': MESSAGE_SPLASH_WELCOME
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required
def place_bid(request):
    notification = NotificationTemplate()
    notification.build(
                    request.user,
                    TYPE_WARNING,
                    ICON_WARNING,
                    MESSAGE_LISTING_EXPIRED,
                    True
                )
    if request.method == "GET":
        return HttpResponseRedirect(reverse("index"))
    else:
        listing_id = request.POST["listing-id"]
        notification.set_page(reverse('view_listing', args=[listing_id]))
        listing_bundle = get_listing(request, listing_id)
        if listing_bundle['expiration_bundle']['expired'] == True:
            notification.save()
        else:
            bid = request.POST["bid"]
            if not bid.isdigit():
                notification.set_message(ICON_WARNING, MESSAGE_LISTING_BID_FORMATTING)
                notification.save()
            elif int(bid) > 99999:
                notification.set_message(ICON_WARNING,MESSAGE_LISTING_BID_TOO_HIGH)
                notification.save()
            elif int(bid) <= listing_bundle["listing"].current_bid:
                notification.set_message(ICON_WARNING,MESSAGE_LISTING_BID_TOO_LOW)
                notification.save()
            else:
                new_bid = Bid.objects.create(
                    amount=decimal.Decimal(bid), 
                    user=request.user, 
                    listing=listing_bundle["listing"])
                new_bid.save()
                listing_bundle = get_listing(request, listing_id)
                notification.build(
                    request.user,
                    TYPE_SUCCESS,
                    ICON_SUCCESS,
                    MESSAGE_LISTING_BID_SUCCESSFUL,
                    True,
                    reverse('view_listing', args=[listing_id])
                )
                notification.save()
                
        return HttpResponseRedirect(
            reverse("view_listing", args=[listing_id]))


@login_required
def preview_listing(request, id):
    """ID refers to the temporary listing. Validate the form
    information and reroute either to this view again, or to
    submit_listing.

    This should also be the route taken for editing an existing
    listing, I suppose.
    """
    temp_listing = TempListing.objects.get(pk=id)
    if request.user != temp_listing.owner:
        notification = NotificationTemplate()
        notification.build(request.user,
        TYPE_INFO,
        ICON_WARNING,
        MESSAGE_LISTING_CREATION_INVALID_USER,
        True)
        return HttpResponseRedirect(reverse('index'))
    else:
        form = NewListingForm(instance=temp_listing)



def register(request):
    notification = NotificationTemplate()
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirm_password"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": MESSAGE_REG_PASSWORD_MISMATCH
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)

            # apply any other biographical details
            for k, v in request.POST.items():
                setattr(user, k, v)
            
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": MESSAGE_REG_USERNAME_TAKEN
            })
        login(request, user)
        notification.build(
            user,
            TYPE_SUCCESS,
            ICON_SUCCESS,
            MESSAGE_REG_SUCCESS,
            False,
            reverse('index')
        )
        notification.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        cred_form = RegistrationForm()
        bio_form = ContactForm()
        ship_form = ShippingInformation()
        return render(request, "auctions/register.html", {
            'cred_form': cred_form,
            'bio_form': bio_form,
            'ship_form': ship_form
        })


def search(request):
    page = {}
    query = request.GET.get("search_query", '')
    if query is not None:
        res_titles = Listing.objects.filter(title__icontains=query)
        res_descr = Listing.objects.filter(description__icontains=query)
        full_res = res_titles.union(res_descr)
        # cannot immediately call get_page because it uses a filter and 
        # that is "not supported" after usion union() >__<
        # so what follows is some obnoxious gymnastics to make this work.
        # i do not like this.
        ids = [listing.id for listing in full_res]
        raw_listings = Listing.objects.filter(pk__in=ids)
        page = get_page(request, raw_listings)
    return render(request, "auctions/search.html", {
        'controls_dict': page[0],
        'listing_bundles': page[1],
        'search_query': query
    })
    

def settings(request):
    if not request.user.is_authenticated:
        return render(request, reverse("index"))
    else:
        profile_picture_form = NewImageForm()
        contact_form = ContactForm({
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': request.user.phone
        })
        shipping_form = ShippingInformation({
            'street': request.user.street,
            'city': request.user.city,
            'state': request.user.state,
            'postcode': request.user.postcode,
            'country': request.user.country
        })
        
        # create a generic notification
        notification = NotificationTemplate()

        if request.method == "POST":
            # instantiate forms
            profile_picture_form = NewImageForm(request.POST, request.FILES)
            contact_form = ContactForm(request.POST)
            shipping_form = ShippingInformation(request.POST)

            # see what, if anything, has changed.
            img_upload = request.FILES.get('image', None)
            img_url = request.POST.get('image_url', None)
            random_img = request.POST.get('random_image', None)
            first_name = request.POST.get('first_name', None)
            last_name = request.POST.get('last_name', None)
            email = request.POST.get('email', None)
            phone = request.POST.get('phone', None)
            street = request.POST.get('street', None)
            city = request.POST.get('city', None)
            state = request.POST.get('state', None)
            postcode = request.POST.get('postcode', None)
            country = request.POST.get('country', None)

            # validate form data
            if not contact_form.is_valid() or not shipping_form.is_valid():
                return render(request, "auctions/settings.html", {
                        'profile_picture_form': profile_picture_form,
                        'contact_form': contact_form,
                        'shipping_form': shipping_form,
                        'notifications': get_notifications(
                            request.user, 
                            reverse('settings')
                            )
                    })

            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone = phone
            user.street = street
            user.city = city
            user.state = state
            user.postcode = postcode
            user.country = country
            user.save()
            
            # check for profile image
            if img_upload or img_url or random_img:

                if profile_picture_form.is_valid():
                    
                    if img_upload:
                        img_source = img_upload
                    else:
                        if img_url:
                            src_url = img_url
                            filename = img_url.split('/')[-1].split('.')[0] + ".jpg"
                        else:
                            src_url = 'https://picsum.photos/200'
                            filename = uuid.uuid4().hex     # random filename
                        
                        res = requests.get(src_url, stream=True)

                        # make sure it's an image
                        content_types = 'image/gif', 'image/jpeg', 'image/png', 'image/tiff'
                        if res.headers['content-type'] not in content_types:
                            notification.build(
                                request.user,
                                TYPE_WARNING,
                                ICON_WARNING,
                                MESSAGE_USER_PICTURE_UPLOAD_FORMAT,
                                True,
                                reverse('settings')
                            )
                            notification.save()
                            return HttpResponseRedirect(reverse('settings'))
                        
                        # source for saving image to temp file:
                        # Mayank Jain https://medium.com/@jainmickey
                        img_temp = tempfile.NamedTemporaryFile(delete=True)
                        for block in res.iter_content(1024 * 8):
                            if not block:
                                break
                            img_temp.write(block)
                        img_source = files.images.ImageFile(
                            img_temp, 
                            name=filename
                            )

                    img_mod = UserImage(
                        owner=request.user,
                        image=img_source
                    )
                    img_mod.save_thumbnail()
                    img_mod.save()

                    # replace the user's profile picture
                    request.user.profile_picture = img_mod.thumbnail.url
                    request.user.save()

                    notification.build(
                        request.user,
                        TYPE_SUCCESS,
                        ICON_SUCCESS,
                        MESSAGE_USER_PICTURE_UPLOAD_SUCCESS,
                        True,
                        reverse('settings')
                    )
                    notification.save()

                    return render(request, "auctions/settings.html", {
                        'profile_picture_form': profile_picture_form,
                        'contact_form': contact_form,
                        'shipping_form': shipping_form,
                        'img': img_mod.thumbnail.url,
                        'notifications': get_notifications(
                            request.user, 
                            reverse('settings')
                            )
                    })
                else:
                    notification.build(
                        request.user,
                        TYPE_WARNING,
                        ICON_WARNING,
                        MESSAGE_USER_PICTURE_UPLOAD_FAILURE,
                        True,
                        reverse('settings')
                    )
                    notification.save()
                    return render(request, "auctions/settings.html", {
                        'profile_picture_form': profile_picture_form,
                        'contact_form': contact_form,
                        'shipping_form': shipping_form,
                        'notifications': get_notifications(
                            request.user, 
                            reverse('settings')
                            )
                    })
            # no changes were made
            else:
                return render(request, "auctions/settings.html", {
                    'profile_picture_form': profile_picture_form,
                    'contact_form': contact_form,
                    'shipping_form': shipping_form,
                    'notifications': get_notifications(
                        request.user, reverse('settings')
                        )
                })

        # request = GET
        else:
            return render(request, "auctions/settings.html", {
                'profile_picture_form': profile_picture_form,
                'contact_form': contact_form,
                'shipping_form': shipping_form,
                'notifications': get_notifications(
                    request.user, reverse('settings')
                    )
            })



def shopping_cart(request):
    return HttpResponseRedirect(reverse('index'))


def submit_listing(id):
    """ID refers to the temporary ID used for drafting a new listing.
    Validate the listing and copy to a new Listing model object, then
    delete the temporary listing.
    """
    pass


def view_all_users(request):
    return HttpResponseRedirect(reverse('index'))


def view_user(request, username):
    user = User.objects.get(username=username)
    raw_listings = Listing.objects.filter(owner=user)
    listings = [get_listing(listing) for listing in raw_listings]
    return render(request, "auctions/user.html", {
        "listings": listings,
        'user': user
    })

def watchlist(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    else:
        # purge listings that have expired
        purge_listings(request)
        notifications = get_notifications(request.user, 'index')
        active_listings_raw = request.user.watchlist.all()
        listing_page_tuple = get_page(request, active_listings_raw)
        return render(request, "auctions/watchlist.html", {
            'listing_controls': listing_page_tuple[0],
            'listing_bundles': listing_page_tuple[1],
            'notifications': notifications
        })


# //////////////////////////////////////////////////////
# UTILITY VIEW FUNCTIONS
# //////////////////////////////////////////////////////





def purge_listings(request):
    """Since this isn't being run on a real server that can purge things in real time,
    instead, every time index.html is loaded, flag any listings that are no longer active.
    """
    all_listings = Listing.objects.all()
    watchlist = request.user.watchlist.all()

    for listing in all_listings:
        expiration = check_expiration(listing)
        if expiration["expired"] and listing.active:
            listing.active = False
            highest_bid = get_highest_bid(listing)
            if highest_bid:
                listing.winning_bid = highest_bid.amount
                listing.winner = highest_bid.user
                notify_winner(highest_bid.user, listing)
            if listing in watchlist:
                obj = request.user.watchlist.get(id=listing.id)
                obj.delete()
            listing.save()


def get_highest_bid(listing) -> Bid:
    bids = Bid.objects.filter(listing=listing).order_by('-amount')
    return bids.first()


def get_listing(request, id=None, listing=None) -> dict:
    if not listing:
        listing = Listing.objects.get(pk=id)

    highest_bid = get_highest_bid(listing)
    listing.current_bid = highest_bid.amount if highest_bid else listing.starting_bid
    owner_controls = True if listing.owner == request.user else False
    watch_options = True if owner_controls == False else True
    watchlist = request.user.watchlist.all()
    watching_currently = True if listing in watchlist else False
    expiration_bundle = check_expiration(listing)
    return {
        'listing': listing,
        'owner_controls': owner_controls,
        'watch_options': watch_options,
        'watching_currently': watching_currently,
        'expiration_bundle': expiration_bundle
    }


def check_expiration(listing) -> dict:
    """Make sure the listing is still active according to its creation timestamp.
    Irrelevant, but for my own notes:
    Due to the db being sqlite, the timestamp is a naive date; i.e. it does not carry with it any timezone information.
    By default Django creates objects using UTC time format.
    LOCAL_TIMEZONE stores the timezone as a string in ISO format, to be used for converting UTC timestamps to local user timezones.
    """
    expiration_date = listing.timestamp + timedelta(days=listing.lifespan)
    today = timezone.now()
    difference = (expiration_date - today)      # e.g. 13 days, 22:18:29.642879.
    s = difference.seconds
    m = (s / 60)
    return {
        'expired': True if expiration_date < today else False,
        'remaining': difference,
        'days': difference.days,
        'hours': floor(m / 60),
        'minutes': floor((s / 60) % 60),
        'seconds': floor(s % 60)
    }


def fetch_image(request, url=None, page=None, listing=None):
    """ Can be called with or without the url parameter. When no url
    is provided, a random image will be returned.
    """
    notification = NotificationTemplate()
    if url:
        src_url = url
        filename = url.split('/')[-1].split('.')[0] + ".jpg"
        #TODO: probably need more URL validation here
    else:
        src_url = 'https://picsum.photos/200'
        filename = uuid.uuid4().hex + ".jpg"     # random filename
    
    res = requests.get(src_url, stream=True)
    # make sure it's an image
    content_types = 'image/gif', 'image/jpeg', 'image/png', 'image/tiff'
    if res.headers['content-type'] not in content_types:
        notification.build(
            request.user,
            TYPE_WARNING,
            ICON_WARNING,
            MESSAGE_USER_PICTURE_UPLOAD_FORMAT,
            True,
            page
        )
        notification.save()
        if not page:
            page = reverse('index')
        return HttpResponseRedirect(page)   
    # source for saving image to temp file:
    # Mayank Jain https://medium.com/@jainmickey
    img_temp = tempfile.NamedTemporaryFile(delete=True)
    for block in res.iter_content(1024 * 8):
        if not block:
            break
        img_temp.write(block)
    img_source = files.images.ImageFile(
        img_temp, 
        name=filename
        )
    img_mod = UserImage(
        owner=request.user,
        image=img_source
    )
    if listing and listing.__class__ == Listing:
        img_mod.listing = listing
    elif listing and listing.__class__ == TempListing:
        img_mod.temp_listing = listing
    img_mod.save_thumbnail()
    img_mod.save()
    return [img_mod]


def get_page(request, raw_listings) -> tuple:
    """Generate a dict containing all the information needed for the template
    to properly paginate the listings.
    """
    controls_dict = {
        'per_page': int(request.GET.get('perPage', 10)),
        'current_page': int(request.GET.get('page', 1)),
        'previous_page': 0,
        'next_page': 0,
        'next_next_page': 0,
        'last_page': 0,
        'order_by': request.GET.get('orderBy', 'newest'),
        'show_expired': request.GET.get('showExpired', False) == "True",
        'categories': [category for category in Category.objects.all()],
        'selected_category': int(request.GET.get('selected_category', 0))
    }

    if controls_dict['selected_category'] != 0:
        categorized_listings = raw_listings.filter(category_id=controls_dict['selected_category'])
    else:
        categorized_listings = raw_listings

    ordered_listings = order_listings(categorized_listings, controls_dict['order_by'])

    if not controls_dict['show_expired']:
        ordered_listings = ordered_listings.filter(active=True)

    pager = Paginator(ordered_listings, controls_dict['per_page'])
    current_page = pager.page(controls_dict['current_page'])
    if current_page.has_previous():
        controls_dict['previous_page'] = current_page.previous_page_number()
    else:
        controls_dict['previous_page'] = 0

    if current_page.has_next():
        controls_dict['next_page'] = current_page.next_page_number()
    else:
        controls_dict['next_page'] = 0

    controls_dict['next_next_page'] = controls_dict['current_page'] + 2
    controls_dict['last_page'] = pager.num_pages

    formatted_listings = [
        get_listing(request, id=None, listing=listing) 
        for listing in current_page.object_list
        ]

    return (controls_dict, formatted_listings)


def order_listings(listings, spec) -> QuerySet:
    order = ''

    if spec == 'newest':
        order = '-timestamp'
    elif spec == 'oldest':
        order = 'timestamp'
    elif spec == 'atoz':
        order = 'title'
    elif spec == 'ztoa':
        order = '-title'
    elif spec == 'priceUp':
        order = 'current_bid'
    elif spec == 'priceDown':
        order = '-current_bid'
        
    return listings.order_by(order)


def upload_images(request, files, listing=None):    
    uploaded_images = []
    for f in files:
        img_mod = UserImage(
            owner=request.user,
            image=f
        )
        if listing and listing.__class__ == Listing:
            img_mod.listing = listing
        elif listing and listing.__class__ == TempListing:
            img_mod.temp_listing = listing
        img_mod.save_thumbnail()
        img_mod.save()
        uploaded_images.append(img_mod)
    return uploaded_images


# //////////////////////////////////////////////////////
# RANDOM OBJECT GENERATION
# //////////////////////////////////////////////////////


def generate_listing(amount, request):
    listings = []
    for i in range(amount):
        listing = {
            'title': generateTitle(),
            'image_url': fetch_image(request),
            'description': generateDescription()[0:500],
            'starting_bid': random.randint(1,9999),
            'shipping': random.randint(5, 50),
            'category': random.randint(1, 8),
            'lifespan': random.randint(1, 5)
        }
        listings.append(listing)
    
    return listings if (amount>1) else listings[0]


def generateTitle():
    adj = random.choice(wordlist.adjectives)
    noun = random.choice(wordlist.nouns)
    return f"{adj.capitalize()} {noun}"


def generateImage():
    # sorta inefficient because the api loads a random image but only looks at the response headers for the id to generate a static URL,
    # so the image is ultimately served twice, first here and again when its absolute URL is called :(
    # but since this is only for testing purposes really it doesn't matter so much, and it's only 200px square images
    image_api = requests.get('https://picsum.photos/200')
    image_id = image_api.headers['picsum-id']
    return f'https://picsum.photos/id/{image_id}/200'


def generateDescription():
    return GEN.paragraph()


def picsum(request):
    image_api = requests.get('https://picsum.photos/200')
    image_id = image_api.headers['picsum-id']
    image_url = f'https://picsum.photos/id/{image_id}/200'
    return render(request, 'auctions/tests/picsum.html', {
        'url': image_url
    })

def generateName():
    firstname = random.choice(namelist.firstnames)
    lastname = random.choice(namelist.lastnames)
    return (firstname, lastname)