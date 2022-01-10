from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE, PROTECT


class Bid(models.Model):
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=False) # max_digits includes decimal places!
    user = models.ForeignKey('User', on_delete=PROTECT, null=True)
    listing = models.ForeignKey('Listing', on_delete=CASCADE, null=True)
    def __str__(self):
        return f"Amount: {self.amount} by {self.user_id}"


class Category(models.Model):
    content = models.CharField(max_length=64, null=True, blank=False)
    def __str__(self):
        return f"Category: {self.content}"


class Comment(models.Model):
    content = models.TextField(max_length=200, null=True, blank=False)
    listing = models.ForeignKey('Listing', on_delete=CASCADE, blank=False, related_name="listings_comments")
    user = models.ForeignKey('User', on_delete=PROTECT, null=True, related_name="users_comments")
    replyTo = models.ForeignKey('Comment', on_delete=CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Listing(models.Model):
    image_url = models.CharField(max_length=200, null=True, blank=False)
    title = models.CharField(max_length=64, null=True, blank=False)
    description = models.TextField(max_length=500, null=True, blank=False)
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=False)
    shipping = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=False)
    owner = models.ForeignKey('User', on_delete=PROTECT, null=True)
    winner = models.ForeignKey('User', on_delete=PROTECT, related_name='won_listings', null=True, blank=True)
    winning_bid = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=CASCADE, null=True, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    active = models.BooleanField(default=True, null=False)
    lifespan = models.IntegerField(default=1, help_text="days until listing expires.")
    objects = models.Manager()

    def __str__(self) -> str:
        return "Listing: " + self.title


class Notification(models.Model):
    user = models.ForeignKey('User', on_delete=CASCADE, related_name="notifications")
    content = models.CharField(max_length=200, null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=50, blank=True, null=False, default='primary', 
        help_text='the Bootstrap alert type')
    autodelete = models.BooleanField(default=False, 
        help_text="True indicates the notification should be deleted as soon as it is rendered.")
    page = models.CharField(max_length=50, 
        default="index", 
        help_text="Defines on which page the notification should appear.")


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True)
    pass
