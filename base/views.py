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
from datetime import datetime,timedelta
from collections import defaultdict
from django.utils.timezone import localtime
from django.utils import timezone
from .models import Event, EventHistory
import socket
from user_agents import parse
from device_detector import DeviceDetector
from .decorators import user_is_organizer, user_is_staff, user_is_guest


def resume_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        # Modifică câmpul `is_canceled` pentru a marca evenimentul ca activ
        event.is_canceled = False  # Evenimentul nu mai este anulat
        event.save()
        messages.success(request, 'Event has been resumed and moved to "My Events".')
    return redirect('event_history')  # Redirecționează înapoi la istoricul evenimentelor


@login_required(login_url='login')
def cancel_event(request, event_id):
    if request.method == "POST":
        event = get_object_or_404(Event, id=event_id)
        
        event.is_canceled = True
        event.save()
        
        messages.success(request, f'Event "{event.event_name}" has been canceled successfully.')
        
        return redirect('my_events') 
       

@login_required(login_url='login')
@user_is_organizer
def organizer_dashboard(request):

    events = Event.objects.filter(organized_by=request.user)
    locations = Location.objects.filter(owner=request.user)
    
  
    context = {
        'events_count': 12,  # Example data
        'confirmed_guests': 240,
        'estimated_profit': 15000,
        'notifications': [
            "Invitatul 'Ion Popescu' a confirmat prezența.",
            "Evenimentul 'Nuntă Maria' este în 3 zile.",
            "Un nou feedback a fost adăugat de un participant."
        ]
    }
    return render(request, 'base/organizator-dashboard.html', context)


@login_required(login_url='/login')
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    EventHistory.objects.create(
        event_name=event.event_name,
        event_date=event.event_date,
        event_time=event.event_time,
        location=event.location,
        description=event.event_description,
        cost=event.cost,
        organized_by=event.organized_by,
        created_at=event.created_at,
        updated_at=event.updated_at,
        deleted_at=timezone.now(),  
    )

   
    event.delete()

    messages.success(request, 'Event has been successfully deleted and archived.')
    return redirect('my_events') 


@login_required(login_url='/login')
def event_builder(request):
    locations = Location.objects.all()  # Obține toate locațiile
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

    return render(request, 'base/event_builder.html', {'form2': form, 'locations': locations})


@login_required(login_url='/login')
def feedback_event(request):
    return render(request, 'base/feedback_eveniment.html')
@login_required(login_url='/login')
def event_history(request):
    events = Event.objects.filter(is_canceled=True)
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
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='/login')
def my_events(request):
    events = Event.objects.filter(is_canceled=False)
    return render(request, 'base/my_events.html', {'events': events})

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
    if request.user.is_authenticated:
        print(f"User {request.user.username} is already authenticated, logging out.")
        logout(request)

    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Attempting login with username: {username}")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            print(f"Authentication successful for user: {user.username}")
            login(request, user)
            if hasattr(user, 'is_superuser') and user.is_superuser:
                print(f"Redirecting superuser {user.username} to admin home.")
                return redirect('home-admin')
            elif hasattr(request.user, 'profile') and request.user.profile.user_type == 'staff':  
                print(f"Redirecting user {user.username} to personal home.")
                return redirect('personal_eveniment_home')
            elif hasattr(request.user, 'profile') and request.user.profile.user_type == 'guest':
                print(f"Redirecting user {user.username} to guest home.")
                return redirect('guest_home')
            else:
                print(f"Redirecting standard user {user.username} to home.")
                return redirect('home')
        else:
            print(f"Authentication failed for username: {username}")
            messages.error(request, "Invalid credentials")
            return render(request, 'base/login_register.html', {'page': page})

    print("Rendering login page.")
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
    event = Event.objects.get(event_name=pk)
    guests_count = event.guests.count()
    location = Location.objects.get(event=event)
    next_day = event.event_date + timedelta(days=1)
    context = {
        'next_day':next_day,
        'location':location,
        'event':event,
        'guests_count':guests_count
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
    events_count = events.count()
    reviews = Review.objects.filter(location=location)
    reviews_count = reviews.count()
    print("Reviews",reviews)
    context = {
        'reviews':reviews,
        'reviews_count':reviews_count,
        'events_count':events_count,
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
    users = User.objects.filter(is_superuser=False).exclude(username="defaultuser")
    if request.method == 'POST':
        nr_form = request.POST.get('nr_form')
        if nr_form == "form_1":
            id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=id)
            except User.DoesNotExist:
                return HttpResponse("User not found.")
            picture = request.FILES.get('profile_picture')
            first_name = request.POST.get('editFirstNameModal')
            last_name = request.POST.get('editLastNameModal')
            email = request.POST.get('editEmailModal')
            username = request.POST.get('editUsernameModal')
            phone = request.POST.get('phone')
            if user.profile:
                if picture:
                    user.profile.photo = picture
                user.profile.first_name = first_name
                user.profile.last_name = last_name
                user.profile.email = email
                user.profile.phone = phone
                user.profile.save()
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()
            return redirect('users')
        if nr_form == "form_3":
            id = request.POST.get('profile_id')
            profile = Profile.objects.get(id=id)
            if request.POST.get('action') == "accept":
                user = User.objects.create_user(
                    username=profile.username,
                    password=profile.password,
                    email=profile.email
                )
                profile.user = user 
                profile.approved = True
                profile.save()
                return redirect('users')
            if request.POST.get('action') == "reject":
                profile.delete()
                return redirect('users')
    profiles = Profile.objects.all()
    user_data = [{'username': profile.user.username, 'salary': random.choice([1000, 5000, 10000])} for profile in profiles]
    non_acc = Profile.objects.filter(approved=False)
    context = {
        'non_acc':non_acc,
        'user_data':user_data,
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
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good Morning"
    elif 12 <= current_hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    tasks = Task.objects.all()
    users = User.objects.filter(is_superuser=False)
    events = Event.objects.all()
    event_locations = [event.location.location for event in events]
    ev_loc = [event.location for event in events]
    locations = Location.objects.all()
    events_count = []
    for location in locations:
        events_count.append({
            'name':location.name,
            'ev_c':location.event_set.count()
            })
    ev_nr = events.count()
    org_ev = []
    organizer_event_count = Counter(event.organized_by for event in events)
    print(organizer_event_count)
    for organizer, count in organizer_event_count.items():
        org_ev.append({
            'organizer': organizer,
            'event_count': count
        })
    high_ev = []
    for location in locations:
        event_count = location.event_set.count() 
        if event_count > 0:
            percentage = int((event_count / ev_nr) * 100)  
            high_ev.append({
                'location': location.location,
                'percentage':percentage
            })
    loc_nr = locations.count()
    for event in events:
        print("Evenimente corecte:", event.event_name, event.location)
    context= {
        'org_ev':org_ev,
        'loc_nr':loc_nr,
        'ev_nr':ev_nr,
        'high_ev':high_ev,
        'greeting':greeting,
        'ev_loc':ev_loc,
        'events':events,
        'users':users,
        'tasks':tasks,
        'form1':form1,
        'profiles': profiles,
        'messages': messages,
        'form': form,
        'hx_post_url': reverse('home-admin'),
        'event_locations': event_locations,
        'events_count':events_count
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
def admin_settings(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    access_time = datetime.now()

    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    device_name = "Unknown"
    os_name = "Unknown"
    if "iPhone" in user_agent_string:
        device_name = "iPhone"
        os_name = "iOS"
    elif "Android" in user_agent_string:
        device_name = "Android Phone"
        os_name = "Android"
    elif "Windows" in user_agent_string:
        device_name = "Windows PC"
        os_name = "Windows"
    device_access, created = DeviceAccess.objects.update_or_create(
        device_name=device_name,
        os_name=os_name,
        defaults={'last_access_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'), 'user_agent': user_agent_string},
    )
    ip_address = request.META.get('REMOTE_ADDR', '')
    print("Date: ",request.POST,"\n")
    user = request.user
    if request.method == 'POST':
        form_type = request.POST.get('form_type', '')
        if form_type == 'form_1':
            profile_photo = request.FILES.get('profile_photo')
            if profile_photo:
                user.profile.photo = profile_photo
            firstname = request.POST.get('firstName')
            lastname = request.POST.get('lastName')
            email = request.POST.get('email')
            username = request.POST.get('username')
            phone = request.POST.get('phone')
            location = request.POST.get('location')
            address = request.POST.get('address')
            zipcode = request.POST.get('zipCode')
            user.first_name = firstname
            user.profile.first_name = firstname
            user.last_name = lastname
            user.profile.last_name = lastname
            user.email = email
            user.profile.email = email
            user.username = username
            user.profile.username = username
            user.profile.number = phone
            user.profile.location = location
            user.profile.street = address
            user.profile.zip_code = zipcode
            user.save()
            user.profile.save()
            return redirect('admin_account_settings')
        elif form_type == 'form_2':
            email = request.POST.get('newEmail')
            user.email = email
            user.profile.email = email
            user.save()
            user.profile.save()
            return redirect('admin_account_settings')
        elif form_type == 'form_4':
            action = request.POST.get('action')
            linkedin = request.POST.get('linkedin')
            facebook = request.POST.get('facebook')
            google = request.POST.get('google')
            if action == "connect_linkedin":
                user.profile.work_link = linkedin
            if action == "disconnect_linkedin":
                user.profile.work_link = ""
            if action == "connect_google":
                user.profile.google_link = google
            if action == "disconnect_google":
                user.profile.google_link = ""
            if action == "connect_facebook":
                user.profile.facebook = facebook
            if action == "disconnect_facebook":
                user.profile.facebook = ""
            user.profile.save()
            return redirect('admin_account_settings')
        elif form_type == 'form_5':
            request.user.delete()
            request.user.profile.delete()
            return redirect('')
    devices = DeviceAccess.objects.all()
    for device in devices:
        print("Dispozitiv: ", device.device_name, device.last_access_time)
    print(f"Accessed at {access_time} from IP {ip_address} with {device_name} running {os_name}")
    print(device_name)
    context = {
        'access_time': access_time,
        'device_name': device_name,  
        'os_name': os_name,
        'ip_address': ip_address,
        'devices':devices
    }
    return render(request, 'base/admin-account-settings.html', context)



#pagina proba
@login_required(login_url='login')
def organizer_locations(request):
    locations = Location.objects.all()
    detailed_locations = []
    for location in locations:
        events = Event.objects.filter(location=location)
        
        detailed_locations.append({
            'name': location.name,
            'added_by': location.owner,
            'photo': location.gallery,
            'located': location.location,
            'seats': location.seats_numbers,
            'added_at': location.created_at,
            'cost': location.cost,
            'events': [
                {
                    'event_name': event.event_name,
                    'event_date': event.event_date,
                    'event_time': event.event_time,
                    'event_description': event.event_description,
                    'event_cost': event.cost,
                }
                for event in events
            ]
        })
    context = {
        'detailed_locations':detailed_locations,
        'locations':locations
    }
    return render(request, 'base/organizator-locatii.html', context)


##evenimente proba
@login_required(login_url='login')
def organizer_events(request):
    events = Event.objects.filter(organized_by=request.user)
    context = {
        'events': events
    }
    return render(request, 'base/organizator-home.html', context)


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
def viewUserAdmin(request, pk):
    if not request.user.is_superuser:
            return HttpResponse("Only admin can access this page.")
    user = User.objects.get(username=pk)
    # form = CustomUserChangeForm(instance=user)  
    # if request.method == 'POST':
    #     form = CustomUserChangeForm(request.POST, instance=user)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('users')
    events = Event.objects.filter(organized_by=user)
    locations = Location.objects.filter(owner=user)
    count_events = 0 
    count_locations = 0
    for event in events:
        count_events += 1
    for location in locations:
        count_locations += 1
    last_login = user.last_login
    location_counts = defaultdict(int)

    for event in events:
        location_counts[event.location.name] += 1
    detailed_locations = [{'location_name': loc.name, 'ev_count': location_counts[loc.name]} for loc in locations] 
    print("Locatii cu evenimente:", detailed_locations)
    context = {
        'detailed_locations':detailed_locations,
        'locations':locations,
        'count_events':count_events,
        'count_locations':count_locations,
        'last_login':last_login,
        'user':user,
        'events':events,
        # 'form':form
    }
    return render(request, 'base/admin-view-user.html', context)


@login_required(login_url='/login')
def viewUserEvents(request, pk):
    if not request.user.is_superuser:
            return HttpResponse("Only admin can access this page.")
    user = User.objects.get(username=pk)
    ev_count = 0
    events = Event.objects.filter(organized_by=user).order_by('-updated_at')
    for event in events:
        ev_count += 1
    time_left = {}
    for event in events:
        now = timezone.now()
        time_diff = event.event_date - now.date()  
        time_left[event.event_name] = abs(time_diff.days)
    now = timezone.now().date()
    locations = Location.objects.filter(owner=user)
    loc_count = locations.count()
    print(time_left)
    print(now)
    context = {
        'loc_count':loc_count,
        'now':now,
        'ev_count':ev_count,
        'user':user,
        'events':events,
        'time_left': time_left,
    }
    return render(request, 'base/admin-user-events.html', context)


@login_required(login_url='/login')
def viewUserLocations(request, pk):
    if not request.user.is_superuser:
            return HttpResponse("Only admin can access this page.")
    user = User.objects.get(username=pk)
    locations = Location.objects.filter(owner=user)
    loc_count = locations.count()
    events = Event.objects.filter(organized_by=user)
    ev_count = events.count()
    print("Count:",loc_count)
    context = {
    'locations':locations,
    'user':user,
    'ev_count':ev_count,
    'loc_count':loc_count
    }
    return render(request, 'base/admin-user-locations.html', context)

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


@login_required(login_url='/login')
@user_is_staff
def personal_eveniment_home(request):
    current_date = datetime.today()
    past_events = Event.objects.filter(event_date__lt = current_date)
    future_events = Event.objects.filter(event_date__gte = current_date)
    profiles = Profile.objects.all()
    locations = Location.objects.all()
    user = request.user
    context = {
        'future_events': future_events,
        'past_events': past_events,
        'locations': locations,
        'profiles': profiles,
        'logged_user': user
        }

    return render(request, 'base/personal_eveniment_home.html', context)

from django.http import JsonResponse

def filter_events(request):
    try:
        search = request.GET.get('search', '').lower()
        event_type = request.GET.get('event_type', '')
        filter_date = request.GET.get('filter_date', '')

        events = Event.objects.all()

        # Filtrare după căutare
        if search:
            events = events.filter(title__icontains=search)

        # Filtrare după tip (Future/Past)
        if event_type == 'future':
            events = events.filter(date__gte=datetime.today())
        elif event_type == 'past':
            events = events.filter(date__lt=datetime.today())

        # Filtrare după dată exactă
        if filter_date:
            events = events.filter(datetime=filter_date)

        # Împărțim evenimentele în viitoare și trecute
        future_events = events.filter(date__gte=datetime.today())
        past_events = events.filter(date__lt=datetime.today())

        # Construim răspunsul JSON
        response_data = {
            'future_events': [
                {
                    'title': event.event_name,
                    'description': event.event_description,
                    'date': event.event_time.strftime('%Y-%m-%d')
                }
                for event in future_events
            ],
            'past_events': [
                {
                    'title': event.event_name,
                    'description': event.event_description,
                    'date': event.event_time.strftime('%Y-%m-%d')
                }
                for event in past_events
            ],
        }

        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required(login_url='/login')
@user_is_staff
def personal_vizualizare_eveniment(request, pk):
    event = Event.objects.get(id=pk)
    context = {
        'event': event
    }
    return render(request, 'base/personal_vizualizare_eveniment.html', context)

@login_required(login_url='/login')
@user_is_staff
def personal_aranjament_invitati(request, pk=None):
    events = Event.objects.first()
    context_default = {
        'event': events
    }
    location = Location.objects.first()
    context_event = {
        'location': location
    }
    if pk:
        return render(request, 'base/personal_aranjament_invitati.html', context_event)
    else:
        return render(request, 'base/personal_aranjament_invitati.html', context_default)


@login_required(login_url='/login')
@user_is_staff
def personal_face_id(request):
    return render(request, 'base/personal_face_id.html')


@login_required(login_url='/login')
@user_is_guest
def guest_profile(request):
    return render(request, 'base/guest_profile.html')


@login_required(login_url='/login')
@user_is_guest
def guest_home(request):
    return render(request, 'base/guest_home.html')


@login_required(login_url='/login')
@user_is_guest
def invite_form(request,event_id,guest_id):
    event = Event.objects.get(id=event_id)
    guest = Guests.objects.first()
    context = {
        'guest' : guest,
        'event' : event
    }
    return render(request, 'base/invite_form.html', context)
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

