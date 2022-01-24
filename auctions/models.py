import math
import os
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE, PROTECT
from django.templatetags.static import static

from .globals import THUMBNAIL_SIZE
from PIL import Image
from django.core import files
from io import BytesIO


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
    default_image = static('auctions/images/user_avatar.png')
    watchlist = models.ManyToManyField('Listing', blank=True)
    profile_picture = models.CharField(max_length=100, default=default_image)
    street = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=100, blank=True)


# note: i was initially concerned about filename conflicts, but it looks like Django
# appends random characters to filenames if there is a conflict.
class User_Image(models.Model):
    owner = models.ForeignKey(User, on_delete=CASCADE, blank=True)
    listing = models.ForeignKey(Listing, on_delete=CASCADE, blank=True, null=True, related_name="images")
    image = models.ImageField(upload_to="%Y/%m/%d/", 
        width_field="pp_width", height_field="pp_height", blank=True)
    pp_width = models.IntegerField(blank=True, null=True)
    pp_height = models.IntegerField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to="%Y/%m/%d/", blank=True)

    # this method and make_thumbnail() originally from:
    # Bharat Chauhan https://bit.ly/3GDQOKS
    def save_thumbnail(self, *args, **kwargs):
        self.thumbnail = make_thumbnail(self.image)
        super().save(*args, **kwargs)



# //////////////////////////////////////////////////////
# UTILITY MODEL FUNCTIONS
# //////////////////////////////////////////////////////


def make_thumbnail(image, size=THUMBNAIL_SIZE):
    """ Format a thumbnail image for storage in DB. 
    This function and the corresponding model method are
    originally from Bharat Chauhan https://bit.ly/3GDQOKS
    """
    img_pil = Image.open(image)
    rgb_img = img_pil.convert("RGB")

    # crop to a square.
    width = rgb_img.size[0]
    height = rgb_img.size[1]
    if width != height:
        dif = abs(width-height)/2
        if width > height:
            (left, top, right, bottom) = (dif, 0, width-dif, height)
        else:
            (left, top, right, bottom) = (0, dif, width, height-dif)
        rgb_img = rgb_img.crop((left, top, right, bottom))
        
    rgb_img.thumbnail(size)
    thumb_io = BytesIO()
    rgb_img.save(thumb_io, "JPEG")
    thumb = files.images.ImageFile(thumb_io, name=image.name)
    return thumb