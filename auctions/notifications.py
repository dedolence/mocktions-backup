from mimetypes import init
from django.db.models.query import QuerySet

from auctions.globals import ICON_GENERIC, ICON_SUCCESS, TYPE_INFO, TYPE_SUCCESS
from . import strings
from .models import Notification
from django.urls import reverse


class NotificationTemplate():
    def __init__(self) -> None:
        self.notification = Notification()
    
    def build(self, 
            user, type, icon, message, 
            autodelete=False, page='index') -> None:
        """ For setting all values at once. """
        self.notification.user = user
        self.notification.type = type
        self.notification.autodelete = autodelete
        self.notification.page = page
        self.notification.content = (
            strings.MESSAGE_GENERIC_TEMPLATE
        ).format(icon=icon, message=message)

    def set_autodelete(self, autodelete):
        self.notification.autodelete = autodelete
        
    def set_message(self, icon, message):
        self.notification.content = (
            strings.MESSAGE_GENERIC_TEMPLATE
        ).format(icon=icon, message=message)

    def set_page(self, page):
        self.notification.page = page

    def set_type(self, type):
        self.notification.type = type

    def save(self):
        self.notification.save()
    



def get_notifications(user, page) -> list:
    # if these aren't added to a list, they will be deleted after
    notifications_all = list(Notification.objects.filter(user=user, page=page))
    # purge auto-delete notifications
    Notification.objects.filter(autodelete=True).delete()
    return notifications_all


def purge_notification(notification_id) -> None:
    notification = Notification.objects.get(pk=notification_id)
    notification.delete()


def notify_winner(user, listing) -> None:
    listing_title = listing.title
    listing_url = reverse('view_listing', args=[listing.id])
    shopping_cart_url = reverse('shopping_cart')
    message = (strings.MESSAGE_NOTIFY_WINNER).format(
        listing_url=listing_url, listing_title=listing_title, 
        shopping_cart_url=shopping_cart_url)
    
    notification = NotificationTemplate()
    notification.build(
        user,
        TYPE_SUCCESS,
        ICON_SUCCESS,
        message,
        False,
        reverse('index')
    )
    notification.save()