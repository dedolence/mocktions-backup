import random
from tkinter import N
import requests
import stripe

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import \
    csrf_exempt
from django.views.decorators.http import require_http_methods

from . import namelist, wordlist
from .ajax_controls import *
from .forms import BioForm, CommentEditForm, CommentForm, CommentReplyForm, NewBidForm, NewListingCreateForm, NewListingSubmitForm, RegistrationForm
from .globals import *
from .models import Bid, Category, Comment, UserImage, Listing, User
from .notifications import *
from .strings import *
from .utility import *


# //////////////////////////////////////////////////////
# URL PATH VIEWS
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


def add_image(request, listing_id):
    notification = NotificationTemplate()
    # check current image count
    listing = get_object_or_404(Listing, pk=listing_id)
    uploaded_image_count = listing.all_images.count()

    if request.user is not listing.owner:
        notification.build(
            request.user,
            TYPE_WARNING,
            ICON_WARNING,
            MESSAGE_LISTING_EDIT_PROHIBITED,
            True,
        )
        return HttpResponseRedirect(reverse('index'))
    
    if uploaded_image_count >= MAX_UPLOADS_PER_LISTING:
        notification.build(
            request.user,
            TYPE_WARNING,
            ICON_WARNING,
            MESSAGE_LISTING_MAX_UPLOADS_EXCEEDED,
            True,
            reverse('edit_listing', args=[listing_id])
        )
        notification.save()
        return HttpResponseRedirect(reverse('edit_listing', args=[listing_id]))

    if request.FILES:
        files = request.FILES.getlist('files', None)
        total_images = len(files) + uploaded_image_count
        if total_images > MAX_UPLOADS_PER_LISTING:
            notification.build(
                        request.user,
                        TYPE_WARNING,
                        ICON_WARNING,
                        MESSAGE_LISTING_MAX_UPLOADS_EXCEEDED,
                        True,
                        reverse('edit_listing', args=[listing_id])
                    )
            notification.save()
            return HttpResponseRedirect(reverse('edit_listing', args=[listing_id]))
        
        try:
            images = upload_images(request, files)
        except Image.DecompressionBombError:
            notification.build(
                request.user,
                TYPE_DANGER,
                ICON_DANGER,
                MESSAGE_LISTING_UPLOAD_TOO_LARGE,
                True,
                reverse('edit_listing', args=[listing_id])
            )
            return HttpResponseRedirect(reverse('edit_listing', args=[listing_id]))
    else:
        # User provided URL of an image
        url = request.POST.get('url', None)
        images = [get_image(request, url)]
    
    return HttpResponseRedirect(reverse('edit_listing', args=[listing_id]))


def category(request, category_id):
    category_title = Category.objects.get(id=category_id)
    category_listings_raw = Listing.objects.filter(category_id=category_id)
    page_tuple = get_page(request, category_listings_raw)
    return render(request, "auctions/category.html", {
        'category_id': category_id,
        'category_title': category_title,
        'listings': page_tuple[1],
        'controls_dict': page_tuple[0]
    })


def categories(request):
    return render(request, "auctions/categories.html", {
        'categories': Category.objects.all()
    })


def checkout(request):

    line_items = []
    items = request.user.shopping_cart.all()
    for item in items:
        # stripe requires all amounts to be in the smallest currency unit; i.e. pennies for USD
        line_items.append({
        'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': item.title,
            },
            'unit_amount': int(item.winning_bid * 100),
        },
        'quantity': 1,
        })

    shipping_data = [{
        'shipping_rate_data': {
            'type': 'fixed_amount',
            'fixed_amount': {
                # sum individual shipping costs, convert to pennies, cast to integer
                'amount': int(sum([(item.shipping * 100) for item in items])),
                'currency': 'usd',
            },
            'display_name': 'Standard ground',
            'delivery_estimate': {
                'minimum': {
                    'unit': 'business_day',
                    'value': 7,
                },
                'maximum': {
                    'unit': 'business_day',
                    'value': 14,
                },
            }
        }
    }]

    session = stripe.checkout.Session.create(
        line_items=line_items,
        payment_method_types=['card'],
        shipping_address_collection=STRIPE_ALLOWED_SHIPPING_COUNTRIES,
        shipping_options=shipping_data,
        mode='payment',
        # TODO: replace these with the actual host duh
        success_url='http://127.0.0.1:8000/order/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://127.0.0.1:8000'+reverse('checkout_cancel')
    )

    new_order = Order.objects.create(session_id=session.id, user=request.user)
    for item in items:
        new_order.items.add(item)
    new_order.save()

    return HttpResponseRedirect(session.url)


@require_http_methods(['GET'])
def checkout_success(request):
    """ Create a notification and redirect to index. """
    notification = NotificationTemplate()
    session_id = request.GET.get('session_id', None)
    session = stripe.checkout.Session.retrieve(session_id)

    order = get_object_or_404(Order, session_id=session_id)
    if not order:
        notification.build(
            request.user,
            TYPE_WARNING,
            ICON_WARNING,
            MESSAGE_ORDER_FAILURE,
            True,
            reverse('index')
        )
        notification.save()
        return HttpResponseRedirect(reverse('index'))
    else:
        if session['payment_status'] == "paid":
            order.status = session['payment_status']
            order.save()

            thanks_notification = NotificationTemplate()
            thanks_notification.build(
                request.user,
                TYPE_INFO,
                ICON_GENERIC,
                MESSAGE_ORDER_THANKS,
                True,
                reverse('index')
            )
            thanks_notification.save()

            notification.build(
                request.user,
                TYPE_SUCCESS,
                ICON_SUCCESS,
                MESSAGE_ORDER_SUCCESSFUL.format(reverse('orders')),
                False,
                reverse('index')
            )
            notification.save()

            return HttpResponseRedirect(reverse('index'))
        else:
            notification.build(
                request.user,
                TYPE_WARNING,
                ICON_WARNING,
                MESSAGE_ORDER_FAILURE,
                True,
                reverse('index')
            )
            notification.save()

        return HttpResponseRedirect(reverse('index'))



def checkout_cancel(request):
    return HttpResponseRedirect(reverse('index'))


@require_http_methods(['POST'])
def comment(request):
    listing_id = request.POST.get('listing', None)
    listing = get_object_or_404(Listing, pk=listing_id)
    content = request.POST.get('content', None)

    comment_id = request.POST.get('comment_id', None)

    if listing and content:
        if comment_id:
            comment = get_object_or_404(Comment, pk=comment_id)
            form = CommentForm(request.POST, instance=comment)
        else:
            form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save()
            comment.user = request.user
            comment.save()
            return HttpResponseRedirect(reverse('view_listing', args=[listing_id]))
        else:
            return render(request, "auctions/viewListing.html", {
                'listing': listing,
                'bid_form': NewBidForm(),
                'comment_form': form,
                'comment_edit_form': CommentEditForm(),
                'comment_reply_form': CommentReplyForm()
            })


@require_http_methods(['POST'])
def comment_reply(request):
    pass


@login_required
@require_http_methods(["GET", "POST"])
def create_listing(request):
    """GET: generate a blank form and render template.
    POST: Create a Listing object, attach images, and redirect
    to edit_listing.py.
    """
    notification = NotificationTemplate()
    # check to see if this user has reached the cap on listing drafts
    temps = Listing.objects.filter(owner=request.user, active=False).count()
    if temps >= LISTING_DRAFT_CAP:
        notification.build(
            request.user,
            TYPE_WARNING,
            ICON_WARNING,
            MESSAGE_LISTING_DRAFT_CAP_EXCEEDED,
            True,
            reverse('drafts')
        )
        notification.save()
        return HttpResponseRedirect(reverse('drafts'))
    
    if request.method == "GET":
        form = NewListingCreateForm()
        return render(request, 'auctions/createListing.html', {
            'form': form
        })
    else:
        form = NewListingCreateForm(request.POST)
        if 'randomize' in request.POST:
            listing = generate_listing(request)
        else:
            listing = form.save(commit=False)
            # set image foreign keys to point to this listing.
            image_ids = request.POST.getlist('images', None)
            if image_ids and len(image_ids) > 0:
                for id in image_ids:
                    image = UserImage.objects.get(pk=id)
                    image.listing = listing
                    image.save()
                
            listing.owner = request.user
            listing.active = False
            listing.save()

        return HttpResponseRedirect(reverse('edit_listing', args=[listing.id]))


@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    notification = NotificationTemplate()
    
    if request.user != listing.owner:
        notification.build(
            request.user,
            TYPE_DANGER,
            ICON_DANGER,
            MESSAGE_USER_DELETE_PROHIBITED,
            True
        )
        notification.save()
        return HttpResponseRedirect(reverse('index'))
    
    if request.method == "GET":
        return render(request, 'auctions/deleteListing.html', {
            'listing': listing
        })
    else:
        listing.delete()
        notification = NotificationTemplate()
        notification.build(
            request.user,
            TYPE_SUCCESS,
            ICON_SUCCESS,
            MESSAGE_USER_LISTING_DELETED.format(listing.title),
            False,
            reverse('index')
        )
        notification.save()
        return HttpResponseRedirect(reverse('index'))
    


@login_required
def drafts(request):
    notifications = get_notifications(request.user, reverse('drafts'))
    results = Listing.objects.filter(owner=request.user, active=False)
    drafts = [listing for listing in results if listing.expired == False]
    return render(request, 'auctions/drafts.html', {
        'drafts': drafts,
        'notifications': notifications
    })


@login_required
def edit_listing(request, listing_id):
    """Edit a listing; functions as a preview as well. If routed
    to via create_listing, a Listing must be generated. Otherwise,
    get the Listing that already exists."""
    notification = NotificationTemplate()

    listing = get_object_or_404(Listing, pk=listing_id)
    # check whether editing is permitted
    if (request.user != listing.owner 
        or listing.current_bid 
        or listing.expired):
        notification.build(
            request.user,
            TYPE_WARNING,
            ICON_WARNING,
            MESSAGE_LISTING_EDIT_PROHIBITED.format(listing.title),
            True,
            reverse('index')
        )
        notification.save()
        return HttpResponseRedirect(reverse("index"))

    if request.method == "GET":
        # redirected here after a draft listing is created
        form = NewListingCreateForm(instance=listing)
    else:
        # redirected here from editListing.html
        form = NewListingCreateForm(request.POST, instance=listing)
        form.save()
        # in case there are new images, link them to this listing
        image_ids = request.POST.getlist('images', None)
        if image_ids and len(image_ids) > 0:
            for id in image_ids:
                image = UserImage.objects.get(pk=id)
                image.listing = listing
                image.save()

    context = {
        'listing': listing,
        'form': form
    }
    return render(request, 'auctions/editListing.html', context)
        

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
            'listings': listing_page_tuple[1],
            'notifications': notifications
        })


def listing_page(request, listing_id):
    if request.user.is_authenticated:
        notifications = get_notifications(
            request.user, 
            reverse('view_listing', args=[listing_id])
        )
    else:
        notifications = None

    listing = get_object_or_404(Listing, pk=listing_id)
    initial_dict = {
        'user': request.user,
        'listing': listing
    }
    bid_form = NewBidForm(initial=initial_dict)
    comment_form = CommentForm(initial=initial_dict)
    comment_edit_form = CommentEditForm(
        auto_id='edit_%s', 
        initial=initial_dict
        )
    comment_reply_form = CommentReplyForm(
        auto_id='reply_%s',
        initial=initial_dict
        )
    return render(request, "auctions/viewListing.html", {
        'listing': listing,
        'bid_form': bid_form,
        'comment_form': comment_form,
        'comment_edit_form': comment_edit_form,
        'comment_reply_form': comment_reply_form,
        'notifications': notifications
    })


@csrf_exempt
def listings(request):
    all_listings = Listing.objects.all()
    page_tuple = get_page(request, all_listings)
    return render(request, "auctions/listings.html", {
        'controls_dict': page_tuple[0],
        'listings': page_tuple[1]
    })


def login_view(request):
    if request.method == "POST":
         # Attempt to sign user in
        u = request.POST.get("username", None)
        p = request.POST.get('password', None)
        user = authenticate(request, username=u, password=p)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
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


def orders(request):
    pass


@login_required
def place_bid(request, listing_id):
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
        listing = get_object_or_404(Listing, pk=listing_id)
        bid_form = NewBidForm(request.POST)
        if not bid_form.is_valid():
            return render(request, 'auctions/viewListing.html', {
                'listing': listing,
                'bid_form': bid_form,
                'notifications': get_notifications(
                    request.user, 
                    reverse('view_listing', args=[listing.id])
                    )
            })
        else:
            new_bid = bid_form.save()
            # build notification
            return HttpResponseRedirect(reverse('view_listing', args=[listing.id]))



def register(request):
    if (request.user.is_authenticated):
        return HttpResponseRedirect(reverse('index'))
    
    notification = NotificationTemplate()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # create and authenticate user
            user = form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
                )
            login(request, user)
            
            # set profile picture, if provided
            image_ids = request.POST.getlist('images', None)
            if (image_ids):
                image_id = image_ids[0]
                image = UserImage.objects.get(pk=image_id)
                image.owner = user
                image.save()
                user.profile_pic = image
                user.save()
            
            # create a welcome message
            notification.build(
                user,
                TYPE_SUCCESS,
                ICON_SUCCESS,
                MESSAGE_REG_SUCCESS,
                False,
                reverse('index')
            )
            notification.save()

            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'auctions/register.html', {
                'form': form
            })
    else:
        form = RegistrationForm()
        return render(request, 'auctions/register.html', {
            'form': form
        })


def remove_image(request, image_id, listing_id=None,):
    image = get_object_or_404(UserImage, pk=image_id)
    image.delete()
    if listing_id:
        return HttpResponseRedirect(reverse('edit_listing', args=[listing_id]))
    else:
        return


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
    

@login_required
def settings(request):
    if request.method == "GET":
        form = BioForm(instance=request.user)
        return render(request, 'auctions/settings.html', {
            'form': form
        })
    else:
        form = BioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()

            if "images" in request.POST:
                image_id = request.POST.getlist('images', None)[0]
                image = UserImage.objects.get(pk=image_id)
                request.user.profile_pic = image
                request.user.save()

            notification = NotificationTemplate()
            notification.build(
                request.user,
                TYPE_SUCCESS,
                ICON_SUCCESS,
                MESSAGE_USER_PROFILE_UPDATE_SUCCESS,
                True,
                reverse('settings')
            )
            notification.save()
            return HttpResponseRedirect(reverse('settings'))
    """ if not request.user.is_authenticated:
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
 """

def shopping_cart(request):
    listings = request.user.shopping_cart.all()
    subtotal_items = sum([listing.winning_bid for listing in listings])
    subtotal_shipping = sum([listing.shipping for listing in listings])
    total = subtotal_items + subtotal_shipping
    return render(request, 'auctions/cart.html', {
        'listings': listings,
        'subtotal_items': subtotal_items,
        'subtotal_shipping': subtotal_shipping,
        'total': total
    })


@login_required
def submit_listing(request, listing_id):
    notification = NotificationTemplate()
    context = {}

    # find the temporary listing
    listing_id = request.POST.get('listing_id', None)
    listing = get_object_or_404(Listing, pk=listing_id)
    if listing.owner != request.user:
        notification.build(
            request.user,
            TYPE_WARNING,
            ICON_WARNING,
            MESSAGE_GENERIC_PERMISSIONS,
            True,
            reverse('index')
        )
        notification.save()
        return HttpResponseRedirect(reverse('index'))

    # bind post data to a form; this form REQUIRES every field
    form = NewListingSubmitForm(request.POST, instance=listing)

    # set foreign keys of any new images, validate number
    image_ids = request.POST.getlist('images', None)
    for id in image_ids:
        image = UserImage.objects.get(pk=id)
        image.listing = listing
        image.save()
    if len(image_ids) < MIN_UPLOADS_PER_LISTING:
        notification.build(
            request.user,
            TYPE_WARNING,
            ICON_WARNING,
            MESSAGE_LISTING_CREATION_IMAGES_REQUIRED,
            True,
            reverse('edit_listing')
        )
        notification.save()
        context = {
            'notifications': get_notifications(
                request.user, 
                reverse('edit_listing')
                ),
            'form': form,
            'listing': listing,
            'form_mode': LISTING_FORM_PREVIEW,
            'template': 'auctions/editListing.html'
        }
        return render(request, context['template'], context)
    
    # check form and submit or return errors
    if not form.is_valid():
        return render(request, 'auctions/editListing.html', {
            'form': form,
            'listing': listing
        })
    else:
        active_listing = form.save(commit=False)
        active_listing.active = True
        active_listing.save()
        return HttpResponseRedirect(
            reverse("view_listing", args=[active_listing.id])
        )


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


@login_required
def watchlist(request):
    # purge listings that have expired
    purge_listings(request)
    notifications = get_notifications(request.user, 'index')
    active_listings_raw = request.user.watchlist.all()
    listing_page_tuple = get_page(request, active_listings_raw)
    return render(request, "auctions/watchlist.html", {
        'listing_controls': listing_page_tuple[0],
        'listings': listing_page_tuple[1],
        'notifications': notifications
    })


# //////////////////////////////////////////////////////
# TEST VIEW
# //////////////////////////////////////////////////////

""" def test_view(request):
    return render(request, 'auctions/tests/bootstrapgrid.html') """




# //////////////////////////////////////////////////////
# RANDOM OBJECT GENERATION
# //////////////////////////////////////////////////////


def generate_listing(request):
    listing = Listing.objects.create(
        owner = request.user,
        category = random.choice(Category.objects.all()),
        title = generate_title(),
        description = generate_description()[0:400],
        starting_bid = random.randint(1,9999),
        shipping = random.randint(5, 50),
        lifespan = random.randint(1, 30)
    )
    
    for i in range(0, random.randint(1, MAX_UPLOADS_PER_LISTING)):
        image = get_image(request, None)
        image.listing = listing
        image.save()
    
    return listing


def generate_title():
    adj = random.choice(wordlist.adjectives)
    noun = random.choice(wordlist.nouns)
    return f"{adj.capitalize()} {noun}"


def generate_image():
    # sorta inefficient because the api loads a random image but only looks at the response headers for the id to generate a static URL,
    # so the image is ultimately served twice, first here and again when its absolute URL is called :(
    # but since this is only for testing purposes really it doesn't matter so much, and it's only 200px square images
    image_api = requests.get('https://picsum.photos/200')
    image_id = image_api.headers['picsum-id']
    return f'https://picsum.photos/id/{image_id}/200'


def generate_description():
    return GEN.paragraph()


def picsum(request):
    image_api = requests.get('https://picsum.photos/200')
    image_id = image_api.headers['picsum-id']
    image_url = f'https://picsum.photos/id/{image_id}/200'
    return render(request, 'auctions/tests/picsum.html', {
        'url': image_url
    })

def generate_name():
    firstname = random.choice(namelist.firstnames)
    lastname = random.choice(namelist.lastnames)
    return (firstname, lastname)