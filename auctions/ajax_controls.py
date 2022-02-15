import random
import requests
from django.core import serializers
from django.http.response import JsonResponse
from django.template.loader import render_to_string
from django.urls import path
from .models import *
from .strings import *
from .globals import *
from .utility import *


def ajax_build_image_thumbnail(request):
    image_ids = request.POST.get('ids', None)
    html_string = ''
    response = {}
    for id in image_ids:
        image_instance = UserImage.objects.get(pk=id)
        html_string += render_to_string('auctions/includes/imageThumbnail.html', {
            'image': image_instance
        })
    response['html'] = html_string
    return JsonResponse(response)


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
    images = None
    current_image_count = request.POST.get('currentImageCount', None)
    if int(current_image_count) >= MAX_UPLOADS_PER_LISTING:
        response['error'] = MESSAGE_LISTING_MAX_UPLOADS_EXCEEDED
    else:
        if request.FILES:
            # User uploaded images from their computer
            files = request.FILES.getlist('files', None)
            if len(files) > MAX_UPLOADS_PER_LISTING:
                response['error'] = MESSAGE_LISTING_MAX_UPLOADS_EXCEEDED
            else:
                try:
                    images = upload_images(request, files)
                except Image.DecompressionBombError:
                    response['error'] = MESSAGE_LISTING_UPLOAD_TOO_LARGE
        else:
            # User provided URL of an image
            url = request.POST.get('url', None)
            images = get_image(request, url, reverse('create_listing'))
        
        if images:
            image_ids = [i.id for i in images]
            html_string = ''
            # generate HTML for these images to be displayed
            for id in image_ids:
                image_instance = UserImage.objects.get(pk=id)
                html_string += render_to_string('auctions/includes/imageThumbnail.html', {
                    'image': image_instance
                })
            response['paths'] = [i.image.url for i in images]
            response['ids'] = image_ids
            response['html'] = html_string
   
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
