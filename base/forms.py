from django.forms import ModelForm
from django import forms
from .models import Location, User, Profile

class LocationForm(ModelForm):
    class Meta:
        model = Location
        fields = '__all__'

class RegisterForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['username', 'password', 'email', 'description', 'photo']
        widgets = {
            'password': forms.PasswordInput(),
        }