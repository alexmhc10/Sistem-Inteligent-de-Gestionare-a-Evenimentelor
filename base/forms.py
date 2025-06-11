from django.forms import ModelForm
from django import forms
from .models import *
from django.contrib.auth.hashers import make_password
from .models import Task
from django.contrib.auth.forms import UserChangeForm
from .models import Profile
from django.core.validators import FileExtensionValidator


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['email', 'number', 'age', 'location', 'street', 'zip_code', 'country', 'facebook', 'work_link', 'google_link', 'photo', 'description']


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

from django import forms
from .models import Event
from django.contrib.auth.models import User

from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'event_name', 
            'event_date', 
            'event_time', 
            'event_description', 
            'location', 
            'guests',
        ]  

    widgets = {
            'event_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control event-input',  # Adăugăm clasele pentru stilizare
                'placeholder': 'Select Date'
            }),
            'event_time': forms.TimeInput(attrs={
                'type': 'time', 
                'class': 'form-control event-input',  # Adăugăm clasele pentru stilizare
                'placeholder': 'Select Time'
            }),
            'event_description': forms.Textarea(attrs={
                'class': 'form-control event-input',
                'rows': 4,
                'placeholder': 'Describe the event'
            }),
            'location': forms.Select(attrs={
                'class': 'form-select event-input',
            }),
        }


class UploadFileForm(forms.Form):
    guest_file = forms.FileField(label="Alege un fișier CSV/XLSX")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'}) 


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']


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

class LocationEventTypesForm(forms.ModelForm):
    types = forms.ModelMultipleChoiceField(
        queryset=Type.objects.all(),
        widget=forms.SelectMultiple,
        required=False
    )
    class Meta:
        model = Location
        fields = ['types']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'}) 

        if self.instance and self.instance.pk:
            self.fields['types'].initial = self.instance.types.all()


ALLERGEN_CHOICES = [
    ("gluten", "Gluten"),
    ("lactose", "Lactoză"),
    ("nuts", "Nuci"),
    ("eggs", "Ouă"),
    ("fish", "Pește"),
]

class FoodSearchForm(forms.Form):
    query = forms.CharField(required=False, label="Caută feluri de mâncare")
    vegetarian = forms.BooleanField(required=False, label="Doar vegetariene")
    allergens = forms.MultipleChoiceField(
        choices=ALLERGEN_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'}) 


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class EventPostForm(forms.ModelForm):
    rating = forms.IntegerField(
        widget=forms.HiddenInput(),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    images = MultipleFileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])],
        help_text="Select maximum 10 images.",
    )

    class Meta:
        model = EventPost
        fields = ['title', 'content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Write a message...'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Title'
            })
        }
        labels = {
            'title': 'Title',
            'content': 'Content'
        }

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_images(self):
            images = self.files.getlist('images')
            if len(images) > 10:
                raise forms.ValidationError("Puteți încărca maxim 10 imagini.")
            return images


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        exclude = ['location']

    def __init__(self, *args, **kwargs):
        
        super(TableForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'