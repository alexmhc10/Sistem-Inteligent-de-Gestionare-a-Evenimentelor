from django.forms import ModelForm
from django import forms
from .models import Location, User, Profile
from django.contrib.auth.hashers import make_password

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
    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.password = make_password(self.cleaned_data["password"])  # Securizează parola
        if commit:
            profile.save()
        return profile