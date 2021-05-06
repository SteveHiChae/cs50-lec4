from django.forms import ModelForm
from django import forms

from .models import *


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('title', 'category', 'description', 'price', 'photo',
            'active_listing', 'watchlist', 'starting_bid')

        widgets = { 
            'description': forms.TextInput(attrs={'class': 'description'}),
            'watchlist': forms.HiddenInput(),
        }