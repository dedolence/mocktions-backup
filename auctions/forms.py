# Not going to use this after all, as I'd prefer writing the form manually to have better control over styles with Bootstrap

from django import forms
from .models import Listing, Comment


class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'image_url', 'starting_bid', 'shipping', 'category', 'lifespan']

class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'listing', 'replyTo', 'user']