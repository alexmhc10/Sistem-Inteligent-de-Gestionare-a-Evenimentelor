from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login,logout
from .models import *
from .forms import *
from django.conf import settings
from collections import Counter, defaultdict
import json
from .forms import EventForm
from .forms import TaskForm
from django.http import HttpResponseRedirect
import random
from datetime import datetime,timedelta
from collections import defaultdict
from django.utils.timezone import localtime
from django.utils import timezone
import socket
from user_agents import parse
from device_detector import DeviceDetector
from .decorators import user_is_organizer, user_is_staff, user_is_guest
from django.contrib.auth.hashers import check_password
from django.utils.timezone import make_aware
from django.db.models.functions import TruncMonth
from django.db.models import Count
from .models import Profile
from django.http import JsonResponse
from .forms import ProfileEditForm
from base.models import Event
from .models import Location
from .utils import is_ajax, classify_face
import base64
from django.core.files.storage import FileSystemStorage
import pandas as pd
from django.utils.text import slugify





def locations_list(request):
    locations = Location.objects.all()
    return render(request, 'base/locations_list.html', {'locations': locations})


@login_required
def home_organizer(request):
    events = Event.objects.all()
    upcoming_events = events.filter(event_date__gte=timezone.now())
    context = {
        'total_events': events.count(),
        'total_participants': sum(event.guests.count() for event in events),
        'acceptance_rate': 85,  
        'average_feedback': 4.7,  
        'upcoming_events': upcoming_events
    }
    return render(request, 'base/home-organizer.html', context)


@login_required
def guest_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    guests = event.guests.all() 
    return render(request, 'base/guest_list.html', {'event': event, 'guests': guests})

def event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'base/event_details.html', {'event': event})
def event_list(request):
    events = Event.objects.all()  
    return render(request, 'base/my_events.html', {'events': events})


@login_required
def edit_profile(request, username):
    profile = get_object_or_404(Profile, user__username=username)

    if profile.user != request.user:
        return redirect('profile')

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            Notification.objects.create(
                    user=request.user,
                    action_type='updated_profile',
                    target_object_id=request.user.id,
                    target_object_name=request.user.username,
                    target_model='Profile'
                )
            return redirect('edit_profile', username=profile.user.username)
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'base/organizer_profile.html', {'form': form, 'profile': profile})    
@login_required


def organizer_profile(request, username):
    profile = get_object_or_404(Profile, user__username=username)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            Notification.objects.create(
                    user=request.user,
                    action_type='updated_profile',
                    target_object_id=request.user.id,
                    target_object_name=request.user.username,
                    target_model='Profile'
                )
            return redirect('organizer-profile', username=profile.user.username)  
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'base/organizer_profile.html', {'profile': profile, 'form': form})






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
    locations = Location.objects.all()
    if request.method == 'POST' and request.FILES.get('guest_file'):
        form = EventForm(request.POST)

        if form.is_valid():
            event = form.save(commit=False)
            event.organized_by = request.user
            event.save()
            form.save_m2m()
            Notification.objects.create(
                user=request.user,
                action_type='created_event',
                target_object_id=request.user.id,
                target_object_name=request.user.username,
                target_model='Event'
            )  

        uploaded_file = request.FILES['guest_file']

        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)

        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            return render(request, 'event_builder.html', {'error': 'Format de fișier invalid'})

        for _, row in df.iterrows():
            name = row.get('nume')
            email = row.get('email')
            phone = row.get('telefon')

            if name and email:
                username = name.replace(" ", "")
                
                counter=1
                while User.objects.filter(username=username).exists():
                    username = f"{username}{counter}"
                    counter += 1

                user, created = User.objects.get_or_create(username=username, email=email)
                if created:
                    user.set_password(phone)
                    user.save()
                    Profile.objects.create(user=user, username=username, email=email, password=phone, number=phone, user_type='guest')

                    try:
                        event = Event.objects.get(id=event.id)
                    except Event.DoesNotExist:
                        continue

                    RSVP.objects.create(guest=user, event=event)
        


        
            
        return redirect('my_events')  
    else:
        form = EventForm()
        form_file = UploadFileForm()


    return render(request, 'base/event_builder.html', {'form2': form,'form_file': form_file, 'locations': locations})


@login_required(login_url='/login')
def feedback_event(request):
    return render(request, 'base/feedback_eveniment.html')
@login_required(login_url='/login')
def event_history(request):
    events = Event.objects.filter(is_canceled=True)
    return render(request, 'base/istoric_evenimente.html', {'events': events})



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


def loginPage(request):
    if request.user.is_authenticated:
        print(f"User {request.user.username} is already authenticated, logging out.")
        logout(request)
    next_url = request.GET.get('next', '/')
    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Attempting login with username: {username}")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            profile = user.profile_set.first()
            print("Tip: ", profile.user_type)
            print("Profil logat: ", profile)
            print(f"Authentication successful for user: {user.username}")
            login(request, user)
            if user.is_superuser:
                if next_url != "" and next_url != '/':
                    return redirect(next_url)
                else:
                    return redirect('home-admin')
            elif profile.user_type == 'staff':
                print(f"Redirecting user {user.username} to personal home.")
                return HttpResponseRedirect(reverse('personal_eveniment_home'))  
            elif profile.user_type == 'organizer':
                print(f"Redirecting user {user.username} to organizer home.")
                return HttpResponseRedirect(reverse('home-organizer'))  
            else:
                print(f"Redirecting user {user.username} to guest home.")
                return HttpResponseRedirect(reverse('guest_home'))  
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
            profile.user_type = "organizer"
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
    detailed_locations = []
    organizers = Profile.objects.filter(
    user__is_superuser=False, 
    user_type="organizer"
).exclude(user__username="defaultuser").select_related('user')

    organizer_users = organizers.values_list('user', flat=True)

    locations = Location.objects.filter(owner__in=organizer_users)

    for location in locations:
        detailed_locations.append({
            'name':location.name,
            'added_by':location.owner,
            'photo':location.gallery,
            'located':location.location,
            'seats':location.seats_numbers,
            'added_at':location.created_at,
            'cost': location.cost,
            'id':location.id,
            'types':location.types
        })
    
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
    users = User.objects.filter(is_superuser=False).exclude(username="defaultuser")
    types = Type.objects.all()
    types_with_event_count = []
    
    for type in types:
        event_count = Event.objects.filter(types=type).count()
        types_with_event_count.append({'type': type.name, 'count': event_count})
    
    events_count = events.count()

    detailed_events = []
    today = datetime.today()
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
            'cancelled': event.is_canceled,
            'types': event_types,
            'guest_count': guest_count,
            'organized_by':event.organized_by
        })
    detailed_incompleted_events = []
    finished_count = 0
    cancelled_count = 0
    for item in detailed_events:
        if item['completed'] == True:
            finished_count += 1
        elif item['cancelled'] == True:
            cancelled_count += 1
            detailed_incompleted_events.append(item)
    today_date = today.date()
    today_time = today.strftime("%H:%M:%S")
    context = {
        'cancelled_count':cancelled_count,
        'today_date':today_date,
        'today_time':today_time,
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
    error_pas = False
    updated = False
    if request.method == 'POST':
        nr_form = request.POST.get('nr_form')
        if nr_form == "form_1":
            id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=id)
            except User.DoesNotExist:
                return HttpResponse("User not found.")
            profile = user.profile_set.first() 
            picture = request.FILES.get('profile_picture')
            first_name = request.POST.get('editFirstNameModal')
            last_name = request.POST.get('editLastNameModal')
            email = request.POST.get('editEmailModal')
            username = request.POST.get('editUsernameModal')
            phone = request.POST.get('phone')
            if profile:
                if picture:
                    profile.photo = picture
                profile.first_name = first_name
                profile.last_name = last_name
                profile.email = email
                profile.phone = phone
                profile.save()
                updated = True
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()
            updated = True
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
        if nr_form == "form_2":
            id = request.POST.get('user_id')
            user = User.objects.get(id=id)
            password = request.POST.get('currentPassword', '')
            if check_password(password, request.user.password):
                new_pass = request.POST.get('editUserModalNewPassword')
                confirm_new_pas = request.POST.get('confirmNewPassword')
                if new_pass == confirm_new_pas:
                    user.set_password(new_pass)
                    user.save()
                    updated = True
                else:
                    error_pas = True
            else:
                error_pas = True
    user_profiles = {user: user.profile_set.first() for user in users}
    profiles = Profile.objects.all()
    user_data = [{'username': profile.user.username if profile.user else profile.username, 'salary': random.choice([1000, 5000, 10000])} for profile in profiles]
    non_acc = Profile.objects.filter(approved=False)
    notifications = Notification.objects.all()
    context = {
        'notifications':notifications,
        'user_profiles':user_profiles,
        'updated':updated,
        'error_pas':error_pas,
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
    budget = Budget.objects.first()
    today = datetime.today()
    start_of_current_month = datetime(today.year, today.month, 1)
    if today.month == 1:
        start_of_previous_month = datetime(today.year - 1, 12, 1)
    else:
        start_of_previous_month = datetime(today.year, today.month - 1, 1)
    events_this_month = Event.objects.filter(event_date__gte=start_of_current_month).count()
    events_last_month = Event.objects.filter(
        event_date__gte=start_of_previous_month,
        event_date__lt=start_of_current_month
    ).count()
    if events_last_month > 0:
        ev_percentage_change = ((events_this_month - events_last_month) / events_last_month) * 100
    elif events_this_month > 0:
        ev_percentage_change = events_this_month * 100
    else:
        ev_percentage_change = 0
    locations_this_month = Location.objects.filter(created_at__gte=start_of_current_month).count()
    locations_last_month = Location.objects.filter(
        created_at__gte=start_of_previous_month,
        created_at__lt=start_of_current_month
    ).count()
    if locations_last_month > 0:
        loc_percentage_change = ((locations_this_month - locations_last_month) / locations_last_month) * 100
    elif locations_this_month > 0:
        loc_percentage_change = locations_this_month * 100
    else:
        loc_percentage_change = 0
    locations_by_month = (
    Location.objects
    .annotate(month=TruncMonth('created_at'))
    .values('month')
    .annotate(total=Count('id'))
    .order_by('month')
)
    location_month_count = []
    for entry in locations_by_month:
        month_str = entry['month'].strftime('%m')
        if month_str == "01":
            month_str = "Jan"
        elif month_str == "02":
            month_str = "Feb"
        elif month_str == "03":
            month_str = "Mar"
        elif month_str == "04":
            month_str = "Apr"
        elif month_str == "05":
            month_str = "May"
        elif month_str == "06":
            month_str = "Jun"
        elif month_str == "07":
            month_str = "Jul"
        elif month_str == "08":
            month_str = "Aug"
        elif month_str == "09":
            month_str = "Sep"
        elif month_str == "10":
            month_str = "Oct"
        elif month_str == "11":
            month_str = "Nov"
        elif month_str == "12":
            month_str = "Dec"
        location_month_count.append(
            {
                'month':month_str,
                'count':entry['total']
            }
        )
    events_by_month = (
    Event.objects
    .annotate(month=TruncMonth('event_date'))
    .values('month')
    .annotate(total=Count('id'))
    .order_by('month')
)
    event_month_count = []
    for entry in events_by_month:
        month_str = entry['month'].strftime('%m')
        if month_str == "01":
            month_str = "Jan"
        elif month_str == "02":
            month_str = "Feb"
        elif month_str == "03":
            month_str = "Mar"
        elif month_str == "04":
            month_str = "Apr"
        elif month_str == "05":
            month_str = "May"
        elif month_str == "06":
            month_str = "Jun"
        elif month_str == "07":
            month_str = "Jul"
        elif month_str == "08":
            month_str = "Aug"
        elif month_str == "09":
            month_str = "Sep"
        elif month_str == "10":
            month_str = "Oct"
        elif month_str == "11":
            month_str = "Nov"
        elif month_str == "12":
            month_str = "Dec"
        event_month_count.append(
            {
                'month':month_str,
                'count':entry['total']
            }
        )
    print("Evenimente per luni: ", event_month_count)
    print("Evenimente si loc lor: ", event_locations)
    budget = Budget.objects.first()
    context= {
        'budget':budget,
        'event_month_count':json.dumps(event_month_count),
        'location_month_count':json.dumps(location_month_count),
        'loc_percentage_change':loc_percentage_change,
        'ev_percentage_change':ev_percentage_change,
        'events':events,
        'budget':budget,
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
def admin_edit_location(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")
    location = Location.objects.get(id=pk)
    pictures = LocationImages.objects.filter(location=location)
    types = Type.objects.all()
    organizers = Profile.objects.filter(
    user__is_superuser=False, 
    user_type="organizer"
).exclude(user__username="defaultuser").select_related('user')
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        organizer = request.POST.get('organizer')
        County = request.POST.get('County')
        selected_types = request.POST.getlist('category')  
        image = request.FILES.get('image')  
        location.name = name
        location.description = description
        location.location = County
        current_types = location.types.all()
        for type_name in selected_types:
            type_obj = Type.objects.get(name=type_name)
            if type_obj not in current_types:
                location.types.add(type_obj)  

        for type_obj in current_types:
            if type_obj.name not in selected_types:
                location.types.remove(type_obj)
        location.save()
        if image:
            LocationImages.objects.create(
                location=location,
                image=image
            )

    messages.success(request, "Location updated successfully!")

    context={
        'organizers':organizers,
        'types':types,
        'pictures':pictures,
        'location':location
    }
    return render(request, 'base/admin-edit-location.html',context)

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
    error_pas = False
    ip_address = request.META.get('REMOTE_ADDR', '')
    user = request.user
    profile = user.profile_set.first()
    if request.method == 'POST':
        form_type = request.POST.get('form_type', '')
        if form_type == 'form_1':
            profile_photo = request.FILES.get('profile_photo')
            if profile_photo:
                profile.photo = profile_photo
            firstname = request.POST.get('firstName')
            lastname = request.POST.get('lastName')
            email = request.POST.get('email')
            username = request.POST.get('username')
            phone = request.POST.get('phone')
            location = request.POST.get('location')
            address = request.POST.get('address')
            zipcode = request.POST.get('zipCode')
            user.first_name = firstname
            profile.first_name = firstname
            user.last_name = lastname
            profile.last_name = lastname
            user.email = email
            profile.email = email
            user.username = username
            profile.username = username
            profile.number = phone
            profile.location = location
            profile.street = address
            profile.zip_code = zipcode
            user.save()
            profile.save()
            return redirect('admin_account_settings')
        elif form_type == 'form_2':
            email = request.POST.get('newEmail')
            user.email = email
            profile.email = email
            user.save()
            profile.save()
            return redirect('admin_account_settings')
        elif form_type == 'form_4':
            action = request.POST.get('action')
            linkedin = request.POST.get('linkedin')
            facebook = request.POST.get('facebook')
            google = request.POST.get('google')
            profile = profile
            if action == "connect_linkedin":
                profile.work_link = linkedin
            elif action == "disconnect_linkedin":
                profile.work_link = ""
            elif action == "connect_google":
                profile.google_link = google
            elif action == "disconnect_google":
                profile.google_link = ""
            elif action == "connect_facebook":
                profile.facebook = facebook
            elif action == "disconnect_facebook":
                profile.facebook = ""
            profile.save()
            return redirect('admin_account_settings')
            print("Profil: ", request.profile)
            action = request.POST.get('action')
            linkedin = request.POST.get('linkedin')
            facebook = request.POST.get('facebook')
            google = request.POST.get('google')
            if action == "connect_linkedin":
                profile.work_link = linkedin
            if action == "disconnect_linkedin":
                profile.work_link = ""
            if action == "connect_google":
                profile.google_link = google
            if action == "disconnect_google":
                profile.google_link = ""
            if action == "connect_facebook":
                profile.facebook = facebook
            if action == "disconnect_facebook":
                profile.facebook = ""
            profile.save()
            return redirect('admin_account_settings')
        elif form_type == 'form_5':
            request.user.delete()
            request.profile.delete()
            return redirect('')
        elif form_type == 'form_3':
            print(request.POST)
            password = request.POST.get('currentPassword', '')
            if check_password(password, request.user.password):
                new_pass = request.POST.get('newPassword')
                confirm_new_pas = request.POST.get('confirmNewPassword')
                if new_pass != None and confirm_new_pas != None:
                    if new_pass == confirm_new_pas:
                        user.set_password(new_pass)
                        user.save()
                        return redirect('login')
                    else:
                        error_pas = True
                else:
                    error_pas = True
            else:
                error_pas = True

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
        'devices':devices,
        'error_pas':error_pas
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
            Notification.objects.create(
                user=request.user,
                action_type='created_location',
                target_object_id=location.id,
                target_object_name=location.name,
                target_model='Location'
            ) 
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
            Notification.objects.create(
                user=request.user,
                action_type='updated_location',
                target_object_id=location.id,
                target_object_name=location.name,
                target_model='Location'
            )
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
    today = datetime.today().date()
    for event in events:
        location_counts[event.location.name] += 1
    detailed_locations = [{'location_name': loc.name, 'ev_count': location_counts[loc.name]} for loc in locations] 
    notifications = Notification.objects.filter(user=user).order_by('-timestamp')[:10]
    context = {
        'notifications':notifications,
        'today':today,
        'detailed_locations':detailed_locations,
        'locations':locations,
        'count_events':count_events,
        'count_locations':count_locations,
        'last_login':last_login,
        'user':user,
        'events':events,
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
    location = Location.objects.filter(owner=request.user)
    print("Locatie:", location)

    events = Event.objects.filter(location__in=location)
    print("Events:", events)

    profiles = Profile.objects.get(user=request.user)

    current_date = datetime.today()

    past_events = Event.objects.filter(event_date__lte = current_date).order_by('event_date')

    upcoming_events = Event.objects.filter(event_date__gte = current_date, location__in=location).order_by('event_date')

    next_event = upcoming_events.first() if upcoming_events.exists() else None

    remaining_events = upcoming_events[1:] if upcoming_events.count() > 1 else []

    if next_event:
        next_event_data = [
        {
            'id': next_event.id,
            'title': next_event.event_name,
            'event_date': datetime.combine(next_event.event_date, next_event.event_time).strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    else:
        next_event_data = None

    if remaining_events:
        remaining_events_data = [
            {
                'id': event.id,
                'title': event.event_name,
                'event_date': datetime.combine(event.event_date, event.event_time).strftime('%Y-%m-%d %H:%M:%S')
            }
            for event in remaining_events
        ]
    else:
        remaining_events_data = None

    context = {
        'events': events,
        'past_events': past_events,
        'event_data': json.dumps(next_event_data),
        'remaining_events_data': remaining_events_data,
        'event': next_event,
        'remaining_events': remaining_events,
        'profile': profiles,
        }

    return render(request, 'base/personal_eveniment_home.html', context)


@login_required(login_url='/login')
@user_is_staff
def personal_profile(request):
    location_owned = Location.objects.filter(owner=request.user).first()
    profile = Profile.objects.get(user = request.user)
    location_images = LocationImages.objects.filter(location=location_owned)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'form1':
            location_owned.name = request.POST.get('name')
            request.user.email = request.POST.get('email')
            profile.email = request.POST.get('email')
            profile.number = request.POST.get('number')
            location_owned.location = request.POST.get('adress')
            profile.save()
            location_owned.save()

        elif form_type == 'form2':
            form = LocationEventTypesForm(request.POST, instance=location_owned)
            if form.is_valid():
                form.save()
            location_owned.description = request.POST.get('description')
            location_owned.seats_numbers = request.POST.get('number') or 0
            location_owned.save()

        elif form_type == 'formSocials':
            profile.facebook = request.POST.get('facebook')
            profile.work_link = request.POST.get('website')
            profile.save()
    else:
        form_type = LocationEventTypesForm()


    form_types = LocationEventTypesForm()
    location_owned = Location.objects.filter(owner=request.user).first()
    profile = Profile.objects.filter(user = location_owned.owner).first()

    context = {
        'location_data':location_owned,
        'profile':profile,
        'location_images':location_images,
        'form': form_types
    }
    return render(request, 'base/personal_profile.html', context)


@login_required(login_url='/login')
@user_is_staff
def upload_images(request):
    location_owned = Location.objects.get(owner=request.user)
    if request.method == 'POST' and request.FILES.getlist('images'):
        images = request.FILES.getlist('images')
        for image in images:
            LocationImages.objects.create(location=location_owned, image=image)
        return redirect('personal_profile') 


@login_required(login_url='/login')
@user_is_staff
def delete_image(request, image_id):
    if request.method == "POST":
        image = get_object_or_404(LocationImages, id=image_id)
        image.delete()
        return JsonResponse({"status": "success"}, status=200)
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required(login_url='/login')
@user_is_staff
def personal_vizualizare_eveniment(request, pk):
    event = Event.objects.get(id=pk)

    if event.location.owner != request.user:
        return redirect(request.META.get('HTTP_REFERER', '/'))
        
    profile = Profile.objects.get(user=request.user)
    rspv = RSVP.objects.filter(event = event, response = "Accepted")

    event_data = [
        {
            'id': event.id,
            'title': event.event_name,
            'event_date': datetime.combine(event.event_date, event.event_time).strftime('%Y-%m-%d %H:%M:%S')
        }
    ]   
    
    context = {
        'event': event,
        'event_data': json.dumps(event_data),
        'rspv': rspv,
        'profile': profile
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
def personal_face_id(request, pk):
    event = Event.objects.get(id=pk)
    context = {
        'event': event
    }
    return render(request, 'base/personal_face_id.html', context)


def find_user_view(request):
    if is_ajax(request):
        photo = request.POST.get('photo')
        _, str_img = photo.split(';base64')

        # print(photo)
        decoded_file = base64.b64decode(str_img)

        x = Log()
        x.photo.save('upload.png', ContentFile(decoded_file))
        x.save()

        try:
            res = classify_face(x.photo)
            print(f"Rezultatul clasificării: {res}")  # Debugging
            
            if res:
                user_exists = User.objects.filter(username=res).exists()
                print(f"User exists: {user_exists}")  # Debugging
                
                if user_exists:
                    user = User.objects.get(username=res)
                    profile = Profile.objects.get(user=user)
                    x.profile = profile
                    x.save()
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'User not found'})
            else:
                return JsonResponse({'success': False, 'error': 'Face recognition failed'})

        except Exception as e:
            print(f"Eroare la clasificare: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    

@login_required(login_url='/login')
@user_is_guest
def guest_profile(request):

    profil = Profile.objects.get(user = request.user)
    preferences = Guests.objects.get(profile = profil)
    not_completed = Guests.objects.filter(profile__user=request.user, state=False).exists()

    if request.method == "POST":
        if not_completed:
            preferences.state = True
            profil.first_name = request.POST.get('firstname')
            profil.last_name = request.POST.get('lastname')
            profil.email = request.POST.get('email')
            profil.age = request.POST.get('age')
            profil.photo = request.FILES.get('photo')
            preferences.gender = request.POST.get('gender')
            preferences.cuisine_preference = request.POST.get('meniu')
            preferences.vegan = request.POST.get('vegan_check') == '1'
            preferences.allergens = request.POST.getlist('allergens')

            preferences.save()
            profil.save()
        else:
            form_type = request.POST.get('form_type')
            if form_type == 'form1':
                profil.first_name = request.POST.get('firstname')
                profil.last_name = request.POST.get('lastname')
                profil.user.email = request.POST.get('email')
                profil.email = request.POST.get('email') 
                if 'photo' in request.FILES:
                    profil.photo = request.FILES.get('photo')
                profil.number = request.POST.get('number')

                profil.save()
                profil.user.save()
                
            elif form_type == 'form2':
                preferences.cuisine_preference = request.POST.get('meniu')
                preferences.vegan = request.POST.get('vegan_check') == '1'
                preferences.allergens = request.POST.getlist('allergens')
                preferences.save()

            
    not_completed = Guests.objects.filter(profile__user=request.user, state=False).exists()
    
    context = {
        "not_completed": not_completed,
        "preferences": preferences,
        "profile": profil
    }            

    return render(request, 'base/guest_profile.html', context)


@login_required(login_url='/login')
@user_is_guest
def guest_home(request):
    profil = Profile.objects.get(user = request.user)
    preferences = Guests.objects.get(profile = profil)

    rsvp = RSVP.objects.filter(guest = request.user)

    next_rsvp = rsvp.first() if rsvp.exists() else None
    other_rsvp = rsvp[1:] if rsvp.count() > 1 else []
    
    next_event = None
    event_data = []

    if next_rsvp is not None:
        next_event = next_rsvp.event

        event_data = [
            {
                'id': next_event.id,
                'title': next_event.event_name,
                'event_date': datetime.combine(next_event.event_date, next_event.event_time).strftime('%Y-%m-%d %H:%M:%S')
            }
        ] 

    not_completed = Guests.objects.filter(profile__user=request.user, state=False).exists()

    context = {
        "not_completed": not_completed,
        "preferences": preferences,
        "profile": profil,
        "rsvp": next_rsvp,
        "other_rsvp": other_rsvp,
        "event": next_event,
        "event_data": json.dumps(event_data)
    }

    if not_completed:
        return redirect('guest_profile')
    else:
        return render(request, 'base/guest_home.html', context)


@login_required(login_url='/login')
@user_is_guest
def guest_event_view(request, pk):
    
    event=Event.objects.get(id=pk)
    rsvp = RSVP.objects.get(event=event, guest=request.user)
    profile=Profile.objects.get(user=request.user)
    preferences = Guests.objects.get(profile = profile)

    print(rsvp)

    if request.method == "POST":
        print(request.POST)
        value = request.POST.get("response")
        print(value)
        if value in ["Accepted", "Declined"]:
            rsvp.response = value
            rsvp.save() 

    rsvp = RSVP.objects.get(event=event, guest=request.user)
    print(rsvp)

    event_data = [
        {
            'id': event.id,
            'title': event.event_name,
            'event_date': datetime.combine(event.event_date, event.event_time).strftime('%Y-%m-%d %H:%M:%S')
        }
    ]

    context={
        'event':event,
        'profile':profile,
        'preferences':preferences,
        'event_data': json.dumps(event_data),
        'rsvp':rsvp
    }
    return render(request,'base/guest_event_view.html', context)


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


@login_required(login_url='/login')
def send_notification(request):
    if request.method == 'POST':
        sender = request.user
        message = request.POST.get('message')
        receiver = request.POST.get('receiver')
        event_id = request.POST.get('event_id')
        event = Event.objects.get(id=int(event_id))

        if receiver == "everyone":
            rsvp_list = RSVP.objects.filter(event=event, response="Accepted")
            for rsvp in rsvp_list:
                EventNotification.objects.create(
                    sender=sender,
                    event=event,
                    receiver=rsvp.guest,
                    message=message
                )
        receiver = event.organized_by
        EventNotification.objects.create(sender=sender, receiver=receiver, event=event ,message=message)
    return redirect('personal_eveniment_home')


@login_required(login_url='/login')
def get_notifications(request):
    profil = Profile.objects.get(user = request.user)
    user_type = profil.user_type
    if profil.user_type == "guest":
        rsvp = RSVP.objects.filter(guest = request.user, response = "Accepted").values_list('event', flat=True)
        notifications = EventNotification.objects.filter(event__in=rsvp, receiver=request.user, is_read="False").order_by('-timestamp')
    elif profil.user_type == "staff":
        events = Event.objects.filter(location__owner = request.user)
        notifications = EventNotification.objects.filter(Q(receiver=request.user), ~Q(sender=request.user), event__in=events, is_read="False").order_by('-timestamp')
        print(notifications)
        for n in notifications:
            print(f"Notification ID: {n.id}, Event: {n.event}")

    notifications_data = [
        {
            "id": n.id, 
            "message": n.message, 
            "timestamp": n.timestamp.strftime("%Y-%m-%d %H:%M"),
            "event_id":n.event.id if n.event else None,
            "user_type": user_type,
        }
        for n in notifications
    ]
    return JsonResponse({"notifications": notifications_data}) 


@login_required
def mark_notifications_as_read(request):
    if request.method == 'POST':
        EventNotification.objects.filter(receiver=request.user, is_read=False).update(is_read=True)
        print("Succes")
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)



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

