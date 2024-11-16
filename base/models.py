from django.db import models
from django.contrib.auth.models import User

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
    

class Guests(models.Model):
    firstname = models.CharField(max_length=20, unique=True)
    lastname = models.CharField(max_length=20, unique=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10)
    picture = models.ImageField(upload_to='poze_invitati/', null=True, blank=True)
    cuisine_preference = models.CharField(max_length=50, blank=True, null=True)
    allergens = models.JSONField(default=list)
    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Menu(models.Model):
    item_name = models.CharField(max_length=80)
    item_cuisine = models.CharField(max_length=20)
    item_vegan = models.BooleanField(default=False)
    allergens = models.JSONField(default=list)
    
    def __str__(self):
        return self.item_name