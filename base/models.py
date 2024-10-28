from django.db import models
from django.contrib.auth.models import User


#Ne mai trebuie sau nu un class aici?


class Type(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Location(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    gallery = models.ImageField(upload_to='images/', null=True, blank=True)
    location = models.TextField(max_length=100)
    types = models.ManyToManyField(Type, blank=True)

    def __str__(self):
        return self.name




class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    comment = models.TextField()
    stars = models.IntegerField(choices=[(i, f"{i} stele") for i in range(1, 6)], default=5)

    def __str__(self):
        return self.comment[0:20]
    