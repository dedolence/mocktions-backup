from multiprocessing.dummy import Array
import tempfile
import requests
from datetime import timedelta
from math import floor
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .notifications import *
from .strings import *
from .globals import *
import json

def get_highest_bid(listing) -> Bid:
    bids = Bid.objects.filter(listing=listing).order_by('-amount')
    return bids.first()


def get_image(request, url=None) -> UserImage:
    """ Can be called with or without the url parameter. When no url
    is provided, a random image will be returned.
    """
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
    if res.headers['content-type'] in content_types:
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
            image=img_source
        )
        img_mod.save_thumbnail()
        img_mod.save()
        return img_mod


def get_listing(request, id=None, listing=None) -> dict:
    """TODO: This method is completely unnecessary at this point."""
    if not listing:
        listing = Listing.objects.get(pk=id)

    highest_bid = get_highest_bid(listing)
    #listing.current_bid = highest_bid.amount if highest_bid else listing.starting_bid
    owner_controls = True if listing.owner == request.user else False
    watch_options = True if owner_controls == False else True
    watchlist = request.user.watchlist.all()
    watching_currently = True if listing in watchlist else False
    # expiration_bundle = get_expiration(listing)
    return {
        'listing': listing,
        #'owner_controls': owner_controls,
        #'watch_options': watch_options,
        #'watching_currently': watching_currently,
        #'expiration_bundle': expiration_bundle
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

    #if not controls_dict['show_expired']:
    ordered_listings = ordered_listings.filter(active=not controls_dict['show_expired'])

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

    formatted_listings = [listing for listing in current_page.object_list]
    
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
    """Every time index.html is loaded, flag any listings that are no 
    longer active and notify winners if necessary.
    """
    all_listings = Listing.objects.all()
    watchlist = request.user.watchlist.all()

    for listing in all_listings:
        # find expired listings
        if listing.active and listing.expired:
            if listing.winner and listing.winning_bid:
                listing.winning_user = listing.winner
                notify_winner(listing.winner, listing)
            if listing in watchlist:
                request.user.watchlist.remove(listing)
            listing.active = False
            listing.save()


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # handle the event
    if event['type'] == 'checkout.session.async_payment_failed':
      session = event['data']['object']
      print(session)
    elif event['type'] == 'checkout.session.async_payment_succeeded':
      session = event['data']['object']
      print(session)
    elif event['type'] == 'checkout.session.completed':
      session = event['data']['object']
      print(session)
    elif event['type'] == 'checkout.session.expired':
      session = event['data']['object']
      print(session)
    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))

    return HttpResponse(status=200)



def upload_images(request, files, listing=None) -> Array:    
    uploaded_images = []
    for f in files:
        img_mod = UserImage(
            image=f,
            listing=listing
        )
        img_mod.listing = listing
        img_mod.save_thumbnail()
        img_mod.save()
        uploaded_images.append(img_mod)
    return uploaded_images