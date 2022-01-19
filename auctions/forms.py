# Not going to use this after all, as I'd prefer writing the form manually to have better control over styles with Bootstrap

from django import forms
from .models import Listing, Comment, User_Image


class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'image_url', 'starting_bid', 'shipping', 'category', 'lifespan']


class NewImageForm(forms.ModelForm):
    image_url = forms.URLField(
        label="Or enter the URL of an image:",
        widget=forms.URLInput(
                attrs={'class': 'form-control'}
            ),
        required=False
        )

    class Meta:
        model = User_Image
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(
                attrs={'class': 'form-control'}
            )
        }
        labels = {
            'image': 'Upload an image:'
        }
""" 
class NewImageForm(forms.Form):
    img_url = forms.URLField(
        label="Or enter the URL of an image:",
        required=False,
        widget=forms.URLInput(
                attrs={'class': 'form-control'}
            )
        )

    image = forms.ImageField(
        label="Upload an image",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control'}
        )
    ) """