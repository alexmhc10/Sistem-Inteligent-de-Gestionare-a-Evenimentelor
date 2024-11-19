from django.contrib import admin

# Register your models here.


from .models import Location, Review, Type, Menu, Guests, EventMenu, Event

admin.site.register(Location)
admin.site.register(Review)
admin.site.register(Type)
admin.site.register(Menu)
admin.site.register(EventMenu)
admin.site.register(Event)
admin.site.register(Guests)