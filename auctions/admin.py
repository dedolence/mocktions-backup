from django.contrib import admin
from .models import Notification, User, Listing, Bid, Comment, Category, User_Image

# Register your models here.
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Notification)
admin.site.register(User_Image)