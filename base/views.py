from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login,logout
from .models import Location, Type, Profile, User, Review
from .forms import LocationForm, ProfileForm
from django.conf import settings


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
            profile = form.save(commit=False)  
            profile.approved = False
            profile.save()
            messages.success(request, "Profile submitted for approval.")
            return redirect('login')
    context = {'form': form, 'page': 'register'}
    return render(request, 'base/login_register.html', context)

@login_required(login_url='login')
def approve_user(request, pk):
    if not request.user.is_superuser:
        return HttpResponse("Only superusers can approve users.")
    
    profile = Profile.objects.get(id=pk)
    if request.method == 'POST':
        if 'approve' in request.POST:
            # Creează utilizatorul abia acum
            user = User.objects.create_user(
                username=profile.username,
                password=profile.password,
                email=profile.email
            )
            profile.user = user 
            profile.approved = True
            profile.save()
            messages.success(request, f"User {profile.username} has been approved.")
        elif 'reject' in request.POST:
            profile.delete()
            messages.warning(request, f"User {profile.username} has been rejected.")
        return redirect('new_users')
    return render(request, 'base/approve_user.html', {'profile': profile})


@login_required(login_url='login')
def new_users(request):
    if not request.user.is_superuser:
        return HttpResponse("Only superusers can approve users.")
    
    profiles = Profile.objects.filter(approved=False)
    return render(request, 'base/new_users.html', {'profiles': profiles})



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
        ).distinct()
    users = User.objects.all()
    types = Type.objects.all()
    location_count = locations.count()
    profiles = Profile.objects.filter(approved=True)
    context = {
        'users' : users,
        'locations' : locations,
        'types' : types,
        'location_count' : location_count,
        'profiles' : profiles
        }
    return render(request, 'base/home.html', context)


@login_required(login_url='/login')
def profilePage(request, username):
    profile = Profile.objects.get(user__username=username)
    return render(request, 'base/profiles.html', {'profile': profile})

def location(request, pk):
    location = Location.objects.get(name=pk)
    reviews = location.review_set.all()
    if request.method == 'POST':
        review = Review.objects.create(
            user = request.user,
            location = location,
            comment = request.POST.get('comment'),
            stars = request.POST.get('rating')
        )
        return redirect('location', pk=location.name)
    star_range = range(1, 6)
    context = {
        'location': location,
        'star_range': star_range,
        'reviews': reviews,
    }
    return render(request, 'base/location.html', context)



@login_required(login_url='/login')
def addLocation(request):
    form = LocationForm()
    types = Type.objects.all()
    
    if request.method == 'POST':
        form = LocationForm(request.POST, request.FILES)
        if form.is_valid():
            # Prevenirea duplicării locației
            location = form.save(commit=False)
            location.owner = request.user  # Atribuie utilizatorul
            location.save()  # Salvează locația înainte de a adăuga tipurile

            custom_types = form.cleaned_data.get('custom_types')
            if custom_types:  # Dacă există tipuri personalizate
                for type_name in custom_types:
                    type_instance, created = Type.objects.get_or_create(name=type_name.strip())  # Crează sau obține tipul
                    if type_instance not in location.types.all():  # Verifică dacă tipul nu a fost deja adăugat
                        location.types.add(type_instance)  # Adaugă tipul la locație
            else:
                # Dacă nu sunt tipuri personalizate, folosim tipurile selectate din formular
                selected_types = form.cleaned_data.get('types')
                for type_instance in selected_types:
                    if type_instance not in location.types.all():  # Verifică dacă tipul nu a fost deja adăugat
                        location.types.add(type_instance)  # Adaugă tipul la locație

            # Logare pentru a verifica
        print(f"Redirecting to home with location: {location.name} and types: {location.types.all()}")
        return redirect('home')
    context = {
        'form': form,
        'types': types
    }
    return render(request, 'base/location_form.html', context)




@login_required(login_url='/login')
def updateLocation(request, pk):
    location = Location.objects.get(name=pk)
    form = LocationForm(instance=location)
    types = Type.objects.all()     
    if request.user != location.owner:
        return HttpResponse("You don't have permission over this room.")
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {
        'form': form,
        'types': types
    }
    return render(request, 'base/location_form.html', context)




@login_required(login_url='/login')
def deleteLocation(request, pk):
    location = Location.objects.get(name=pk)
    if request.method == 'POST':
        location.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {
        'obj': location})


@login_required(login_url='/login')
def deleteReview(request, pk):
    review = Review.objects.get(id=pk)
    location_name = review.location.name
    if request.method == 'POST':
        review.delete()
        return redirect('location', pk=location_name)
    return render(request, 'base/delete.html', {
        'obj': review})
