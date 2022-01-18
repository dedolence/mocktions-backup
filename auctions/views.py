import decimal
from io import BytesIO, StringIO
import random
from datetime import timedelta
from math import floor
import tempfile

import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.core import serializers, files
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import \
    csrf_exempt  # to make the watchlist AJAX request work, which doesn't use a CSRF token
from PIL import Image
from . import wordlist
from .forms import NewImageForm, NewListingForm
from .globals import *
from .models import Bid, Category, Comment, User_Image, Listing, Notification, User
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
        if not request.user.is_authenticated:
            response["message"] = "You must be logged in to do that." 
            response["button_text"] = "Add to Watchlist", 
            response["undo"] = True
        else:
            if action == 'watch_listing':
                listing = Listing.objects.get(id=id)
                watchlist = request.user.watchlist
                if listing in watchlist.all():
                    watchlist.remove(listing)
                    response["message"] = "Removed from watchlist."
                    response["button_text"] = "Add to Watchlist"
                else:
                    watchlist.add(listing)
                    response["message"] = "Added to watchlist."
                    response["button_text"] = "Watching"
            
            elif action == 'dismiss':
                try:
                    notification = Notification.objects.get(pk=id)
                    notification.delete()
                except ObjectDoesNotExist:
                    pass
            
            elif action == 'generate_comment':
                message = ''
                for i in range(0, random.randint(1,5)):
                    message += GEN.sentence()
                response["message"] = message

            elif action == 'delete_comment':
                comment = Comment.objects.get(pk=id)
                comment.delete()
                response["message"] = "Comment deleted."

            elif action == 'reply_comment':
                # Filter must be used instead of get to return iterable for serializer
                # (or wrap the queryset in [] to list-ify it).
                comment = Comment.objects.filter(pk=id)
                response["comment"] = serializers.serialize("json", comment)
                response["author"] = comment.first().user.username
        
        return JsonResponse(response)


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
def create_listing(request):
    # if GET, display new listing form
    if request.method == "GET":
        new_listing_form = NewListingForm()
        # categories = Category.objects.all()
        return render(request, "auctions/createListing.html", {
            # 'categories': categories
            'form': new_listing_form
        })

    # TODO: move this to the views.preview_listing() method     
    # else if POST, preview listing for changes or add to DB
    elif request.method == "POST":

        # check if we need to generate a random listing:
        if 'random' in request.POST:
            form = NewListingForm(generateListing(1))
        else:
            # create form instance
            form = NewListingForm(request.POST)
        
        # validate form
        if not form.is_valid():
            # errors were found so return the form to the initial listing form page
            return render(request, "auctions/createListing.html", {
                'form': form
            })       
        else:
            # create an instance of the object
            instance = form.save(commit=False)
            # attach user to the form instance
            instance.owner = request.user
            instance.current_bid = instance.starting_bid
            # check to see if we need to preview or submit
            if 'submit' in request.POST:
                # add to DB
                instance.save()
                # include many-to-many relationships
                form.save_m2m()
                return HttpResponseRedirect(reverse('view_listing', args=[instance.id]))
            else:
                return render(request, 'auctions/previewListing.html', {
                    'listing': instance,
                    'form': form,
                    'form_controls': False
                })


@login_required
def delete_listing(request, listing_id):
    listing_bundle = get_listing(request, id=listing_id)
    if request.user != listing_bundle["listing"].owner:
        notification = build_notification(
            request.user, 
            TYPE_DANGER, 
            ICON_DANGER, 
            MESSAGE_LISTING_DELETE_PROHIBITED,
            True)
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
            notification = build_notification(
                request.user,
                TYPE_INFO,
                ICON_GENERIC,
                MESSAGE_USER_LISTING_DELETED.format(listing.title),
                True
            )
            notification.save()
            return HttpResponseRedirect(reverse("index"))


@login_required
def edit_listing(request, listing_id):
    raw_listing = Listing.objects.get(id=listing_id)
    listing_bundle = get_listing(request, None, raw_listing)
    if request.user != raw_listing.owner:
        message = MESSAGE_USER_LISTING_EDIT_PROHIBITED.format(raw_listing.title)
        notification = build_notification(
            request.user, 
            TYPE_DANGER, 
            ICON_DANGER, 
            message, 
            True)
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
                notification = build_notification(
                    request.user, 
                    TYPE_DANGER, 
                    ICON_DANGER, 
                    MESSAGE_USER_LISTING_EDIT_PROHIBITED.format(raw_listing.title),
                    True,
                    'listing_page')
                notification.save()
                return HttpResponseRedirect(
                    reverse("listing_page", args=[listing_id])
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
                notification = build_notification(
                    request.user,
                    TYPE_SUCCESS,
                    ICON_SUCCESS,
                    MESSAGE_LISTING_EDIT_SUCCESSFUL,
                    True,
                    'listing_page')
                notification.save()
                return HttpResponseRedirect(
                    reverse("view_listing", rgs=[raw_listing.id]))


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    else:
        # purge listings that have expired
        purge_listings(request)
        notifications = get_notifications(request.user, 'index')
        active_listings_raw = Listing.objects.filter(owner=request.user)
        listing_page_tuple = get_page(request, active_listings_raw)
        return render(request, "auctions/index.html", {
            'listing_controls': listing_page_tuple[0],
            'listing_bundles': listing_page_tuple[1],
            'notifications': notifications
        })


def listing_page(request, listing_id):
    notifications = get_notifications(request.user, 'listing_page')
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
        if 'next' in request.GET:
            next = request.GET['next']
        else:
            next = None
            
        return render(request, "auctions/login.html", {
            'next': next
        })


def logout_view(request):
    logout(request)
    return render(request, "auctions/index.html", {
        "message": "You have been logged out."
    })


@login_required
def place_bid(request):
    """Lot of repetition of generate_notification(); however, even though
    that function does return the notification object, making changes to it
    don't seem to properly save to the DB.
    """
    if request.method == "GET":
        return HttpResponseRedirect(reverse("index"))
    else:
        listing_id = request.POST["listing-id"]
        listing_bundle = get_listing(request, listing_id)
        if listing_bundle['expiration_bundle']['expired'] == True:
            notification = build_notification(
                    request.user,
                    TYPE_WARNING,
                    ICON_WARNING,
                    MESSAGE_LISTING_EXPIRED,
                    True,
                    'listing_page'
                )
            notification.save()
        else:
            bid = request.POST["bid"]
            if not bid.isdigit():
                notification = build_notification(
                    request.user,
                    TYPE_WARNING,
                    ICON_WARNING,
                    MESSAGE_LISTING_BID_FORMATTING,
                    True,
                    'listing_page'
                )
                notification.save()
            elif int(bid) > 99999:
                notification = build_notification(
                    request.user,
                    TYPE_WARNING,
                    ICON_WARNING,
                    MESSAGE_LISTING_BID_TOO_HIGH,
                    True,
                    'listing_page'
                )
                notification.save()
            elif int(bid) <= listing_bundle["listing"].current_bid:
                notification = build_notification(
                    request.user,
                    TYPE_WARNING,
                    ICON_WARNING,
                    MESSAGE_LISTING_BID_TOO_LOW,
                    True,
                    'listing_page'
                )
                notification.save()
            else:
                new_bid = Bid.objects.create(
                    amount=decimal.Decimal(bid), 
                    user=request.user, 
                    listing=listing_bundle["listing"])
                new_bid.save()
                listing_bundle = get_listing(request, listing_id)
                notification = build_notification(
                    request.user,
                    TYPE_SUCCESS,
                    ICON_SUCCESS,
                    MESSAGE_LISTING_BID_SUCCESSFUL,
                    True,
                    'listing_page'
                )
                notification.save()
                

        return HttpResponseRedirect(
            reverse("view_listing", args=[listing_id]))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


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

        if request.method == "POST":
            # instantiate forms
            profile_picture_form = NewImageForm(request.POST, request.FILES)
            random_setting_form1 = ''
            random_setting_form2 = ''
            random_setting_form3 = ''


            # see what, if anything, has changed.
            img_upload = request.FILES.get('image', None)
            img_url = request.POST.get('image_url', None)
            random_setting1 = ''
            random_setting2 = ''
            random_setting3 = ''

            # check for profile image
            if img_upload or img_url:
                if profile_picture_form.is_valid():

                    if img_url:
                        # source for saving image to temp file:
                        # Mayank Jain https://medium.com/@jainmickey
                        filename = img_url.split('/')[-1].split('.')[0] + ".jpg"
                        res = requests.get(img_url, stream=True)
                        img_temp = tempfile.NamedTemporaryFile(delete=True)
                        for block in res.iter_content(1024 * 8):
                            if not block:
                                break
                            img_temp.write(block)
                            # convert to ImageFile?
                        img_source = files.images.ImageFile(img_temp, name=filename)
                    else:
                        img_source = img_upload
                    

                    img_mod = User_Image(
                        owner=request.user,
                        image=img_source
                    )
                    img_mod.save_thumbnail()
                    img_mod.save()

                    notification = build_notification(
                        request.user,
                        TYPE_SUCCESS,
                        ICON_SUCCESS,
                        MESSAGE_USER_PICTURE_UPLOAD_SUCCESS,
                        True
                    )
                    notification.save()

                    return render(request, "auctions/settings.html", {
                        'profile_picture_form': profile_picture_form,
                        'img': img_mod.thumbnail.url
                    })
                else:
                    notification = build_notification(
                        request.user,
                        TYPE_WARNING,
                        ICON_WARNING,
                        MESSAGE_USER_PICTURE_UPLOAD_FAILURE,
                        True
                    )
                    notification.save()
                    return render(request, "auctions/settings.html")

            elif random_setting1:
                pass

            elif random_setting2:
                pass

            elif random_setting3:
                pass

            # no changes were made
            else:
                return render(request, "auctions/settings.html", {
                    'profile_picture_form': profile_picture_form
                })

        # request = GET
        else:
            return render(request, "auctions/settings.html", {
                'profile_picture_form': profile_picture_form
            })



def shopping_cart(request):
    return HttpResponseRedirect(reverse('index'))


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

""" 
def format_comment(raw_comment) -> dict:
    formatted_comment = {
        "content": raw_comment.content,
        "listing": raw_comment.listing,
        "user": raw_comment.user,
        "replyTo": raw_comment.replyTo }
    if raw_comment.replyTo:
        formatted_comment["originalContent"] = raw_comment.replyTo.content


def get_comments(raw_listing) -> QuerySet:
    raw_comments = raw_listing.listings_comments.all().order_by('-timestamp')
    return map(format_comment, raw_comments)

"""
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


# //////////////////////////////////////////////////////
# RANDOM OBJECT GENERATION
# //////////////////////////////////////////////////////


def generateListing(amount):
    listings = []
    for i in range(amount):
        listing = {
            'title': generateTitle(),
            'image_url': generateImage(),
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
