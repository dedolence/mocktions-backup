import random
import requests
from django.core import serializers
from django.http.response import JsonResponse
from django.urls import path
from .models import *
from .strings import *
from .globals import *
from .utility import *


def ajax_delete_comment(request):
    comment = Comment.objects.get(pk=id)
    comment.delete()


def ajax_dismiss_notification(request):
    try:
        notification = Notification.objects.get(pk=id)
        notification.delete()
    except Notification.ObjectDoesNotExist:
        pass


def ajax_generate_comment(request):
    response = {}
    message = ''
    for i in range(0, random.randint(1,5)):
        message += GEN.sentence()
    response["message"] = message
    return JsonResponse(response)


def ajax_generate_user(request):
    return requests.get('https://randomuser.me/api/').json()["results"][0]


def ajax_purge_media(request):
    img_id = request.POST.get('img_id', None)
    img_mod = UserImage.objects.get(pk=img_id)
    """
    If the auto-delete middleware doesn't do its job and delete
    abandoned media, this will:
        img_mod.image.close()
        img_mod.image.delete()
        img_mod.thumbnail.close()
        img_mod.thumbnail.delete()
    """
    img_mod.delete()
    return JsonResponse({'message': 'Image removed successfully.'})


def ajax_reply_comment(request):
    response = {}
    # Filter must be used instead of get to return iterable for serializer
    # (or wrap the queryset in [] to list-ify it).
    comment = Comment.objects.filter(pk=id)
    response["comment"] = serializers.serialize("json", comment)
    response["author"] = comment.first().user.username
    return JsonResponse(response)



def ajax_upload_media(request):
    response = {}
    listing_id = request.POST.get('listing_id', None)
    if not listing_id:
        response['error'] = "Listing ID not found: can't save images."
    else:
        try:
            listing = Listing.objects.get(pk=listing_id)
        except Listing.DoesNotExist:
            try:
                listing = TempListing.objects.get(pk=listing_id)
            except TempListing.DoesNotExist:
                request['error'] = "No listing found with that ID."

        current_count = listing.images.count()
        images = None
        if request.FILES:
            # User uploaded images from their computer
            files = request.FILES.getlist('files', None)
            if (len(files) + current_count) > MAX_UPLOADS_PER_LISTING:
                response['error'] = MESSAGE_LISTING_MAX_UPLOADS_EXCEEDED
            else:
                try:
                    images = upload_images(request, files, listing)
                except Image.DecompressionBombError:
                    response['error'] = 'DecompressionBombError'
        else:
            # User provided URL of an image
            url = request.POST.get('url', None)
            images = get_image(request, url, reverse('create_listing'), listing)
        
        if images:
            response['paths'] = [i.image.url for i in images]
            response['ids'] = [i.id for i in images]
        
        return JsonResponse(response)


def ajax_watch_listing(request):
    response = {}
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
    return JsonResponse(response)
