from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from base.models import Profile

def user_is_organizer(view_func):
    def wrapper(request, *args, **kwargs):
        profile = Profile.objects.filter(user=request.user).first()
        if request.user.is_authenticated and profile:
            if profile.user_type == 'organizer':  
                return view_func(request, *args, **kwargs)
        messages.error(request, "Acces denied: You must have an organizer account in order to acces this part of the site.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return wrapper

def user_is_staff(view_func):
    def wrapper(request, *args, **kwargs):
        profile = Profile.objects.filter(user=request.user).first()
        if request.user.is_authenticated and profile:
            if profile.user_type == 'staff':
                return view_func(request, *args, **kwargs)
        messages.error(request, "Acces denied: You must have a staff account in order to acces this part of the site.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return wrapper

def user_is_guest(view_func):
    def wrapper(request, *args, **kwargs):
        profile = Profile.objects.filter(user=request.user).first()
        if request.user.is_authenticated and profile:
            if profile.user_type == 'guest':
                return view_func(request, *args, **kwargs)
        messages.error(request, "Acces denied: You must have a guest account in order to acces this part of the site.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return wrapper
