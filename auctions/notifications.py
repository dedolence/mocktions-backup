from django.db.models.query import QuerySet
from . import strings
from .models import Notification
from django.urls import reverse


def generate_notification(user, type, icon, message, autodelete=False, page="index") -> Notification:
    """Generate and return an alert box. 'Type' and 'icon' are string values
    corresponding to the Bootstrap 5.0 'alert-' and 'bi-' classes. 'Page'
    is the view on which the notification should appear, defaults to index.
    """
    content = (strings.MESSAGE_GENERIC).format(icon=icon, message=message)
    notification = Notification.objects.create(
        user=user, 
        content=content, 
        type=type, 
        autodelete=autodelete,
        page=page)
    notification.save()
    return notification


def get_notifications(user, page) -> list:
    # if these aren't added to a list, they will be deleted after
    notifications_all = [i for i in Notification.objects.filter(user=user, page=page)]
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
    generate_notification(user, 'success', 'none', message)


