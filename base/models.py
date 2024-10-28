from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=100)
    #owner = 
    description= models.TextField(null=True, blank=True)
    #available_events =
    #reviewers = 
    gallery = models.ImageField(upload_to='images/', null=True, blank=True)
    location= models.TextField(max_length=100)

    def __str__(self):
        return self.name
