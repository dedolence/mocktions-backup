import random
from django.core import serializers
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from auctions.testing import generate_bulk_listings, generate_listing

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
    comment_id = request.POST.get('comment_id', None)
    if comment_id:
        comment = get_object_or_404(Comment, pk=comment_id)
        if comment.user == request.user:
            comment.delete()
            return JsonResponse({}, status=200)
        else:
            error_string = f"Comment user: {comment.user}\nRequest user: {request.user}"
            return JsonResponse({'error':error_string}, status=403)


def ajax_dismiss_notification(request):
    notification_id = request.POST.get('notification_id', None)
    if notification_id:
        try:
            notification = Notification.objects.get(pk=notification_id)
            notification.delete()
        except Notification.DoesNotExist:
            pass
        return JsonResponse({}, status=200)


def ajax_generate_comment(request):
    response = {}
    comment = ''
    for i in range(0, random.randint(1,5)):
        comment += GEN.sentence().strip()
    response["comment"] = comment[0:200]
    return JsonResponse(response)


def ajax_generate_listing(request):
    listing = generate_listing(request)
    listing.draft = False
    listing.active = True
    listing.save()
    html = render_to_string('auctions/includes/listingDraft.html', {
        'listing': listing
    })
    return JsonResponse({'html': html})


def ajax_reply_comment(request):
    response = {}
    # Filter() must be used instead of get() to return iterable for serializer
    # (or wrap the queryset in [] to list-ify it).
    comment_id = request.POST.get('comment_id', None)
    comment = Comment.objects.filter(pk=comment_id)
    response["comment"] = serializers.serialize("json", comment)
    response["author"] = comment.first().user.username
    return JsonResponse(response)


def ajax_upload_media(request):
    response = {}
    images = None
    current_image_count = request.POST.get('currentImageCount', None)
    listing_id = request.POST.get('listing_id', None)
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
            images = [get_image(request, url)]
        
        if images:
            image_ids = [i.id for i in images]
            html_string = ''
            
            # generate HTML for these images to be displayed
            for id in image_ids:
                image_instance = UserImage.objects.get(pk=id)

                # Since JS uses "null" instead of None...
                if listing_id != 'null':
                    listing = get_object_or_404(Listing, pk=listing_id)
                else:
                    listing = None
                
                html_string += render_to_string('auctions/includes/imageThumbnail.html', {
                    'image': image_instance,
                    'listing': listing
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