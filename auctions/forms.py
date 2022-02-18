# Not going to use this after all, as I'd prefer writing the form manually to have better control over styles with Bootstrap

from django import forms
from .models import Listing, UserImage, Category


category_choices = [(c.id, c.content) for c in Category.objects.all()]

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


class NewListingSubmitForm(forms.Form):
    """For submitting listing drafts and creating active listings; i.e.,
    all fields will be required.
    """
    title = forms.CharField(max_length=64, required=True)
    description = forms.CharField(max_length=500, required=True)
    starting_bid = forms.DecimalField(max_digits=8, decimal_places=2, required=True)
    shipping = forms.DecimalField(max_digits=6, decimal_places=2, required=True)
    category = forms.ChoiceField(choices=category_choices, required=True)
    lifespan = forms.IntegerField(max_value=30, required=True)
    

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

class RegistrationForm(forms.Form):
    username = forms.CharField(
        label="Username", 
        max_length=50,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Username'}
        )
    )

    email = forms.EmailField(
        label="Email address", 
        max_length=100,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Email address'}
        )
    )

    password = forms.CharField(
        label="Password", 
        max_length=50,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password'}
        )
    )

    confirm_password = forms.CharField(
        label="Confirm your password",
        max_length=50,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Confirm your password'}
        )
    )


class ContactForm(forms.Form):
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


class ShippingInformation(forms.Form):
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