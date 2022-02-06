from django.urls import reverse

from auctions.globals import (AJAX_DELETE_COMMENT, AJAX_DISMISS_NOTIFICATION,
                              AJAX_GENERATE_COMMENT, AJAX_GENERATE_USER,
                              AJAX_PURGE_MEDIA, AJAX_REPLY_COMMENT,
                              AJAX_UPLOAD_MEDIA, AJAX_WATCH_LISTING)


def ajax(request):
    return {
        'delete_comment': {
            'name': AJAX_DELETE_COMMENT, 
            'url': reverse(AJAX_DELETE_COMMENT)
        },
        'dismiss_notification': {
            'name': AJAX_DISMISS_NOTIFICATION, 
            'url': reverse(AJAX_DISMISS_NOTIFICATION)
        },
        'generate_comment': {
            'name': AJAX_GENERATE_COMMENT,
            'url': reverse(AJAX_GENERATE_COMMENT)
        },
        'generate_user': {
            'name': AJAX_GENERATE_USER,
            'url': reverse(AJAX_GENERATE_USER)
        },
        'purge_media': {
            'name': AJAX_PURGE_MEDIA,
            'url': reverse(AJAX_PURGE_MEDIA)
        },
        'reply_comment': {
            'name': AJAX_REPLY_COMMENT,
            'url': reverse(AJAX_REPLY_COMMENT)
        },
        'upload_media': {
            'name': AJAX_UPLOAD_MEDIA,
            'url': reverse(AJAX_UPLOAD_MEDIA)
        },
        'watch_listing': {
            'name': AJAX_WATCH_LISTING,
            'url': reverse(AJAX_WATCH_LISTING)
        }
    }
