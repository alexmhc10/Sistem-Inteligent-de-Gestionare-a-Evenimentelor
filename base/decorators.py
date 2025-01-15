from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages

def user_is_organizer(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            if request.user.profile.user_type == 'organizer':  
                return view_func(request, *args, **kwargs)
        messages.error(request, "Acces interzis: Trebuie să fii organizator pentru a accesa această pagină.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return wrapper

def user_is_staff(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            if request.user.profile.user_type == 'staff':
                return view_func(request, *args, **kwargs)
        messages.error(request, "Acces interzis: Trebuie să fii staff pentru a accesa această pagină.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return wrapper

def user_is_guest(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            if request.user.profile.user_type == 'guest':
                return view_func(request, *args, **kwargs)
        messages.error(request, "Acces interzis: Trebuie să fii invitat pentru a accesa această pagină.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return wrapper
