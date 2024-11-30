from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

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

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128) 
    email = models.EmailField()
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    approved = models.BooleanField(default=False) 

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
    