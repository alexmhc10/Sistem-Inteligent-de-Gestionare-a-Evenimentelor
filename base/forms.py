from django.forms import ModelForm
from django import forms
from .models import *
from django.contrib.auth.hashers import make_password
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title']
        labels = {
            'title': 'Task Nou',
        }

#pentru form
# class EventForm(forms.Form):
#     EVENT_TYPES = [
#         ('wedding', 'Nuntă'),
#         ('conference', 'Conferință'),
#         ('birthday', 'Petrecere aniversară'),
#         ('team-building', 'Team Building'),
#     ]
#     event_name = forms.CharField(max_length=100, required=True, label='Nume eveniment')
#     event_type = forms.ChoiceField(choices=EVENT_TYPES, required=True, label='Tip eveniment')
#     participants = forms.IntegerField(min_value=1, required=True, label='Număr estimat de participanți')
#     event_date = forms.DateField(required=True, label='Data preferată')
#     location = forms.ModelChoiceField(queryset=Location.objects.all(), required=True, label='Locație')
#     budget = forms.DecimalField(max_digits=10, decimal_places=2, required=True, label='Buget estimativ (€)')

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'event_name', 
            'event_date', 
            'event_time', 
            'event_description', 
            'location', 
            'guests'
        ]
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'event_time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
class LocationForm(ModelForm):
    custom_types = forms.CharField(
        max_length=200,
        required=False,
        label="Or write the types separated by commas"
    )

    class Meta:
        model = Location
        fields = ['name', 'description', 'gallery', 'location', 'seats_numbers', 'types']
        exclude = ['owner']

    def clean_custom_types(self):
        custom_types = self.cleaned_data.get('custom_types')
        if custom_types:
            return [type.strip() for type in custom_types.split(',')]
        return None



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
        profile.password = make_password(self.cleaned_data["password"])  
        if commit:
            profile.save()
        return profile
    
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body']
        widgets ={ 
            'body': forms.TextInput(attrs={'placeholder': 'Write a message...', 'class': 'message-input', 'maxlength': '300', 'autofocus': True })
        }