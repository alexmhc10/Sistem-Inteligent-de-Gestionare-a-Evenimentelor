from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login,logout
from .models import *
from .forms import *
from django.conf import settings
from collections import Counter, defaultdict
import json

def loginPage(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.warning(request, "User does not exist!")
            return render(request, 'base/login_register.html', {'page': page})
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print(f"User is authenticated: {user.username}")
            print(f"Is superuser: {user.is_superuser}")

            if user.is_superuser:
                return redirect('home-admin')
            else:
                return redirect('home')
        else:
            messages.error(request, "Error. Wrong credentials")
            return render(request, 'base/login_register.html', {'page': page})
    if request.user.is_authenticated:
        print(f"User is authenticated: {request.user.username}")
        print(f"Is superuser: {request.user.is_superuser}")
        if request.user.is_superuser:
            return redirect('menu-items')
        else:
            return redirect('home')
    context = {'page': page}
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
def homeAdmin(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")
    return render(request, 'base/home-admin.html', {})

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
    print("Se incarca home")
    return render(request, 'base/home.html', context)


def MenuItems(request):
    menu = Menu.objects.all()
    context = {
        'menu': menu,
    }
    return render(request, 'base/menu_items.html', context)


def MenuForEvent(request, event_id):
    event = Event.objects.get(id=event_id)
    guests = event.guests.all()
    menu_items = Menu.objects.all()
    menu_items = menu_items.reverse() 
    countguests = guests.count() 
    majority_allergens = []

    for guest in guests:
        if isinstance(guest.allergens, str):
            try:
                guest_allergens = json.loads(guest.allergens)
            except json.JSONDecodeError:
                guest_allergens = [guest.allergens]
        else:
            guest_allergens = guest.allergens

        for allergen in guest_allergens:
            majority_allergens.append(allergen)
    allergen_counts = Counter(majority_allergens)
    menu_selected = []
    for guest in guests:
        available_dishes = [dish for dish in menu_items if dish.item_cuisine == guest.cuisine_preference]
        if guest.vegan:
            available_dishes = [dish for dish in available_dishes if dish.item_vegan]
        if not guest.vegan:
            available_dishes = [dish for dish in available_dishes]
        if isinstance(guest.allergens, str):
            try:
                guest_allergens = json.loads(guest.allergens)
            except json.JSONDecodeError:
                guest_allergens = [guest.allergens]
        else:
            guest_allergens = guest.allergens
        for allergen in guest_allergens:
            available_dishes_filtered = []
            for dish in available_dishes:
                if isinstance(dish.allergens, str):
                    try:
                        dish_allergens = json.loads(dish.allergens)
                    except json.JSONDecodeError:
                        dish_allergens = [dish.allergens]
                else:
                    dish_allergens = dish.allergens

                if not set(dish_allergens).intersection(set(guest_allergens)):
                    available_dishes_filtered.append(dish)

        available_dishes = available_dishes_filtered
        if available_dishes:
                selected_dish = available_dishes[0]
                menu_selected.append(selected_dish)
    unique_menu = []
    seen = set()
    for selected_dish in menu_selected:
        if hasattr(selected_dish, 'item_name') and selected_dish.item_name not in seen:
            unique_menu.append(selected_dish)
            seen.add(selected_dish.item_name)
    grouped_menu = defaultdict(list)
    for dish in unique_menu:
        grouped_menu[dish.item_cuisine].append(dish)
    EventMenu.objects.filter(event=event).delete()
    for dish in unique_menu:
        EventMenu.objects.create(
            event=event,
            item_name=dish.item_name,
            item_cuisine=dish.item_cuisine,
            item_vegan=dish.item_vegan,
            allergens=dish.allergens,
            item_picture=dish.item_picture
        )
    eventmenu = EventMenu.objects.filter(event=event)
    context = {
        'eventmenu': eventmenu,
        'event': event,
        'guests_count': countguests,
    }
    return render(request, 'base/event_menu.html', context)



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
            location = form.save(commit=False)
            location.owner = request.user 
            location.save()

            custom_types = form.cleaned_data.get('custom_types')
            if custom_types:  
                for type_name in custom_types:
                    type_instance, created = Type.objects.get_or_create(name=type_name.strip()) 
                    if type_instance not in location.types.all(): 
                        location.types.add(type_instance) 
            else:
                selected_types = form.cleaned_data.get('types')
                for type_instance in selected_types:
                    if type_instance not in location.types.all():  
                        location.types.add(type_instance)  

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

def carousel_view(request):
    return render(request, 'base/carousel-imagini.html')


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
    return render(request, 'base/delete.html', {'obj': review})




@login_required(login_url='/login')
def chat(request):
    print("DATE:")
    print(request.POST)
    profiles = Profile.objects.all()
    messages = Message.objects.all()
    form = MessageForm()
    
    if request.htmx:
        form = MessageForm(request.POST)
        print("DARi")
        if form.is_valid():
            print("Formularul este valid")
            message = form.save(commit=False)
            message.author = request.user
            print(message.author)
            message.save()
            context = {
                'message': message,
                'form': form,
                'messages':messages,
                'profiles': profiles,
            }
            print(f"Message saved: {message.body, message.author}") 
            return render(request, 'base/partials/chat_message_p.html', context)
        else:
            print("Formularul nu este valid:", form.errors) 
    
    return render(request, 'base/chat.html', {
        'form': form,
        'profiles': profiles,
        'messages': messages
    })

