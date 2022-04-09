from multiprocessing import context
import random
import requests
from django.core import serializers
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
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
        context = {
            'click_action': "showEditImageModal",
            'image': image_instance
        }
        html_string += render_to_string('auctions/includes/imageThumbnail.html', context)
    response['html'] = html_string
    return JsonResponse(response)


def ajax_delete_comment(request):
    comment = Comment.objects.get(pk=id)
    comment.delete()


def ajax_dismiss_notification(request):
    notification_id = request.POST.get('notification_id', None)
    if notification_id:
        notification = Notification.objects.get(pk=notification_id)
        notification.delete()
        return JsonResponse({})
    else:
        return JsonResponse({}, status=404)


def ajax_generate_comment(request):
    response = {}
    message = ''
    for i in range(0, random.randint(1,5)):
        message += GEN.sentence()
    response["message"] = message
    return JsonResponse(response)


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
    # click_action defines what should happen when the thumbnail is clicked
    # (either show an edit modal or a view modal)
    click_action = request.POST.get('click_action', None)
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
            images = [get_image(request, url, reverse('create_listing'))]
        
        if images:
            image_ids = [i.id for i in images]
            html_string = ''
            # generate HTML for these images to be displayed
            for id in image_ids:
                image_instance = UserImage.objects.get(pk=id)
                html_string += render_to_string('auctions/includes/imageThumbnail.html', {
                    'image': image_instance,
                    'click_action': click_action
                })
            response['paths'] = [i.image.url for i in images]
            response['ids'] = image_ids
            response['html'] = html_string
   
    return JsonResponse(response)


def ajax_watch_listing(request):
    listing_id = request.POST.get('listing_id', None)
    listing = get_object_or_404(Listing, pk=listing_id)
    context = {'listing': listing}

    if not listing_id or not listing:
        return JsonResponse({'message': MESSAGE_GENERIC_ERROR}, status=403)
    else:
        if listing in request.user.watchlist.all():
            request.user.watchlist.remove(listing)
            context['toast_message'] = MESSAGE_WATCHLIST_REMOVED
            context['in_watchlist'] = False
        else:
            request.user.watchlist.add(listing)
            context['toast_message'] = MESSAGE_WATCHLIST_ADDED
            context['in_watchlist'] = True
    
    return JsonResponse({
        'html': render_to_string('auctions/includes/watchlistButton.html', context)
        })