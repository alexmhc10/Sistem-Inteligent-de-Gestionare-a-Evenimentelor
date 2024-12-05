from django.shortcuts import render, redirect, get_object_or_404
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
from .forms import EventForm
from .models import Task
from .forms import TaskForm
from django.http import HttpResponseRedirect
from .models import Event
import random
from datetime import datetime

@login_required(login_url='/login')
def event_builder(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organized_by = request.user
            event.save()
            form.save_m2m()  
            return redirect('my_events')  
    else:
        form = EventForm()

    return render(request, 'base/event_builder.html', {'form2': form})

@login_required(login_url='/login')
def feedback_event(request):
    return render(request, 'base/feedback_eveniment.html')
@login_required(login_url='/login')
def event_history(request):
    events = Event.objects.all()
    return render(request, 'base/istoric_evenimente.html', {'events': events})

@login_required(login_url='/login')
def guest_list(request):
    guests = Guests.objects.all()
    return render(request, 'base/guest_list.html', {'guests': guests})

def vizualizare_eveniment(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'base/panou_eveniment.html', {'event': event})
from django.urls import reverse



def vizualizare_eveniment(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'base/panou_eveniment.html', {'event': event})

@login_required(login_url='/login')
def my_events(request):
   
    events = Event.objects.all()
    context = {
        'events': events,
    }
    return render(request, 'base/my_events.html', context)
@login_required(login_url='/login')
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return redirect('home')

@login_required(login_url='/login')
def my_events(request):
   
    events = Event.objects.all()
    context = {
        'events': events,
    }
    return render(request, 'base/my_events.html', context)

# def task_manager_view(request):
#     if request.method == 'POST':
#         form = TaskForm(request.POST)
#         if form.is_valid():
#             task = form.save(commit=False)
#             task.user = request.user
#             task.save()
#     else:
#         form = TaskForm()

#     tasks = Task.objects.filter(user=request.user)
#     return render(request, 'base/task-manager.html', {'form': form, 'tasks': tasks})


@login_required(login_url='/login')
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('home')  
    else:
        form = TaskForm()
    return render(request, 'base/add_task.html', {'form': form})



@login_required(login_url='/login')
def complete_task(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)
    task.completed = True
    task.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def carousel_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()  
            return redirect('home')  
    else:
        form = EventForm()
    return render(request, 'base/carousel-imagini.html', {'form': form})


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
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, 'base/approve_user.html', {'profile': profile})


@login_required(login_url='login')
def admin_charts(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")
    locations_data = []
    locations = Location.objects.all()
    
    for location in locations:
        event_count = location.event_set.count() 
        locations_data.append({
            'name': location.name,
            'event_count': event_count,
        })
    
    context = {
        'locations_data': json.dumps(locations_data),
    }
    return render(request, 'base/admin-charts.html', context)



@login_required(login_url='login')
def admin_locations(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")
    locations = Location.objects.all()
    detailed_locations = []
    for location in locations:
        detailed_locations.append({
            'name':location.name,
            'added_by':location.owner,
            'photo':location.gallery,
            'located':location.location,
            'seats':location.seats_numbers,
            'added_at':location.created_at,
            'cost': location.cost
        })
    organizers = User.objects.filter(is_superuser = False)
    count_organizers = organizers.count()
    filter_date = datetime(2024, 12, 2, 0, 0, 0)
    new_locations_count = sum(1 for location in detailed_locations 
            if location['added_at'].replace(tzinfo=None) > filter_date)
    new_locations_detailed = []
    for location in detailed_locations:
        if location['added_at'].replace(tzinfo=None) > filter_date:
            new_locations_detailed.append(location)
    all_locations_count = locations.count()
    types_with_location_count = []
    types = Type.objects.all()
    for type in types:
        location_count = Location.objects.filter(types=type).count()
        types_with_location_count.append({'type': type.name, 'count': location_count})
    print("Date locatii cu tipuri:" ,types_with_location_count)
    context = {
        'new_locations_detailed':new_locations_detailed,
        'types_with_location_count':types_with_location_count,
        'organizers':organizers,
        'count_organizers':count_organizers,
        'all_locations_count':all_locations_count,
        'new_locations_count':new_locations_count,
        'detailed_locations':detailed_locations
    }
    return render(request, 'base/admin-locations.html', context)


@login_required(login_url='login')
def admin_events(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")
    events = Event.objects.all()
    users = User.objects.filter(is_superuser=False)
    types = Type.objects.all()
    types_with_event_count = []
    
    for type in types:
        event_count = Event.objects.filter(types=type).count()
        types_with_event_count.append({'type': type.name, 'count': event_count})
    
    events_count = events.count()

    detailed_events = []
    for event in events:
        guest_count = event.guests.count()  
        event_types = [type.name for type in event.types.all()] 
        detailed_events.append({
            'id':event.id,
            'cost':event.cost,
            'name': event.event_name,
            'location': event.location,
            'event_date': event.event_date,
            'event_time': event.event_time,
            'completed': event.completed,
            'types': event_types,
            'guest_count': guest_count,
            'organized_by':event.organized_by
        })
    print("Date evenimente: ", detailed_events)
    detailed_incompleted_events = []
    finished_count = 0
    for item in detailed_events:
        if item['completed'] == True:
            finished_count += 1
            print(item)
            detailed_incompleted_events.append(item)
    context = {
        'finished_count':finished_count,
        'detailed_incompleted_events':detailed_incompleted_events,
        'detailed_events': detailed_events,
        'events_count': events_count,
        'types_with_event_count': types_with_event_count,
        'events': events,
        'users': users
    }
    return render(request, 'base/admin-events.html', context)



@login_required(login_url='login')
def admin_view_events(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")
    context = {

    }
    return render(request, 'base/admin-view-event.html', context)



@login_required(login_url='login')
def admin_view_locations(request, name):
    location = Location.objects.get(name=name)
    profile = Profile.objects.get(username=location.owner)
    events = Event.objects.filter(location=location)
    detailed_events = []
    for event in events:
        detailed_events.append({
            'organizer':event.organized_by,
            'name':event.event_name,
            'guests':event.guests.count(),
            'location':event.location,
            'date':event.event_date,
            'time':event.event_time,
            'description':event.event_description,
            'created_at':event.created_at,
            'completed':event.completed,
            'type':event.types,
            'cost':event.cost
        })
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")
    context = {
        'detailed_events':detailed_events,
        'events':events,
        'profile':profile,
        'location':location
    }
    return render(request, 'base/admin-view-location.html', context)



@login_required(login_url='login')
def users(request):
    if not request.user.is_superuser:
        return HttpResponse("Only superusers can approve users.")
    
    awaiting_profiles = Profile.objects.filter(approved=False)
    waiting_count = Profile.objects.filter(approved=False).count()
    profiles = Profile.objects.filter(approved=True).exclude(user__username="Darius")
    users = User.objects.all()
    user_data = [{'username': profile.user.username, 'salary': random.choice([1000, 5000, 10000])} for profile in profiles]
    context = {
        'chartusers': json.dumps(user_data),
        'waiting_count':waiting_count,
        'users':users,
        'profiles':profiles,
        'awaiting_profiles':awaiting_profiles
    }
    return render(request, 'base/users.html', context) 


@login_required(login_url='login')
def homeAdmin(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")
    form1 = TaskForm()
    profiles = Profile.objects.all()
    messages = Message.objects.all()
    form = MessageForm()
    if request.method == 'POST' and request.htmx:
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.save()
            context = {
                'message': message,
                'form': form,
                'messages': messages,
                'profiles': profiles,
            }
            return render(request, 'base/partials/chat_message_p.html', context)
    tasks = Task.objects.all()
    users = User.objects.all()
    context= {
        'users':users,
        'tasks':tasks,
        'form1':form1,
        'profiles': profiles,
        'messages': messages,
        'form': form,
        'hx_post_url': reverse('home-admin')
    }
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('home-admin')
    return render(request, 'base/home-admin.html', context)



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
    form1 = TaskForm()
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
    tasks = Task.objects.all()
    tasks_count = tasks.count()
    profiles = Profile.objects.filter(approved=True)
    form2 = EventForm
    context = {
        'form2':form2,
        'form1':form1, 
        'tasks': tasks,
        'tasks_count':tasks_count,
        'users' : users,
        'locations' : locations,
        'types' : types,
        'location_count' : location_count,
        'profiles' : profiles
        }
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('home')
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



@login_required(login_url='/login')
def updateUserAdmin(request, pk):
    if not request.user.is_superuser:
            return HttpResponse("Only superusers can approve users.")
    user = User.objects.get(username=pk)
    form = CustomUserChangeForm(instance=user)  
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users')
    context = {
        'form':form
    }
    return render(request, 'base/admin-update-user.html', context)

@login_required(login_url='/login')
def deleteUserAdmin(request, pk):
    if not request.user.is_superuser:
        return HttpResponse("Only superusers can approve users.")
    user = User.objects.get(username=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('home-admin')
    return render(request, 'base/admin-delete-user.html', {
        'obj': user})




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
def deleteUser(request, pk):
    if not request.user.is_superuser:
        return HttpResponse("Only superusers can approve users.")
    user = User.objects.get(username=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('admin-home')
    return render(request, 'base/delete.html', {
        'obj': user})

# @login_required(login_url='/login')
# def chat(request):
#     print("DATE:")
#     print(request.POST)
#     profiles = Profile.objects.all()
#     messages = Message.objects.all()
#     form = MessageForm()
    
#     if request.htmx:
#         form = MessageForm(request.POST)
#         print("DARi")
#         if form.is_valid():
#             print("Formularul este valid")
#             message = form.save(commit=False)
#             message.author = request.user
#             print(message.author)
#             message.save()
#             context = {
#                 'message': message,
#                 'form': form,
#                 'messages':messages,
#                 'profiles': profiles,
#             }
#             print(f"Message saved: {message.body, message.author}") 
#             return render(request, 'base/partials/chat_message_p.html', context)
#         else:
#             print("Formularul nu este valid:", form.errors) 
    
#     return render(request, 'base/chat.html', {
#         'form': form,
#         'profiles': profiles,
#         'messages': messages
#     })

