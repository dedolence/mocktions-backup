# Not going to use this after all, as I'd prefer writing the form manually to have better control over styles with Bootstrap

from django import forms
from .models import Listing, Comment, Image


class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'image_url', 'starting_bid', 'shipping', 'category', 'lifespan']


class NewImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(
                attrs={'class': 'form-control'}
            )
        }
        labels = {
            'image': 'Upload an image:'
        }