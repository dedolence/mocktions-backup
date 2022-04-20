from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Notification, User, Listing, Order, Bid, Comment, Category, UserImage

admin.site.register(User, UserAdmin)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Notification)
admin.site.register(UserImage)
admin.site.register(Order)