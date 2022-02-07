from multiprocessing.dummy import Array
import tempfile
import requests
from datetime import timedelta
from math import floor
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from .models import *
from .notifications import *
from .strings import *
from .globals import *


def get_expiration(listing) -> dict:
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


def get_highest_bid(listing) -> Bid:
    bids = Bid.objects.filter(listing=listing).order_by('-amount')
    return bids.first()


def get_image(request, url=None, page=None, listing=None) -> Array:
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


def get_listing(request, id=None, listing=None) -> dict:
    if not listing:
        listing = Listing.objects.get(pk=id)

    highest_bid = get_highest_bid(listing)
    listing.current_bid = highest_bid.amount if highest_bid else listing.starting_bid
    owner_controls = True if listing.owner == request.user else False
    watch_options = True if owner_controls == False else True
    watchlist = request.user.watchlist.all()
    watching_currently = True if listing in watchlist else False
    expiration_bundle = get_expiration(listing)
    return {
        'listing': listing,
        'owner_controls': owner_controls,
        'watch_options': watch_options,
        'watching_currently': watching_currently,
        'expiration_bundle': expiration_bundle
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


def purge_listings(request) -> None:
    """Since this isn't being run on a real server that can purge things in real time,
    instead, every time index.html is loaded, flag any listings that are no longer active.
    """
    all_listings = Listing.objects.all()
    watchlist = request.user.watchlist.all()

    for listing in all_listings:
        expiration = get_expiration(listing)
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


def upload_images(request, files, listing=None) -> Array:    
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