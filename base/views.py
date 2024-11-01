from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login,logout
from .models import Location, Type
from .forms import LocationForm


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.warning(request, "User does not exist!")
            return render(request, 'base/login_register.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Error. Wrong credentials")

    context = {}
    return render(request, 'base/login_register.html', context)



def logoutPage(request):
    logout(request)
    return redirect('home')



def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    locations = Location.objects.filter(
        Q(types__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) | 
        Q(owner__username__icontains=q) |
        Q(location__icontains=q)
        )
    types = Type.objects.all()
    location_count = locations.count()
    context = {
        'locations' : locations,
        'types' : types,
        'location_count' : location_count
        }
    return render(request, 'base/home.html', context)


def location(request, pk):
    location = Location.objects.get(name=pk)
    context = {'location': location}
    return render(request, 'base/location.html', context)


def addLocation(request):
    form = LocationForm()
    if request.method == 'POST':
        form = LocationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {
        'form': form
    }
    return render(request, 'base/location_form.html', context)


def updateLocation(request, pk):
    location = Location.objects.get(name=pk)
    form = LocationForm(instance=location)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {
        'form': form,
    }
    return render(request, 'base/location_form.html', context)

def deleteLocation(request, pk):
    location = Location.objects.get(name=pk)
    if request.method == 'POST':
        location.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': location})

