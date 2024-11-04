from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login,logout
from .models import Location, Type, Profile
from .forms import LocationForm, ProfileForm


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
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

    context = {'page' : page}
    return render(request, 'base/login_register.html', context)



def registerPage(request):
    form = ProfileForm()
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile submitted for approval.")
            return redirect('login')
    context = {'form': form, 'page': 'register'}
    return render(request, 'base/login_register.html', context)

@login_required(login_url='login')
def new_users(request):
    if not request.user.is_superuser:
        return HttpResponse("Only superusers can approve users.")
    
    profiles = Profile.objects.filter(approved=False)
    return render(request, 'base/new_users.html', {'profiles': profiles})

@login_required(login_url='login')
def approve_user(request, pk):
    if not request.user.is_superuser:
        return HttpResponse("Only superusers can approve users.")
    
    profile = Profile.objects.get(id=pk)
    if request.method == 'POST':
        if 'approve' in request.POST:
            user = User.objects.create_user(username=profile.username, password=profile.password, email=profile.email)
            profile.approved = True
            profile.save()
            messages.success(request, f"User {profile.username} has been approved.")
        elif 'reject' in request.POST:
            profile.delete()
            messages.warning(request, f"User {profile.username} has been rejected.")
        return redirect('new_users')
    return render(request, 'base/approve_user.html', {'profile': profile})


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


@login_required(login_url='/login')
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

@login_required(login_url='/login')
def updateLocation(request, pk):
    location = Location.objects.get(name=pk)
    form = LocationForm(instance=location)
    if request.user != location.owner:
        return HttpResponse("You don't have permission over this room.")
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {
        'form': form,
    }
    return render(request, 'base/location_form.html', context)

@login_required(login_url='/login')
def deleteLocation(request, pk):
    location = Location.objects.get(name=pk)
    if request.method == 'POST':
        location.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': location})

