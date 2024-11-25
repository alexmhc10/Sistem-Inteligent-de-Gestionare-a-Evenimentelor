from django.contrib import admin

# Register your models here.


from .models import *

admin.site.register(Location)
admin.site.register(Task)
admin.site.register(Profile)
admin.site.register(Review)
admin.site.register(Type)
admin.site.register(Menu)
admin.site.register(EventMenu)
admin.site.register(Event)
admin.site.register(Guests)
admin.site.register(Message)