# Not going to use this after all, as I'd prefer writing the form manually to have better control over styles with Bootstrap

from xml.etree.ElementTree import Comment
from django import forms
from .models import Bid, Listing, User, UserImage, Category, Comment
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings

category_choices = [(c.id, c.content) for c in Category.objects.all()]
payment_card_choices = ['MasterCard', 'Visa', "American Express", 'Discover']

class BioForm(forms.ModelForm):

    first_name = forms.CharField(
        label="First name", 
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'First name'}
        )
    )

    last_name = forms.CharField(
        label="Last name", 
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Last name'}
        )
    )
    
    email = forms.CharField(
        label="Email address",
        max_length=100,
        required=False,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Email address'}
        )
    )
    
    phone = forms.CharField(
        label="Phone number", 
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Phone number'}
        )
    )

    street = forms.CharField(
        label="Street", 
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Street'}
        )
    )

    city = forms.CharField(
        label="City", 
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'City'}
        )
    )

    state = forms.CharField(
        label="State/Region/Province", 
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'State/Region/Province'}
        )
    )

    postcode = forms.CharField(
        label="Postal code", 
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Postal code'}
        )
    )

    country = forms.CharField(
        label="Country", 
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Country'}
        )
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'street',
            'city',
            'state',
            'postcode',
            'country',
            'phone'
            ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'listing', 'replyTo']
        labels = {
            'content': 'Leave a comment here'
        }
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'listing': forms.HiddenInput(attrs={'autocomplete': 'off'}),
            'replyTo': forms.HiddenInput(attrs={'autocomplete': 'off'})
        }


class CommentEditForm(CommentForm):
    comment_id = forms.CharField(widget=forms.HiddenInput(attrs={'autocomplete': 'off'}))


class CommentReplyForm(CommentForm):
    pass


class NewBidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount', 'listing', 'user']
        widgets = {
            'amount': forms.TextInput(
                attrs={
                        'class': 'form-control',
                        'aria-label': 'Amount (to the nearest dollar)'
                    }
            ),
            'listing': forms.HiddenInput(),
            'user': forms.HiddenInput()
        }


class NewImageForm(forms.ModelForm):
    image_url = forms.URLField(
        label="Or enter the URL of an image:",
        widget=forms.URLInput(
                attrs={'class': 'form-control'}
            ),
        required=False
        )

    random_image = forms.BooleanField(
        label="Or generate a random image:",
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        ),
        required=False
    )

    class Meta:
        model = UserImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(
                attrs={'class': 'form-control'}
            )
        }
        labels = {
            'image': 'Upload an image:'
        }


class NewListingCreateForm(forms.ModelForm):
    """For creating listing DRAFTS; i.e., no field is required."""
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'shipping', 'category', 'lifespan']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control'}),
            'shipping': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'lifespan': forms.NumberInput(attrs={'class': 'form-control'})
        }


class NewListingSubmitForm(forms.ModelForm):
    """For submitting listing drafts and creating active listings; i.e.,
    all fields will be required.
    """
    def __init__(self, *args, **kwargs):
        super(NewListingSubmitForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = True
    
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'shipping', 'category', 'lifespan']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control'}),
            'shipping': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'lifespan': forms.NumberInput(attrs={'class': 'form-control'})
        }


class RegistrationForm(UserCreationForm, BioForm):

    class Meta:
        model = User
        fields = [
            'username',
            'password1', 
            'password2',
            'first_name',
            'last_name',
            'email', 
            'street',
            'city',
            'state',
            'postcode',
            'country',
            'phone'
            ]
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    street = forms.CharField(
        label="Street", 
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Street'}
        )
    )

    city = forms.CharField(
        label="City", 
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'City'}
        )
    )

    state = forms.CharField(
        label="State/Region/Province", 
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'State/Region/Province'}
        )
    )

    postcode = forms.CharField(
        label="Postal code", 
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Postal code'}
        )
    )

    country = forms.CharField(
        label="Country", 
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Country'}
        )
    )