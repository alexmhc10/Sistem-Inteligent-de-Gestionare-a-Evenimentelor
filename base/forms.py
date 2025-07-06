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
                'class': 'form-control event-input', 
                'placeholder': 'Select Date'
            }),
            'event_time': forms.TimeInput(attrs={
                'type': 'time', 
                'class': 'form-control event-input', 
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
    
    email = forms.EmailField(
        max_length=200,
        required=True,
        label="Staff Account Email",
        help_text="This email will be used for the location's staff account"
    )
    
    number = forms.CharField(
        max_length=20,
        required=True,
        label="Phone Number",
        initial="+(40) 74 83 64 823",
        help_text="This number will be used as the password for the staff account"
    )

    class Meta:
        model = Location
        fields = ['name', 'description', 'gallery', 'location', 'seats_numbers', 'types', 'email', 'number']
        exclude = ['owner', 'user_account']

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
        fields = ['username', 'password', 'email', 'description', 'photo', 'cv_file', 'first_name', 'last_name']
        widgets = {
            'password': forms.PasswordInput(),
        }
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].required = True
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


class EventGalleryUploadForm(forms.ModelForm):
    class Meta:
        model = EventGallery
        fields = ['archive']

    def clean_archive(self):
        file = self.cleaned_data.get('archive')
        if file:
            if not file.name.endswith('.zip'):
                raise forms.ValidationError("Fișierul trebuie să fie o arhivă ZIP sau RAR.")
            if file.size > 100 * 1024 * 1024:
                raise forms.ValidationError("Arhiva nu trebuie să depășească 100MB.")
        return file


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        exclude = ['location']

    def __init__(self, *args, **kwargs):
        
        super(TableForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

from django import forms
from .models import Event, Guests, Profile, TableGroup, Allergen, User
from django.contrib.auth.models import User

class ComprehensiveGuestForm(forms.ModelForm):
    """
    Formular comprehensiv pentru invitați care respectă toate caracteristicile
    algoritmului inteligent de aranjare a meselor
    """
    
    first_name = forms.CharField(
        max_length=50,
        label="Prenume",
        help_text="Prenumele invitatului",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ex: Maria'
        })
    )
    
    last_name = forms.CharField(
        max_length=50,
        label="Nume de familie",
        help_text="Numele de familie al invitatului",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ex: Popescu'
        })
    )
    
    age = forms.IntegerField(
        min_value=1,
        max_value=120,
        label="Vârsta",
        help_text="Vârsta invitatului (importantă pentru aranjarea pe grupe de vârstă)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '25'
        })
    )
    
    gender = forms.ChoiceField(
        choices=Guests.GENDER_CHOICES,
        label="Gen",
        help_text="Genul invitatului",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    email = forms.EmailField(
        label="Email",
        help_text="Adresa de email pentru invitații și confirmări",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'maria.popescu@email.com'
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        label="Telefon",
        help_text="Numărul de telefon pentru contact",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+40 123 456 789'
        })
    )
    
    cuisine_preference = forms.ChoiceField(
        choices=REGION_CHOICES,
        required=False,
        label="Preferințe culinare",
        help_text="Algoritmul va grupa invitații cu preferințe similare",
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    
    vegan = forms.BooleanField(
        required=False,
        label="Dietă vegană",
        help_text="Invitatul urmează o dietă vegană",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    allergens = forms.ModelMultipleChoiceField(
        queryset=Allergen.objects.all(),
        required=False,
        label="Alergii alimentare",
        help_text="Selectează toate alergiile invitatului (important pentru aranjarea la mese)",
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    relationship_to_couple = forms.ChoiceField(
        choices=[
            ('bride_family', 'Familia miresei'),
            ('groom_family', 'Familia mirelui'),
            ('bride_friends', 'Prieteni ai miresei'),
            ('groom_friends', 'Prieteni ai mirelui'),
            ('work_colleagues', 'Colegi de serviciu'),
            ('university_friends', 'Prieteni din facultate'),
            ('neighbors', 'Vecini'),
            ('other', 'Altele'),
        ],
        label="Relația cu cuplul",
        help_text="Algoritmul va grupa persoanele cu relații similare",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    social_group_priority = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=5,
        label="Prioritate socială",
        help_text="1 = prioritate scăzută, 10 = prioritate înaltă (familie apropiată)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '10'
        })
    )
    
    preferred_companions = forms.CharField(
        max_length=200,
        required=False,
        label="Invitați preferați la aceeași masă",
        help_text="Nume separate prin virgulă (ex: Ion Popescu, Maria Ionescu)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ion Popescu, Maria Ionescu'
        })
    )
    
    avoid_companions = forms.CharField(
        max_length=200,
        required=False,
        label="Invitați de evitat",
        help_text="Persoane cu care invitatul preferă să nu stea la aceeași masă",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Numele persoanelor de evitat'
        })
    )
    
    mobility_needs = forms.BooleanField(
        required=False,
        label="Nevoi de mobilitate",
        help_text="Invitatul are nevoie de acces facil (scaun cu rotile, baston, etc.)",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    elderly_companion = forms.BooleanField(
        required=False,
        label="Însoțitor în vârstă",
        help_text="Invitatul vine cu o persoană în vârstă care necesită atenție specială",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    children_accompanying = forms.IntegerField(
        min_value=0,
        max_value=10,
        initial=0,
        required=False,
        label="Număr copii însoțitori",
        help_text="Numărul de copii care îl însoțesc (important pentru mărimea mesei)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'max': '10'
        })
    )
    
    personality_type = forms.ChoiceField(
        choices=[
            ('extrovert', 'Extrovert - îi place să socializeze'),
            ('introvert', 'Introvert - preferă grupuri mici'),
            ('mixed', 'Mixt - depinde de situație'),
        ],
        label="Tipul de personalitate",
        help_text="Algoritmul va echilibra mesele între extroverte și introverte",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    conversation_topics = forms.MultipleChoiceField(
        choices=[
            ('work', 'Muncă și carieră'),
            ('sports', 'Sport'),
            ('travel', 'Călătorii'),
            ('food', 'Gastronomie'),
            ('family', 'Familie'),
            ('music', 'Muzică'),
            ('movies', 'Filme'),
            ('books', 'Cărți'),
            ('technology', 'Tehnologie'),
            ('art', 'Artă'),
        ],
        required=False,
        label="Subiecte preferate de conversație",
        help_text="Algoritmul va grupa persoane cu interese comune",
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    arrival_time = forms.ChoiceField(
        choices=[
            ('early', 'Timpuriu (cu 30+ min înainte)'),
            ('on_time', 'La timp'),
            ('fashionably_late', 'Cu întârziere elegantă (10-15 min)'),
        ],
        label="Obiceiuri de sosire",
        help_text="Pentru organizarea locurilor și a momentului serviri",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    plus_one = forms.BooleanField(
        required=False,
        label="Vine cu +1",
        help_text="Invitatul va veni însoțit de o altă persoană",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    plus_one_name = forms.CharField(
        max_length=100,
        required=False,
        label="Numele însoțitorului (+1)",
        help_text="Numele persoanei care îl însoțește",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Numele însoțitorului'
        })
    )
    
    special_notes = forms.CharField(
        max_length=500,
        required=False,
        label="Notițe speciale",
        help_text="Orice informații suplimentare importante pentru aranjarea la mese",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'ex: Nu poate sta cu spatele la fereastră din cauza alergiei la lumină'
        })
    )
    
    class Meta:
        model = Guests
        fields = ['gender', 'cuisine_preference', 'vegan', 'allergens']
    
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        
        if self.event:
            pass
    
    def save(self, commit=True):
        guest = super().save(commit=False)
        
        if commit:
            profile = Profile.objects.create(
                username=f"{self.cleaned_data['first_name'].lower()}_{self.cleaned_data['last_name'].lower()}",
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                age=self.cleaned_data['age'],
                number=self.cleaned_data['phone'],
                user_type='guest',
                approved=True
            )
            
            guest.profile = profile
            guest.age = self.cleaned_data['age']
            guest.save()
            
            self.save_m2m()
            
            self._assign_to_social_group(guest)
        
        return guest
    
    def _assign_to_social_group(self, guest):
        if not self.event:
            return
        
        relationship = self.cleaned_data['relationship_to_couple']
        priority = self.cleaned_data['social_group_priority']
        
        group_mapping = {
            'bride_family': 'Familia Miresei',
            'groom_family': 'Familia Mirelui', 
            'bride_friends': 'Prietenii Miresei',
            'groom_friends': 'Prietenii Mirelui',
            'work_colleagues': 'Colegi de Serviciu',
            'university_friends': 'Prieteni din Facultate',
            'neighbors': 'Vecini și Cunoscuți',
            'other': 'Alți Invitați',
        }
        
        group_name = group_mapping.get(relationship, 'Alți Invitați')
        
        group, created = TableGroup.objects.get_or_create(
            event=self.event,
            name=group_name,
            defaults={
                'priority': priority,
                'notes': f'Grup automat creat pentru {group_name}'
            }
        )
        
        group.guests.add(guest)

class GuestSelfRegistrationForm(forms.ModelForm):

    first_name = forms.CharField(
        max_length=50,
        label="Prenumele tău",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ex: Maria'
        })
    )
    
    last_name = forms.CharField(
        max_length=50,
        label="Numele tău de familie",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ex: Popescu'
        })
    )
    
    age = forms.IntegerField(
        min_value=1,
        max_value=120,
        label="Vârsta ta",
        help_text="Ne ajută să aranjăm mesele cu persoane de vârste apropiate",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '25'
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        label="Numărul tău de telefon",
        help_text="Pentru contact în ziua evenimentului",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+40 123 456 789'
        })
    )
    
    relationship_to_couple = forms.ChoiceField(
        choices=[
            ('bride_family', 'Sunt din familia miresei'),
            ('groom_family', 'Sunt din familia mirelui'),
            ('bride_close_friend', 'Sunt prieten apropiat al miresei'),
            ('groom_close_friend', 'Sunt prieten apropiat al mirelui'),
            ('mutual_friend', 'Suntem prieteni cu amândoi'),
            ('work_colleague', 'Suntem colegi de serviciu'),
            ('university_friend', 'Ne cunoaștem din facultate'),
            ('neighbor', 'Suntem vecini'),
            ('family_friend', 'Sunt prieten al familiei'),
            ('other', 'Altă relație'),
        ],
        label="Cum îi cunoști pe Ana și Florin?",
        help_text="Ne ajută să te așezăm lângă persoane pe care le cunoști",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    how_close = forms.ChoiceField(
        choices=[
            ('very_close', 'Suntem foarte apropiați (familie, prieteni cei mai buni)'),
            ('close', 'Suntem apropiați (prieteni buni)'),
            ('acquaintance', 'Ne cunoaștem bine (colegi, cunoscuți)'),
            ('distant', 'Ne cunoaștem mai puțin (prieteni comuni, distant)'),
        ],
        label="Cât de apropiați sunteți?",
        help_text="Pentru a te așeza în apropierea persoanelor potrivite",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    cuisine_preference = forms.ChoiceField(
        choices=[
            ('romanian', 'Mâncare românească tradițională'),
            ('italian', 'Mâncare italiană'),
            ('french', 'Mâncare franceză'),
            ('mediterranean', 'Mâncare mediteraneană'),
            ('international', 'Mâncare internațională'),
            ('modern', 'Bucătărie modernă/fusion'),
            ('no_preference', 'Nu am preferințe speciale'),
        ],
        required=False,
        label="Ce tip de mâncare îți place cel mai mult?",
        help_text="Pentru a te așeza cu persoane cu gusturi similare",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    vegan = forms.BooleanField(
        required=False,
        label="Urmez o dietă vegană",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    vegetarian = forms.BooleanField(
        required=False,
        label="Sunt vegetarian/ă",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    allergens = forms.ModelMultipleChoiceField(
        queryset=Allergen.objects.all(),
        required=False,
        label="Am următoarele alergii alimentare:",
        help_text="Important pentru siguranța ta și aranjarea mesei",
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    plus_one = forms.BooleanField(
        required=False,
        label="Vin însoțit/ă de o persoană (+1)",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    plus_one_name = forms.CharField(
        max_length=100,
        required=False,
        label="Numele persoanei care mă însoțește",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Numele complet al însoțitorului'
        })
    )
    
    children_with_me = forms.IntegerField(
        min_value=0,
        max_value=5,
        initial=0,
        required=False,
        label="Câți copii vin cu mine?",
        help_text="Pentru a rezerva spațiul potrivit la masă",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'max': '5'
        })
    )
    
    social_personality = forms.ChoiceField(
        choices=[
            ('very_social', 'Îmi place să cunosc oameni noi și să socializez mult'),
            ('social', 'Îmi place să stau de vorbă, dar nu sunt foarte extrovert'),
            ('quiet', 'Prefer conversații mai liniștite în grupuri mici'),
            ('depends', 'Depinde de oameni și de atmosferă'),
        ],
        label="Cum ești la evenimente sociale?",
        help_text="Pentru a crea o atmosferă plăcută la masa ta",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    preferred_table_companions = forms.CharField(
        max_length=200,
        required=False,
        label="Există persoane cu care ți-ar plăcea să stai la masă?",
        help_text="Scrie numele lor separate prin virgulă (ex: Ion Popescu, Maria Ionescu)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Numele persoanelor preferate (opțional)'
        })
    )
    
    mobility_assistance = forms.BooleanField(
        required=False,
        label="Am nevoie de o masă cu acces facil (scaun cu rotile, baston, etc.)",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    elderly_person_with_me = forms.BooleanField(
        required=False,
        label="Vin cu o persoană în vârstă care are nevoie de atenție specială",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    arrival_style = forms.ChoiceField(
        choices=[
            ('early', 'De obicei ajung puțin mai devreme'),
            ('on_time', 'Ajung întotdeauna la timp'),
            ('fashionably_late', 'Ajung de obicei cu câteva minute întârziere'),
        ],
        label="Cum ajungi de obicei la evenimente?",
        help_text="Pentru organizarea locurilor și servirea mesei",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    special_requests = forms.CharField(
        max_length=300,
        required=False,
        label="Alte cerințe sau informații importante",
        help_text="Orice altceva ce ar trebui să știm pentru confortul tău",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'ex: Nu pot sta cu spatele la fereastră, prefer să stau aproape de ieșire, etc.'
        })
    )
    
    dietary_notes = forms.CharField(
        max_length=200,
        required=False,
        label="Alte preferințe sau restricții alimentare",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'ex: fără lactate, fără gluten, nu mănânc carne roșie, etc.'
        })
    )
    
    class Meta:
        model = Guests
        fields = ['gender', 'cuisine_preference', 'vegan', 'allergens']
    
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        
        if self.event:
            couple_names = getattr(self.event, 'couple_names', 'miri')
            self.fields['relationship_to_couple'].help_text = f"Ne ajută să te așezăm lângă persoane pe care le cunoști"
    
    def clean(self):
        cleaned_data = super().clean()
        
        plus_one = cleaned_data.get('plus_one')
        plus_one_name = cleaned_data.get('plus_one_name')
        
        if plus_one and not plus_one_name:
            raise forms.ValidationError("Te rugăm să introduci numele persoanei care te însoțește.")
        
        return cleaned_data
    
    def save(self, commit=True):
        guest = super().save(commit=False)
        
        if commit:
            profile = Profile.objects.create(
                username=f"{self.cleaned_data['first_name'].lower()}_{self.cleaned_data['last_name'].lower()}",
                email=self.cleaned_data.get('email', f"{self.cleaned_data['first_name'].lower()}@temp.com"),
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                age=self.cleaned_data['age'],
                number=self.cleaned_data['phone'],
                user_type='guest',
                approved=True
            )
            
            guest.profile = profile
            guest.age = self.cleaned_data['age']
            guest.save()
            
            self.save_m2m()
            
            priority = self._calculate_priority()
            
            self._assign_to_social_group(guest, priority)
        
        return guest
    
    def _calculate_priority(self):
        relationship = self.cleaned_data['relationship_to_couple']
        closeness = self.cleaned_data['how_close']
        
        relationship_priority = {
            'bride_family': 10,
            'groom_family': 10,
            'bride_close_friend': 8,
            'groom_close_friend': 8,
            'mutual_friend': 7,
            'work_colleague': 6,
            'university_friend': 6,
            'family_friend': 7,
            'neighbor': 5,
            'other': 4,
        }
        
        closeness_modifier = {
            'very_close': 1,
            'close': 0,
            'acquaintance': -1,
            'distant': -2,
        }
        
        base_priority = relationship_priority.get(relationship, 5)
        modifier = closeness_modifier.get(closeness, 0)
        
        return max(1, min(10, base_priority + modifier))
    
    def _assign_to_social_group(self, guest, priority):
        if not self.event:
            return
        
        relationship = self.cleaned_data['relationship_to_couple']
        
        group_mapping = {
            'bride_family': 'Familia Miresei',
            'groom_family': 'Familia Mirelui',
            'bride_close_friend': 'Prietenii Apropiați ai Miresei',
            'groom_close_friend': 'Prietenii Apropiați ai Mirelui',
            'mutual_friend': 'Prieteni Comuni',
            'work_colleague': 'Colegi de Serviciu',
            'university_friend': 'Prieteni din Facultate',
            'family_friend': 'Prieteni ai Familiei',
            'neighbor': 'Vecini și Cunoscuți',
            'other': 'Alți Invitați',
        }
        
        group_name = group_mapping.get(relationship, 'Alți Invitați')
        
        group, created = TableGroup.objects.get_or_create(
            event=self.event,
            name=group_name,
            defaults={
                'priority': priority,
                'notes': f'Grup creat din înregistrările invitaților'
            }
        )
        
        group.guests.add(guest)