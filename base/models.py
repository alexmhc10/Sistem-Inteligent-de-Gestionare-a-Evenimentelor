from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.utils import timezone

#model pentru noua baza de date
class EventHistory(models.Model):
    event_name = models.CharField(max_length=255)
    event_date = models.DateTimeField()
    event_time = models.TimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    organized_by = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Marcare pentru evenimente șterse

    def __str__(self):
        return f"{self.event_name} on {self.event_date}"

    class Meta:
        verbose_name = 'Event History'
        verbose_name_plural = 'Event Histories'


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
class Type(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Location(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    gallery = models.ImageField(upload_to='images/', null=True, blank=True)
    location = models.TextField(max_length=30)
    types = models.ManyToManyField(Type, blank=True)
    seats_numbers = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cost = models.IntegerField(default=3000)
    number = models.CharField(max_length=20, default="+(40) 74 83 64 823")
    def __str__(self):
        return self.name


from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class PersonalLocationManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class PersonalLocation(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    location = models.ForeignKey('Location', on_delete=models.CASCADE, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = PersonalLocationManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128) 
    email = models.EmailField()
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    approved = models.BooleanField(default=False)
    number = models.CharField(max_length=15,default="+(40) 748364823")
    age = models.IntegerField(default=20)
    def __str__(self):
        return self.user.username



class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    comment = models.TextField()
    stars = models.IntegerField(choices=[(i, f"{i} stele") for i in range(1, 6)], default=5)

    def __str__(self):
        return self.comment[0:20]
    

# class Guests(models.Model):
#     firstname = models.CharField(max_length=20, unique=True)
#     lastname = models.CharField(max_length=20, unique=True)
#     email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
#     age = models.IntegerField(null=True, blank=True)
    # gender = models.CharField(max_length=10)
#     picture = models.ImageField(upload_to='poze_invitati/', null=True, blank=True)
#     cuisine_preference = models.CharField(max_length=50, blank=True, null=True)
#     vegan = models.BooleanField(default=False)
    # allergens = models.JSONField(default=list, blank=True, null=True)
#     def __str__(self):
#         return f"{self.firstname} {self.lastname}"

class Guests(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Feminin')
        ]
    firstname = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    picture = models.ImageField(upload_to='poze_invitati/', null=True, blank=True)
    cuisine_preference = models.CharField(max_length=50, blank=True, null=True)
    vegan = models.BooleanField(default=False)
    allergens = models.JSONField(default=list, blank=True, null=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
    
class Menu(models.Model):
    item_name = models.CharField(max_length=80)
    item_cuisine = models.CharField(max_length=20)
    item_vegan = models.BooleanField(default=False)
    allergens = models.JSONField(default=list, blank=True, null=True)
    item_picture = models.ImageField(upload_to='menu_items/', null=True, blank=True)
    def __str__(self):
        return self.item_name    
    

class Event(models.Model):
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    event_name = models.CharField(max_length=100)
    event_date = models.DateField()
    event_time = models.TimeField()
    event_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    guests = models.ManyToManyField(Guests, related_name='events', blank=True)
    completed = models.BooleanField(default=False) 
    types = models.ManyToManyField(Type, blank=True)
    cost = models.IntegerField(default= 3000)
    updated_at = models.DateTimeField(auto_now=True)
    organized_by = models.ForeignKey(
            User,
            on_delete=models.CASCADE, 
            related_name="organized_events",
            blank=True,
            null=True
        )
    def clean(self):
        if self.organized_by and self.organized_by.is_superuser:
            raise ValidationError("Superuser-ul nu poate organiza evenimente.")
    def __str__(self):
        return self.event_name

    def check_completed(self):
        if self.event_date <= now().date():
            self.completed = True
            self.save()
            

class EventMenu(models.Model):
    event = models.ForeignKey(Event, related_name='menus', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=80)
    item_cuisine = models.CharField(max_length=20)
    item_vegan = models.BooleanField(default=False)
    allergens = models.JSONField(default=list, blank=True, null=True)
    item_picture = models.ImageField(upload_to='event_menus/', null=True, blank=True)

    def __str__(self):
        return self.item_name


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username}: {self.body}'
    
    class Meta:
        ordering = ['-created']
    
