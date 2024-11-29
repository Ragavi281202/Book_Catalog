from django import forms
from .models import BookCatalog,Review,Rating
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class AddBookForm(forms.ModelForm):
    class Meta:
        model = BookCatalog
        fields = ['book_id', 'cover_image_url', 'book_title', 'book_details', 'publication_info', 
                  'authorlink', 'author', 'num_pages', 'genres', 'num_ratings', 'num_reviews', 
                  'average_rating', 'rating_distribution', 'image_url']


class UpdateBookForm(forms.ModelForm):
    book_id = forms.CharField(max_length=15, required=True, widget=forms.HiddenInput())  # Define book_id as a hidden field

    class Meta:
        model = BookCatalog
        fields = ['num_pages', 'num_ratings']

class RemoveBookForm(forms.Form):
    book_id = forms.CharField(max_length=15)

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['username'].help_text=None

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label=("Password"), strip=False, widget=forms.PasswordInput)

