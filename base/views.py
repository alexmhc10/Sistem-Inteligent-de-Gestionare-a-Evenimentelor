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
from django.db.models import Count, Avg
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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, Location
from .forms import EventForm
from django.db.models import Avg
from django.db.models import Exists, OuterRef, Value
from .models import EventNotification
from django.views import View
import face_recognition as face_recognition
import cv2
import winsound
import numpy as np
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from .table_arrangement_algorithm import TableArrangementAlgorithm
from django.views.decorators.http import require_GET
from django.forms import modelformset_factory
import joblib
from django.utils.decorators import method_decorator
import os
from .models import EventBudget
from .recommender import get_recommendations_for_guest, get_similar_dishes_for_dish, get_recommender
from .constants import TEMP_CHOICES, TEXTURE_CHOICES, NUTRITION_GOAL_CHOICES, DIET_CHOICES, REGION_CHOICES, COOKING_METHOD_CHOICES



class NotificationView(View):
    def get(self, request):
        # Filtrăm notificările pentru utilizatorul conectat
        notifications = EventNotification.objects.filter(receiver=request.user).order_by('-timestamp')  # Ordonați după dată, cele mai recente primele
        
        # Poți filtra și notificările necitite, dacă dorești
        unread_notifications = notifications.filter(is_read=False)
        
        return render(request, 'home-organizer.html', {
            'notifications': notifications,  # Trimiți notificările în template
        })


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('event_details', event_id=event.id)  
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EventForm(instance=event)

    return render(request, 'base/edit_event.html', {'form': form, 'event': event})




from django.db.models import Q

def locations_list(request):
    locations = Location.objects.all()

    # Obținem parametrii din query string
    search = request.GET.get('search', '').strip()
    min_seats = request.GET.get('min_seats', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    # Aplicăm filtrele
    if search:
        locations = locations.filter(name__icontains=search)

    if min_seats:
        try:
            locations = locations.filter(seats_numbers__gte=int(min_seats))
        except ValueError:
            pass  # ignori inputuri invalide

    if max_price:
        try:
            locations = locations.filter(cost__lte=float(max_price))
        except ValueError:
            pass

    context = {
        'locations': locations,
        'search': search,
        'min_seats': min_seats,
        'max_price': max_price
    }
    return render(request, 'base/locations_list.html', context)



def home_organizer(request):
    events = Event.objects.all()
    upcoming_events_raw = events.filter(organized_by=request.user, event_date__gte=timezone.now()).order_by('event_date')[:5]
    
    upcoming_events = []
    for event in upcoming_events_raw:
        upcoming_events.append({
            'title': event.event_name,
            'time': event.event_time.strftime('%H:%M') if event.event_time else 'All Day',
            'date': event.event_date.strftime('%b %d'),
            'id': event.id
        })
    
    notifications = EventNotification.objects.filter(
        receiver=request.user
    ).order_by('-timestamp').select_related('sender', 'event')[:10]
    
    unread_notifications = [n for n in notifications if not n.is_read]
    if unread_notifications:
        unread_ids = [n.id for n in unread_notifications]
        EventNotification.objects.filter(id__in=unread_ids).update(is_read=True)
        for notification in notifications:
            if not notification.is_read:
                notification.is_read = True

    from django.db.models import Count
    from collections import Counter
    
    popular_categories = []
    event_types = events.values_list('types__name', flat=True).exclude(types__name__isnull=True)
    type_counts = Counter(event_types)
    
    for type_name, count in type_counts.most_common(5):
        if type_name:  # Exclude None values
            popular_categories.append({
                'name': type_name,
                'count': count,
                'percentage': round((count / events.count()) * 100, 1) if events.count() > 0 else 0
            })
    
    # If no categories found, add some default ones
    if not popular_categories:
        popular_categories = [
            {'name': 'Wedding', 'count': 15, 'percentage': 35.0},
            {'name': 'Corporate', 'count': 12, 'percentage': 28.0},
            {'name': 'Birthday', 'count': 8, 'percentage': 19.0},
            {'name': 'Conference', 'count': 5, 'percentage': 12.0},
            {'name': 'Anniversary', 'count': 3, 'percentage': 7.0},
        ]

    # Calculate recent performance data
    from datetime import timedelta
    
    # Get events from last 6 months
    six_months_ago = timezone.now() - timedelta(days=180)
    recent_events = events.filter(event_date__gte=six_months_ago, organized_by=request.user)
    
    # Calculate monthly performance
    recent_performance = []
    for i in range(6):
        month_start = timezone.now() - timedelta(days=30 * (i + 1))
        month_end = timezone.now() - timedelta(days=30 * i)
        
        month_events = recent_events.filter(event_date__gte=month_start, event_date__lt=month_end)
        month_participants = sum(event.guests.count() for event in month_events)
        
        # Calculate success rate (completed events / total events)
        completed_events = month_events.filter(completed=True).count()
        total_month_events = month_events.count()
        success_rate = round((completed_events / total_month_events) * 100, 1) if total_month_events > 0 else 0
        
        # Only add months with activity (events > 0)
        if total_month_events > 0:
            recent_performance.append({
                'month': month_start.strftime('%B'),
                'events': total_month_events,
                'participants': month_participants,
                'success_rate': success_rate,
                'revenue': sum(event.cost for event in month_events.filter(completed=True)) if month_events.filter(completed=True).exists() else 0
            })
    
    # Reverse to show oldest to newest
    recent_performance.reverse()
    
    # If no real data, add sample data (only months with activity)
    if len(recent_performance) == 0:
        recent_performance = [
            {'month': 'April', 'events': 1, 'participants': 1, 'success_rate': 100.0, 'revenue': 3000},
            {'month': 'May', 'events': 1, 'participants': 2, 'success_rate': 100.0, 'revenue': 3000},
        ]

    # Calculate organizer rating
    from django.db.models import Avg
    organizer_reviews = Review.objects.filter(organizer=request.user)
    average_rating = organizer_reviews.aggregate(Avg('organizer_stars'))['organizer_stars__avg']
    
    # Format rating to 1 decimal place or show N/A if no reviews
    if average_rating is not None:
        formatted_rating = round(average_rating, 1)
    else:
        formatted_rating = "N/A"

    # Calculate revenue analytics
    from decimal import Decimal
    organizer_events = events.filter(organized_by=request.user)
    
    # Monthly revenue data for last 6 months
    revenue_analytics = []
    total_revenue = Decimal('0')
    total_costs = Decimal('0')
    
    for i in range(6):
        month_start = timezone.now() - timedelta(days=30 * (i + 1))
        month_end = timezone.now() - timedelta(days=30 * i)
        
        month_events = organizer_events.filter(event_date__gte=month_start, event_date__lt=month_end, completed=True)
        
        # Calculate revenue (from completed events)
        month_revenue = sum(event.cost for event in month_events) if month_events.exists() else Decimal('0')
        
        # Calculate estimated costs (30% of revenue as operational costs)
        month_costs = month_revenue * Decimal('0.3')
        
        # Calculate profit
        month_profit = month_revenue - month_costs
        
        total_revenue += month_revenue
        total_costs += month_costs
        
        if month_revenue > 0:  # Only add months with revenue
            revenue_analytics.append({
                'month': month_start.strftime('%B'),
                'revenue': float(month_revenue),
                'costs': float(month_costs),
                'profit': float(month_profit),
                'events_count': month_events.count()
            })
    
    # Reverse to show oldest to newest
    revenue_analytics.reverse()
    
    # If no real data, add sample data
    if len(revenue_analytics) == 0:
        revenue_analytics = [
            {'month': 'April', 'revenue': 3000, 'costs': 900, 'profit': 2100, 'events_count': 1},
            {'month': 'May', 'revenue': 3000, 'costs': 900, 'profit': 2100, 'events_count': 1},
        ]
        total_revenue = Decimal('6000')
        total_costs = Decimal('1800')
    
    total_profit = total_revenue - total_costs

    # --- NEW STATISTICS FOR QUICK STATS CARD ---
    # Number of distinct locations/cities where organizer has held events
    events_cities = organizer_events.exclude(location__isnull=True).values_list('location__location', flat=True).distinct().count()
    
    # Date of the most recent event
    last_event_obj = organizer_events.order_by('-event_date').first()
    last_event_date = last_event_obj.event_date.strftime('%d.%m.%Y') if last_event_obj else 'N/A'

    # Positive feedback percentage (reviews with 4 or 5 stars)
    total_reviews = organizer_reviews.count()
    positive_reviews = organizer_reviews.filter(organizer_stars__gte=4).count()
    positive_feedback = round((positive_reviews / total_reviews) * 100) if total_reviews > 0 else 0
    # -------------------------------------------------

    context = {
        'total_events': events.count(),
        'total_participants': sum(event.guests.count() for event in events),
        'acceptance_rate': 85,
        'average_feedback': 4.7,
        'average_rating': formatted_rating,
        'today_date': datetime.now().strftime('%B %d, %Y'),
        'upcoming_events': upcoming_events,
        'notifications': notifications,
        'popular_categories': popular_categories,
        'recent_performance': recent_performance,
        'revenue_analytics': revenue_analytics,
        'total_revenue': float(total_revenue),
        'total_costs': float(total_costs),
        'total_profit': float(total_profit),
        # NEW stats for quick stats card
        'events_cities': events_cities,
        'last_event_date': last_event_date,
        'positive_feedback': positive_feedback,
    }
    return render(request, 'base/home-organizer.html', context)


@login_required(login_url='login')
@user_is_organizer
def financial_management(request):
    """View pentru managementul financiar al organizatorului"""
    from decimal import Decimal
    
    # Obține evenimentele organizatorului
    organizer_events = Event.objects.filter(organized_by=request.user)
    
    # Calculează statistici financiare
    total_revenue = Decimal('0')
    total_pending = Decimal('0')
    completed_events = organizer_events.filter(completed=True)
    pending_events = organizer_events.filter(completed=False, is_canceled=False)
    
    # Calculează veniturile totale din evenimente completate
    for event in completed_events:
        total_revenue += event.cost
    
    # Calculează veniturile în așteptare
    for event in pending_events:
        total_pending += event.cost
    
    # Calculează costurile estimate (30% din venituri)
    total_costs = total_revenue * Decimal('0.3')
    net_profit = total_revenue - total_costs
    
    # Tranzacții recente (simulat pentru demo)
    recent_transactions = []
    for event in completed_events.order_by('-event_date')[:5]:
        recent_transactions.append({
            'date': event.event_date,
            'description': f'Payment for {event.event_name}',
            'amount': float(event.cost),
            'type': 'income',
            'status': 'completed'
        })
    
    # Informații card (simulat)
    card_info = {
        'card_number': '**** **** **** 1234',
        'card_type': 'Visa',
        'balance': float(net_profit),
        'available_for_withdrawal': float(net_profit * Decimal('0.8'))  # 80% disponibil pentru retragere
    }
    
    context = {
        'total_revenue': float(total_revenue),
        'total_pending': float(total_pending),
        'total_costs': float(total_costs),
        'net_profit': float(net_profit),
        'recent_transactions': recent_transactions,
        'card_info': card_info,
        'completed_events_count': completed_events.count(),
        'pending_events_count': pending_events.count(),
    }
    
    return render(request, 'base/financial_management.html', context)


@login_required
def guest_list(request, event_id):
    event = get_object_or_404(
        Event.objects.prefetch_related('guests__profile'),  
        id=event_id
    )
    return render(request, 'base/guest_list.html', {
        'event': event,
        'guests': event.guests.all()  
    })

def event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    tables = list(event.location.tables.values(
        'id', 'table_number', 'capacity', 'shape', 'is_reserved',
        'position_x', 'position_y', 'rotation', 'width', 'height', 'radius'
    )) if event.location else []
    special_elements = list(event.location.special_elements.values(
        'type','label','position_x','position_y','rotation','width','height','radius'
    )) if event.location else []
    budget = getattr(event, 'eventbudget', None)
    total_invites = event.rsvps.count()
    accepted_invites = event.rsvps.filter(response='Accepted').count()
    pending_invites = event.rsvps.filter(response='Pending').count()
    declined_invites = event.rsvps.filter(response='Declined').count()

    guest_count = event.guests.count()
    seated_count = event.table_arrangements.count()
    unseated_count = guest_count - seated_count if guest_count >= seated_count else 0

    show_arrangement = False
    if event.location:
        if event.location.tables.exists() or event.location.name.lower() in ["perla cosaului", "romanita"]:
            show_arrangement = True

    context = {
        'event': event,
        'tables_json': json.dumps(tables),
        'special_json': json.dumps(special_elements),
        'budget': budget,
        'total_invites': total_invites,
        'accepted_invites': accepted_invites,
        'pending_invites': pending_invites,
        'declined_invites': declined_invites,
        'guest_count': guest_count,
        'seated_count': seated_count,
        'unseated_count': unseated_count,
        'show_arrangement': show_arrangement,
    }
    return render(request, 'base/event_details.html', context)

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


@login_required
def organizer_profile(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    reviews = Review.objects.filter(organizer=profile.user).order_by('-created_at')
    average_rating = reviews.aggregate(models.Avg('organizer_stars'))['organizer_stars__avg'] or 0
    star_range = range(1, 6)

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

    return render(request, 'base/organizer_profile.html', {
        'profile': profile,
        'form': form,
        'reviews': reviews,
        'average_rating': average_rating,
        'star_range': star_range
    })






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


def event_builder(request):
    locations = Location.objects.all()

    if request.method == 'POST':
        form = EventForm(request.POST)
        form_file = UploadFileForm(request.POST, request.FILES)

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

            # Dacă a fost încărcat și un fișier cu invitați, îl procesăm
            if request.FILES.get('guest_file'):
                uploaded_file = request.FILES['guest_file']
                fs = FileSystemStorage()
                filename = fs.save(uploaded_file.name, uploaded_file)
                file_path = fs.path(filename)

                try:
                    if filename.endswith('.csv'):
                        df = pd.read_csv(file_path)
                    elif filename.endswith(('.xls', '.xlsx')):
                        df = pd.read_excel(file_path)
                    else:
                        raise ValueError('Format de fișier invalid')
                except Exception as e:
                    return render(request, 'event_builder.html', {
                        'error': f"Fișierul invitați nu poate fi citit: {e}",
                        'form': form,
                        'form_file': form_file,
                        'locations': locations
                    })

                # Procesăm invitații din fișier
                invited_guests = []
                for _, row in df.iterrows():
                    name = row.get('nume')
                    email = row.get('email')
                    phone = row.get('telefon')

                    if name and email:
                        username = name.replace(" ", "")
                        counter = 1
                        while User.objects.filter(username=username).exists():
                            username = f"{username}{counter}"
                            counter += 1
                        user, created = User.objects.get_or_create(username=username, email=email)
                        if created:
                            user.set_password(phone or "password123")
                            user.save()
                            Profile.objects.create(user=user, username=username, email=email, password=phone or "password123", number=phone, user_type='guest')

                        invited_guests.append(RSVP(guest=user, event=event))

                if invited_guests:
                    RSVP.objects.bulk_create(invited_guests)

        return redirect('my_events')

    else:
        form = EventForm()
        form_file = UploadFileForm()

    # Obținem invitații deja înregistrați ca "guest" pentru a-i afișa în modal
    existing_guests = Profile.objects.filter(user_type='guest')
    guests_with_accounts = [profile.user for profile in existing_guests]  # Userii invitați

    return render(request, 'base/event_builder.html', {
        'form': form,
        'locations': locations,
        'guests': guests_with_accounts,
        'form_file': form_file,
    })



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

from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
#my events
@login_required(login_url='login')
def my_events(request):
    events = Event.objects.filter(organized_by=request.user)

    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if search_query:
        events = events.filter(event_name__icontains=search_query)

    if status_filter:
        if status_filter == 'active':
            events = events.filter(is_canceled=False, completed=False)
        elif status_filter == 'inactive':
            events = events.filter(is_canceled=True)
        elif status_filter == 'completed':
            events = events.filter(completed=True)


    events = events.order_by('-event_date')

    # paginare
    paginator = Paginator(events, 10)  # 10 evenimente pe pagină
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'base/my_events.html', {'events': page_obj})


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

from django.db.models import Avg, Value, FloatField
from django.db.models.functions import Coalesce
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
    average_ratings = Location.objects.annotate(
    rating=Coalesce(Avg('review__location_stars'), Value(0), output_field=FloatField())
).values('name', 'rating')
    print("Average: ", average_ratings)
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
        location_count = Location.objects.filter(types=type,owner__in=organizer_users).count()
        types_with_location_count.append({'type': type.name, 'count': location_count})
    if request.method == 'POST':
        location_id = request.POST.get('location_id')
        del_loc = Location.objects.filter(id=location_id)
        del_loc.delete()
        return redirect('admin-locations')
    context = {
        'average_ratings':average_ratings,
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
    users = User.objects.filter(
    is_superuser=False,
    profile__user_type='organizer'
).exclude(username='defaultuser')

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
    today_date = today.date()
    today_time = today.strftime("%H:%M:%S")
    detailed_incompleted_events = []
    finished_count = 0
    cancelled_count = 0
    for item in detailed_events:
        if item['completed'] :
            finished_count += 1
        elif item['cancelled'] == True:
            cancelled_count += 1
            detailed_incompleted_events.append(item)

    if request.method == 'POST':
        if request.POST.get('form_delete') == 'form_delete':
            event_id = request.POST.get('event_id')
            Event.objects.filter(id=event_id).delete()
            return redirect('admin-events')

        organizer = request.POST.get('organizer')
        event_name = request.POST.get('event_name')
        event_location = request.POST.get('event_location')
        location = Location.objects.get(id=event_location)
        date_str = request.POST.get('event_date')
        print("Data din post: ", date_str)

        event_date = datetime.strptime(date_str, '%d %b, %Y').date()
        print("Data dupa convertire: ", event_date)

        id = request.POST.get('event_id')
        event = Event.objects.get(id=id)
        print("Data evenimentului in formatul ei: ", event.event_date)

        try:
            organizer_user = User.objects.get(id=organizer)
        except User.DoesNotExist:
            organizer_user = None
        print(
            "Nume: ",event_name,"\n"
            "Date: ",event_date,"\n"
            "Location: ",location,"\n"
            "Organizer: ", organizer_user
        )
        event.event_name = event_name
        event.event_date = event_date
        event.location = location
        event.organized_by = organizer_user
        event.save()

        return redirect('admin-events')
    locations = Location.objects.all()
    completed = "completed"
    context = {
        'completed':completed,
        'locations':locations,
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
def admin_optimise_events(request, pk):
    completed = "completed"
    events = Event.objects.all()
    users = User.objects.filter(
    is_superuser=False,
    profile__user_type='organizer'
).exclude(username='defaultuser')

    types = Type.objects.all()
    types_with_event_count = []
    
    for type in types:
        event_count = Event.objects.filter(types=type).count()
        types_with_event_count.append({'type': type.name, 'count': event_count})
    
    events_count = events.count()
    users = User.objects.filter(
    is_superuser=False,
    profile__user_type='organizer'
).exclude(username='defaultuser')
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
    context = {
        'detailed_events':detailed_events,
        'completed':completed,
    }
    return render(request, 'base/optimise_events.html', context)

@login_required(login_url='login')
def admin_view_events(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")
    event = Event.objects.get(id=pk)
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
    events_completed = Event.objects.filter(location=location, completed=True, is_canceled=False)
    today = datetime.today()
    total_event_income = sum(event.cost for event in events_completed)
    created_date = location.created_at.date()
    months_passed = (today.year - created_date.year) * 12 + (today.month - created_date.month)
    months_passed = max(months_passed, 0)
    total_maintenance_cost = Decimal(months_passed) * location.cost
    profit = total_event_income - total_maintenance_cost
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
    loc_images = LocationImages.objects.filter(location=location)
    average_rating = reviews.aggregate(avg=Avg('location_stars'))['avg'] or 0
    average_rating = round(float(average_rating), 1)
    print("rating: ", average_rating)
    ratings = Review.objects.filter(location=location).values('location_stars').annotate(count=Count('location_stars'))
    rating_counts = {i: 0 for i in range(1, 6)}
    total_reviews = 0

    for item in ratings:
        rating_counts[item['location_stars']] = item['count']
        total_reviews += item['count']

    rating_percentages = {
    i: (rating_counts[i] / total_reviews) * 100 if total_reviews else 0
    for i in range(1, 6)
}
    print("Counts: ", rating_counts)
    print("Percentage: ", rating_percentages)
    stars = range(1, 6)
    context = {
        "rating_counts": rating_counts,
        "rating_percentages": rating_percentages,
        'stars':stars,
        'average_rating':average_rating,
        'profit':profit,
        'loc_images':loc_images,
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
    users = User.objects.filter(is_superuser=False, profile__user_type="organizer").exclude(username="defaultuser")
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
                Salary.objects.create(user=user)
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
        if nr_form == "form_4":
            id = request.POST.get('user_id')
            print("ID de sters: ", id)
            user = User.objects.filter(id=id)
            user.delete()
            return redirect('users')
    total_users_accepted = Profile.objects.filter(user_type="organizer", approved=True).count()
    total_users = Profile.objects.filter(user_type="organizer").count()
    user_profiles = {user: user.profile_set.first() for user in users}
    profiles = Profile.objects.filter(user_type="organizer")
    today = now()
    current_year = today.year
    current_month = today.month
    new_this_month = Profile.objects.filter(
        user_type="organizer",
        created_at__year=current_year,
        created_at__month=current_month
    ).count()
    if total_users > 0:
        percent_new = (new_this_month / total_users) * 100
    else:
        percent_new = 0
    user_data = [
    {
        'username': profile.user.username if profile.user else profile.username,
        'salary': float(getattr(profile.user.salary, 'total_salary', 0)) if profile.user else 0
    }
    for profile in profiles
]
    non_acc = Profile.objects.filter(approved=False,user_type="organizer")
    notifications = Notification.objects.all()
    context = {
        'new_this_month': new_this_month,
        'percent_new': percent_new,
        'total_users_accepted': total_users_accepted,
        'total_users': total_users,
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
    profit_by_month = (
        CompanyProfit.objects
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
    profit_month_count = []
    for entry in profit_by_month:
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
        profit_month_count.append(
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
    today = now().date()
    loc_profit = []

    all_locations = Location.objects.all()

    for loc in all_locations:
        events_completed = Event.objects.filter(location=loc, completed=True, is_canceled=False)
        event_count = events_completed.count()
        total_event_income = sum(event.cost for event in events_completed)

        created_date = loc.created_at.date()
        months_passed = (today.year - created_date.year) * 12 + (today.month - created_date.month)
        months_passed = max(months_passed, 0)

        total_maintenance_cost = Decimal(months_passed) * loc.cost
        profit = total_event_income - total_maintenance_cost

        loc_profit.append({
            "location": loc,
            "event_count": event_count,
            "profit": profit
        })

    top_locations = sorted(loc_profit, key=lambda x: x["profit"], reverse=True)[:5]
    print("Cele mai bune loc: ", top_locations)
    for location in locations:
        print("Loc locatii: ", location.location)
    context= {
        'top_locations':top_locations,
        'loc_profit':loc_profit,
        'budget':budget,
        'event_month_count':json.dumps(event_month_count),
        'location_month_count':json.dumps(location_month_count),
        'profit_month_count':json.dumps(profit_month_count),
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
        if guest.diet_preference != 'none':
            available_dishes = [dish for dish in available_dishes if dish.diet_type == guest.diet_preference]
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
    try:
        location = Location.objects.get(pk=pk)  # Căutăm locația pe baza id-ului (pk)
    except Location.DoesNotExist:
        raise Http404("Location does not exist")  # Aruncăm o eroare dacă locația nu există
    
    reviews = location.review_set.all()
    
    if request.method == 'POST':
        review = Review.objects.create(
            user=request.user,
            location=location,
            comment=request.POST.get('comment'),
            stars=request.POST.get('rating')
        )
        return redirect('location', pk=location.pk)  # Redirecționăm la pagina locației

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
            
            # Create unique staff user account
            base_username = f"{location.name.replace(' ', '_').lower()}_staff"
            username = base_username
            counter = 1
            from django.contrib.auth.models import User
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            email = f"{username}@eventplanner.com"
            password = location.number  # Using the location's phone number as password
            
            # Create user account
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=location.name,
                is_active=True
            )
            
            # Create profile with user_type='staff'
            Profile.objects.create(
                user=user,
                username=username,
                password=password,
                email=email,
                user_type='staff'
            )
            
            # Link user account to location
            location.user_account = user
            location.save()

            Notification.objects.create(
                user=request.user,
                action_type='created_location',
                target_object_id=location.id,
                target_object_name=location.name,
                target_model='Location'
            ) 

            custom_types = form.cleaned_data.get('custom_types') or []
            if custom_types:
                for type_name in custom_types:
                    type_instance, _ = Type.objects.get_or_create(name=type_name.strip()) 
                    location.types.add(type_instance)
            else:
                selected_types = form.cleaned_data.get('types')
                for type_instance in selected_types:
                    location.types.add(type_instance)

            # Return modal with credentials
            context = {
                'form': LocationForm(),
                'types': types,
                'show_success_modal': True,
                'staff_username': username,
                'staff_password': password
            }
            return render(request, 'base/location_form.html', context)
        else:
            print(form.errors)  # Debug invalid form

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
    location = Location.objects.get(user_account=request.user)
    print("Locatie:", location)
    print("Locatie:", location.id)

    events = Event.objects.filter(location=location)
    print("Events:", events)

    profiles = Profile.objects.get(user=request.user)
    print(profiles.user_type)
    
    current_date = datetime.today() 

    past_events = [ev for ev in events if ev.status == 'completed'] or []
    print("Evente din trecut", past_events)
    
    upcoming_events = Event.objects.filter(event_date__gte = current_date, location=location).order_by('event_date')

    next_event = upcoming_events.first() if upcoming_events.exists() else None
    print("Primul event urmator", next_event)

    remaining_events = upcoming_events[1:] if upcoming_events.count() > 1 else []
    print("Eventuri ramase", remaining_events)

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
        'past_events_count': len(past_events),
        'event_data': json.dumps(next_event_data),
        'remaining_events_data': remaining_events_data,
        'event': next_event,
        'remaining_events': remaining_events,
        'profile': profiles,
        }

    return render(request, 'base/personal_eveniment_home.html', context)


def event_list_json(request):
    location = Location.objects.get(user_account=request.user)
    events = Event.objects.filter(location=location)
    event_data = []
    print("Found events:", events.count())

    for event in events:
        event_data.append({
            'title': event.event_name,
            'start': format(event.event_date, 'Y-m-d'),
            'url': f'/personal_vizualizare_eveniment/{event.id}',
        })
    print("Event data:", event_data)
    return JsonResponse(event_data, safe=False)


TableFormSet = modelformset_factory(Table, form=TableForm, extra=1, can_delete=True)

@login_required(login_url='/login')
@user_is_staff
def personal_profile(request):
    location_owned = Location.objects.filter(user_account=request.user).first()
    print(location_owned)
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
            profile.instagram = request.POST.get('instagram')
            profile.save()
        
        elif form_type == 'formTable':
            formset = TableFormSet(request.POST)
            if formset.is_valid():
                tables = formset.save(commit=False)
                for table in tables:
                    table.location = location_owned
                    table.save()
    else:
        form_type = LocationEventTypesForm(instance=location_owned)
        formset = TableFormSet(queryset=Table.objects.none())

    formset = TableFormSet(queryset=Table.objects.none())
    form_types = LocationEventTypesForm(instance=location_owned)
    location_owned = Location.objects.filter(user_account=request.user).first()
    profile = Profile.objects.filter(user = location_owned.user_account).first()

    context = {
        'location_data':location_owned,
        'profile':profile,
        'location_images':location_images,
        'form': form_types,
        'formset': formset
    }
    return render(request, 'base/personal_profile.html', context)


@login_required
def get_tables_for_location(request, location_id):
    tables_location = Location.objects.get(id=location_id)
    tables = Table.objects.filter(location=tables_location).values(
        'id', 'table_number', 'capacity', 'shape', 'notes'
    )
    return JsonResponse(list(tables), safe=False)


@login_required(login_url='/login')
@user_is_staff
def upload_images(request):
    location_owned = Location.objects.get(user_account=request.user)
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
    event_guests = event.guests.all()
    print('Event guests:', event.id)

    if event.location.user_account != request.user:
        messages.error(request, "Acces denied: You cant acces events that are not organised at your location.")
        return redirect(request.META.get('HTTP_REFERER', '/login/'))
    
    if event.status == "completed":
        messages.error(request, "This event is completed!.")
        return redirect('completed_event', pk)

        
    profile = Profile.objects.get(user=request.user)
    rspv = RSVP.objects.filter(event = event, response = "Accepted")
    rspv_pending = RSVP.objects.filter(event = event, response = "Pending")
    print('RSPV:', rspv)
    logs = Log.objects.filter(event=event, is_correct = True)
    print('Logs:', logs)

    event_data = [
        {
            'id': event.id,
            'title': event.event_name,
            'event_date': datetime.combine(event.event_date, event.event_time).strftime('%Y-%m-%d %H:%M:%S')
        }
    ]   
    
    guests_menu = GuestMenu.objects.filter(event=event)
    print('Guests Menu:', guests_menu)

    tables_json = []
    special_json = []
    if event.location:
        tables_json = list(event.location.tables.values('id','table_number','capacity','shape','is_reserved','position_x','position_y','rotation','width','height','radius'))
        special_json = list(event.location.special_elements.values('type','label','position_x','position_y','rotation','width','height','radius'))

    # Map guests to their assigned table numbers
    arrangements = TableArrangement.objects.filter(event=event).select_related('guest', 'table')
    guest_table_map = {arr.guest.id: (arr.table.table_number if arr.table else None) for arr in arrangements}

    # attach attribute for easy template access
    for g in event_guests:
        g.table_number = guest_table_map.get(g.id)

    guests_with_table_count = sum(1 for g in event_guests if g.table_number is not None)

    context = {
        'logs': logs,
        'event': event,
        'event_guests': event_guests,
        'event_guests_count': event_guests.count(),
        'guests_with_table_count': guests_with_table_count,
        'guests_count': rspv.count(),
        'event_data': json.dumps(event_data),
        'rspv': rspv,
        'profile': profile,
        'guests_menu': guests_menu,
        'tables_json': json.dumps(tables_json),
        'special_json': json.dumps(special_json)
    }
    return render(request, 'base/personal_vizualizare_eveniment.html', context)


@login_required(login_url='/login')
@user_is_staff
def completed_event(request, pk):
    try:
        event = Event.objects.get(id=pk)
    except Event.DoesNotExist:
        messages.error(request, "We couln't find this event")
        return redirect(request.META.get('HTTP_REFERER', '/personal_eveniment_home'))

    if event.status != "completed":
        messages.error(request, "This event is not completed yet.")
        return redirect('personal_vizualizare_eveniment', pk)

    profile = Profile.objects.get(user=request.user)
    rspv = RSVP.objects.filter(event = event)

    total_guests = event.guests.count()
    guests = event.guests.all()

    guest_users = User.objects.filter(id__in=guests.values_list('id', flat=True))
    
    search_query = request.GET.get('search', '')
    
    # ------ Pregătim set-uri de ID-uri pentru a evita dublurile ------
    raw_logs = Log.objects.filter(event=event, is_correct=True).select_related('profile__user').order_by('created')
    present_logs = []
    present_user_ids = set()
    for lg in raw_logs:
        uid = getattr(lg.profile, 'user_id', None)
        if uid and uid not in present_user_ids:
            present_logs.append(lg)
            present_user_ids.add(uid)
 
    accepted_user_ids = set(
        RSVP.objects.filter(event=event, response="Accepted", responded=True)
            .values_list('guest_id', flat=True).distinct()
    )
 
    declined_user_ids = set(
        RSVP.objects.filter(event=event, response="Declined", responded=True)
            .values_list('guest_id', flat=True).distinct()
    )
 
    pending_user_ids = set(
        RSVP.objects.filter(event=event, response="Pending", responded=False)
            .values_list('guest_id', flat=True).distinct()
    )
 
    # Guests who accepted but didn't show
    confirmed_but_absent_ids = accepted_user_ids - present_user_ids

    # Percentages
    # Calculăm denominator pe baza reuniunii seturilor (elim. eventuale discrepanţe)
    unique_user_ids = present_user_ids | confirmed_but_absent_ids | declined_user_ids | pending_user_ids
    denominator = len(unique_user_ids) or 1

    present_guests_percentage = round(len(present_user_ids) / denominator * 100, 2)
    confirmed_but_absent_percentage = round(len(confirmed_but_absent_ids) / denominator * 100, 2)
    absent_guests_percentage = round(len(declined_user_ids) / denominator * 100, 2)
    pending_guests_percentage = round(len(pending_user_ids) / denominator * 100, 2)
 
    base_present_guests = Log.objects.filter(id__in=[lg.id for lg in present_logs])
    base_confirmed_but_absent = RSVP.objects.filter(event=event, guest_id__in=confirmed_but_absent_ids)
    base_absent_guests = RSVP.objects.filter(event=event, guest_id__in=declined_user_ids)
    base_pending_guests = RSVP.objects.filter(event=event, guest_id__in=pending_user_ids)

    if search_query:
        base_present_guests = base_present_guests.filter(
            Q(profile__first_name__icontains=search_query) |
            Q(profile__last_name__icontains=search_query)
        )
        base_absent_guests = base_absent_guests.filter(
            Q(guest__profile__first_name__icontains=search_query) |
            Q(guest__profile__last_name__icontains=search_query)
        )
        base_pending_guests = base_pending_guests.filter(
            Q(guest__profile__first_name__icontains=search_query) |
            Q(guest__profile__last_name__icontains=search_query)
        )

    present_guests = base_present_guests
    confirmed_but_absent = base_confirmed_but_absent
    absent_guests = base_absent_guests
    pending_guests = base_pending_guests

    if event.location.user_account != request.user:
        messages.error(request, "Acces denied: You cant acces an completed event that was not organised at your location.")
        return redirect(request.META.get('HTTP_REFERER', '/login/'))

    archives = event.archives.all()
    posts = event.posts.all()
    print('Posts:', posts)
    print('Posts count:', posts.count())
    
    if event is not None:
        arrival_series = []
        cnt = 0
        for lg in base_present_guests.order_by('created'):
            cnt += 1
            dt = lg.created
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
            local_time = localtime(dt)
            arrival_series.append({'x': local_time.strftime('%H:%M'), 'y': cnt})
        context = {
            'event':event,
            'profile': profile,
            'rspv': rspv,
            'present_guests': present_guests,
            'confirmed_but_absent': confirmed_but_absent,
            'absent_guests': absent_guests,
            'pending_guests': pending_guests,
            'total_guests': total_guests,
            'guest_users': guest_users,
            'present_guests_percentage': present_guests_percentage,
            'absent_guests_percentage': absent_guests_percentage,
            'pending_guests_percentage': pending_guests_percentage,
            'confirmed_but_absent_percentage': confirmed_but_absent_percentage,
            'search_query': search_query,
            'archives': archives,
            'posts': posts,
            'posts_count': posts.count(),
            'arrival_series': json.dumps(arrival_series)
        }
    return render(request, 'base/completed_event.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class UploadArchiveAPI(View):
    def post(self, request, event_id):
        profile = Profile.objects.get(user=request.user)
        if not request.user.is_authenticated or profile.user_type != 'staff':
            return HttpResponseForbidden("Nu ai acces.")

        event = get_object_or_404(Event, id=event_id)

        archive_file = request.FILES.get('archive')
        if not archive_file or not archive_file.name.endswith('.zip'):
            return JsonResponse({"error": "Trebuie să fie fișier .zip sau .rar."}, status=400)

        import os
        archive_obj = EventGallery.objects.create(event=event, archive=archive_file)

        archive_info = {
            "id": archive_obj.id,
            "url": archive_obj.archive.url,
            "name": os.path.basename(archive_obj.archive.name),
            "uploaded_at": archive_obj.uploaded_at.strftime("%Y-%m-%d %H:%M")
        }

        return JsonResponse({"success": True, "archive": archive_info})


@csrf_exempt
@login_required(login_url='/login')
@user_is_staff
def delete_archive(request, archive_id):
    if request.method not in ["POST", "DELETE"]:
        return JsonResponse({"success": False, "error": "Metodă invalidă"}, status=400)

    try:
        archive = EventGallery.objects.get(id=archive_id)

        if archive.event.location.user_account != request.user:
            return JsonResponse({"success": False, "error": "Permisiune refuzată"}, status=403)

        if archive.archive:
            archive.archive.delete(save=False)

        archive.delete()
        return JsonResponse({"success": True})

    except EventGallery.DoesNotExist:
        return JsonResponse({"success": False, "error": "Arhiva nu a fost găsită"}, status=404)


@login_required(login_url='/login')
@user_is_staff
def personal_menu(request):
    profile = Profile.objects.get(user=request.user)
    menu_items = Menu.objects.all()
    allergens = Allergen.objects.all()
    region_choices = REGION_CHOICES
    category_choices = Menu.CATEGORY_CHOICES
    diet_choices = DIET_CHOICES
    spicy_choices = Menu.SPICY_LEVELS
    temp_choices = TEMP_CHOICES
    cooking_choices = COOKING_METHOD_CHOICES

    top_stats = []
    for code, label in category_choices:
        podium = (
            Menu.objects.filter(category=code)
            .annotate(sel_count=Count('menu_choices', distinct=True), avg_rating=Avg('ratings__rating'))
            .order_by('-sel_count')[:5]
        )
        if podium:
          top_stats.append({'code': code, 'label': label, 'dishes': list(podium)})

    context = {
        'profile':profile,
        'menu_items': menu_items,
        'allergens': allergens,
        'region_choices': region_choices,
        'category_choices': category_choices,
        'diet_choices': diet_choices,
        'spicy_choices': spicy_choices,
        'temp_choices': temp_choices,
        'cooking_choices': cooking_choices,
        'top_stats': top_stats,
    }
    return render(request, 'base/personal_menu.html', context)


def add_allergen(request):
    if request.method == "POST":
        data = json.loads(request.body)
        allergen_name = data.get("allergen_name")

        if allergen_name:
            Allergen.objects.create(name=allergen_name, added_by=request.user)
            return JsonResponse({"success": True})
    
    return JsonResponse({"success": False})


@login_required(login_url='/login')
@user_is_staff
def add_food(request):
    if request.method == "POST":
        print("Cerere POST primită:", request.POST)

        location = request.user.location_set.first()
        name = request.POST.get("name")
        category = request.POST.get("category", "main")
        item_cuisine = request.POST.get("item_cuisine", "no_region")
        diet_type = request.POST.get("diet_type", "none")
        spicy_level = request.POST.get("spicy_level", "none")
        cooking_method = request.POST.get("cooking_method") or None
        serving_temp = request.POST.get("serving_temp", "hot")
        calories = request.POST.get("calories") or None
        protein_g = request.POST.get("protein_g") or None
        carbs_g = request.POST.get("carbs_g") or None
        fat_g = request.POST.get("fat_g") or None
        description = request.POST.get("description") or ""

        allergens_data = request.POST.getlist('allergens')
        image = request.FILES.get("image")

        print(
            f"Date primite: nume={name}, category={category}, cuisine={item_cuisine}, diet={diet_type}, spicy={spicy_level}, "
            f"cooking={cooking_method}, temp={serving_temp}, alergeni={allergens_data}, image={image}"
        )

        if name:
            food = Menu.objects.create(
                at_location=location,
                item_name=name,
                category=category,
                item_cuisine=item_cuisine,
                diet_type=diet_type,
                spicy_level=spicy_level,
                cooking_method=cooking_method,
                serving_temp=serving_temp,
                calories=calories or None,
                protein_g=protein_g or None,
                carbs_g=carbs_g or None,
                fat_g=fat_g or None,
                description=description,
                item_picture=image
            )

            allergens_id = [int(id) for id in allergens_data]
            allergens = Allergen.objects.filter(id__in=allergens_id)
            food.allergens.set(allergens)
            return JsonResponse({"success": True, "food_id": food.id, "image_url": food.item_picture.url if food.item_picture else None})
        else:
            return JsonResponse({"success": False, "error": "Name is mandatory."})

    return JsonResponse({"success": False, "error": "Error"})


def search_food(request):
    profile = Profile.objects.get(user=request.user)
    allergens_db = Allergen.objects.all()

    query = request.GET.get("query", "").strip()
    vegetarian = request.GET.get("vegetarian", "")
    selected_allergens = request.GET.getlist("allergens")
    

    foods = Menu.objects.annotate(avg_rating=Avg('ratings__rating'))

    if query:
        foods = foods.filter(
            Q(item_name__icontains=query) |
            Q(allergens__name__icontains=query)
        ).distinct()

    if vegetarian:
        foods = foods.filter(diet_type__in=["vegetarian", "vegan"])

    if selected_allergens:
        allergen_filters = Q()
        for allergen_name in selected_allergens:
            allergen_filters |= Q(allergens__name__icontains=allergen_name)
        foods = foods.filter(allergen_filters)

    context = {
        "menu_items": foods,
        "query": query,
        "selected_allergens": selected_allergens,
        "profile": profile,
        "allergens": allergens_db,
        "region_choices": REGION_CHOICES,
        "category_choices": Menu.CATEGORY_CHOICES,
        "diet_choices": DIET_CHOICES,
        "spicy_choices": Menu.SPICY_LEVELS,
        "temp_choices": TEMP_CHOICES,
        "cooking_choices": COOKING_METHOD_CHOICES,
    }
    return render(request, "base/personal_menu.html", context)   


@login_required(login_url='/login')
@user_is_staff
def personal_layout(request):
    profile = Profile.objects.get(user=request.user)
    location = Location.objects.filter(user_account=request.user).first()
    if not location:
        messages.error(request, "You don't have a location associated with your account.")
        return redirect('personal_profile')
    tables = Table.objects.filter(location__user_account=request.user)
    special_elements = location.special_elements.all() if location else []

    context = {
        'profile': profile,
        'location': location,
        'tables': tables,
        'special_elements': special_elements
    }
    return render(request, 'base/personal_layout.html', context)

@login_required(login_url='/login')
@user_is_staff
@require_POST
def add_table(request):
    try:
        location = Location.objects.get(user_account=request.user)
        table = Table.objects.create(
            location=location,
            table_number=request.POST.get('table_number'),
            capacity=request.POST.get('capacity'),
            shape=request.POST.get('shape'),
            position_x=50,
            position_y=50
        )
        return JsonResponse({
            'success': True,
            'table': {
                'id': table.id,
                'table_number': table.table_number,
                'capacity': table.capacity,
                'shape': table.shape,
                'x': 50,
                'y': 50
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/login')
@user_is_staff
@require_POST
def update_table(request):
    try:
        table = Table.objects.get(
            id=request.POST.get('table_id'),
            location__user_account=request.user
        )
        table.table_number = request.POST.get('table_number')
        table.capacity = request.POST.get('capacity')
        table.shape = request.POST.get('shape')
        table.is_vip = request.POST.get('is_vip') == 'on'
        table.save()
        
        return JsonResponse({
            'success': True,
            'table': {
                'id': table.id,
                'table_number': table.table_number,
                'capacity': table.capacity,
                'shape': table.shape,
                'is_vip': table.is_vip,
                'x': table.position_x,
                'y': table.position_y
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/login')
@user_is_staff
@require_POST
def delete_table(request):
    try:
        data = json.loads(request.body)
        table = Table.objects.get(
            id=data.get('table_id'),
            location__user_account=request.user
        )
        table.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/login')
@user_is_staff
@require_POST
def save_table_layout(request):
    try:
        data = json.loads(request.body)
        location = Location.objects.get(user_account=request.user)

        # Id-urile meselor rămase pe canvas
        table_ids_on_canvas = [t['id'] for t in data.get('tables', [])]

        # Șterge mesele care nu mai există pe canvas
        Table.objects.filter(location=location).exclude(id__in=table_ids_on_canvas).delete()

        # Salvează/actualizează pozițiile și rotația meselor rămase
        for table_data in data.get('tables', []):
            table = Table.objects.get(
                id=table_data['id'],
                location=location
            )
            table.position_x = table_data['x']
            table.position_y = table_data['y']
            table.rotation = table_data.get('rotation', 0)
            table.width = table_data.get('width', 0) or 0
            table.height = table_data.get('height', 0) or 0
            table.radius = table_data.get('radius', 0) or 0
            table.save()

        # Salvează elementele speciale (ca înainte)
        special_elements = data.get('special_elements', [])
        location.special_elements.all().delete()
        from .models import SpecialElement
        for el in special_elements:
            SpecialElement.objects.create(
                location=location,
                type=el['type'],
                label=el.get('label', ''),
                position_x=el['x'],
                position_y=el['y'],
                rotation=el.get('rotation', 0),
                width=el.get('width', 0) or 0,
                height=el.get('height', 0) or 0,
                radius=el.get('radius', 0) or 0
            )

        # NOTIFICARE pentru organizator
        from .models import EventNotification
        staff_user = request.user
        organizer = location.owner  # presupunem că owner este organizatorul
        if organizer and organizer != staff_user:
            mesaj = f"{staff_user.username} a modificat layout-ul pentru locația {location.name}."
            EventNotification.objects.create(
                sender=staff_user,
                receiver=organizer,
                event=None,
                message=mesaj
            )

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/login')
@user_is_staff
def personal_face_id(request, pk):
    event = Event.objects.get(id=pk)
    context = {
        'event': event
    }
    return render(request, 'base/personal_face_id.html', context)


import tempfile


def find_user_view(request):
    if is_ajax(request):
        photo = request.POST.get('photo')
        _, str_img = photo.split(';base64')
        event_id = request.POST.get("event_id")
        event = Event.objects.get(id=event_id)
    
        decoded_file = base64.b64decode(str_img)

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img:
            temp_img.write(decoded_file)
            temp_img_path = temp_img.name

        res = classify_face(temp_img_path, event_id)

        os.remove(temp_img_path)

        if res:
            try:
                user = User.objects.get(username=res)
                profile = Profile.objects.get(user=user)

                existing_log = Log.objects.filter(profile=profile, event=event, is_correct=True).first()
                if existing_log:
                    return JsonResponse({
                        'status': 'success',
                        'logged': 1,
                        'user': {
                            'id': user.id,
                            'name': f"{user.first_name} {user.last_name}",
                            'email': user.email,
                            'photo_url': profile.photo.url if profile.photo else '',
                        }
                    })

                x = Log(event=event, profile=profile)
                x.photo.save('upload.png', ContentFile(decoded_file))
                x.save()

                return JsonResponse({
                    'status': 'success',
                    'log_id': x.id,
                    'user': {
                        'id': user.id,
                        'name': f"{user.first_name} {user.last_name}",
                        'email': user.email,
                        'photo_url': profile.photo.url if profile.photo else '',
                    }
                })

            except User.DoesNotExist:
                return JsonResponse({'success': False, 'result': 'Not_found'})

        return JsonResponse({'success': False})


@csrf_exempt
def validate_attendance(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        event_id = data.get('event_id')
        log_id = data.get('log_id')
        
        try:
            event = Event.objects.get(id=event_id)
            user = User.objects.get(id=user_id)
            profile = Profile.objects.get(user=user)
            preferences = Guests.objects.get(profile=profile)
            log = Log.objects.get(id=log_id)
            log.is_correct = True
            log.save()
            created_aware = make_aware(log.created)
            return JsonResponse({
                'message': 'Attendance marked',
                'user': {
                    'id': user.id,
                    'name': f"{profile.first_name} {profile.last_name}",
                    'email': user.email,
                    'photo_url': profile.photo.url if profile.photo else '',
                    'arriving_time': localtime(created_aware).strftime("%d, %H:%M"),
                    'gender': preferences.gender,
                    'cuisine_preference': preferences.cuisine_preference,
                    'vegan': preferences.vegan,
                    'allergens': [allergen.name for allergen in preferences.allergens.all()]
                    }
                }, status=200)
        except Profile.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    return JsonResponse({'error': 'Invalid method'}, status=400)

from .constants import TEMP_CHOICES, TEXTURE_CHOICES, NUTRITION_GOAL_CHOICES, DIET_CHOICES

@login_required(login_url='/login')
@user_is_guest
def guest_profile(request):

    profil = Profile.objects.get(user = request.user)
    preferences = Guests.objects.get(profile = profil)
    not_completed = Guests.objects.filter(profile__user=request.user, state=False).exists()

    if request.method == "POST":
        if not_completed:
            try:
                required_fields = {
                    'firstname': "Firstname is mandatory",
                    'lastname': "Lastname is mandatory",
                    'email': "Email is mandatory",
                    'age': "Age is mandatory",
                    'gender': "Gender is mandatory",
                    'diet_preference': "Diet preference is mandatory",
                    'spicy_food': "Spicy food preference is mandatory"
                }
                
                errors = {}
                for field, error_msg in required_fields.items():
                    if not request.POST.get(field):
                        errors[field] = error_msg
                
                email = request.POST.get('email')
                
                age = request.POST.get('age')
                if age:
                    try:
                        age = int(age)
                        if age < 1 or age > 120:
                            errors['age'] = "Vârsta trebuie să fie între 1 și 120"
                    except ValueError:
                        errors['age'] = "Vârsta trebuie să fie un număr"
                
                if errors:
                    for field, error in errors.items():
                        messages.error(request, error)
                    return redirect('guest_profile')
                
                profil = request.user.profile_set.first()
                profil.first_name = request.POST.get('firstname')
                profil.last_name = request.POST.get('lastname')
                profil.email = request.POST.get('email')
                profil.age = request.POST.get('age')
                profil.photo = request.FILES.get('photo')
                
                preferences = profil.guest_profile
                preferences.age = request.POST.get('age')

                preferences.gender = request.POST.get('gender')
                preferences.cuisine_preference = request.POST.get('meniu')
                preferences.diet_preference = request.POST.get('diet_preference')
                preferences.spicy_food = request.POST.get('spicy_food')
                
                selected_allergens = request.POST.getlist('allergensSet')
                selected_allergens_ids = [int(id) for id in selected_allergens if id.isdigit()]
                allergens = Allergen.objects.filter(id__in=selected_allergens_ids)
                preferences.allergens.set(allergens)
                
                preferences.state = True


                profil.save()
                preferences.save()
                
                messages.success(request, "Profilul a fost actualizat cu succes!")
                return redirect('guest_profile')
                
            except Exception as e:
                messages.error(request, f"A apărut o eroare: {str(e)}")
                return redirect('guest_profile')
        else:
            form_type = request.POST.get('form_type')
            if form_type == 'form1':
                profil.first_name = request.POST.get('firstname')
                profil.last_name = request.POST.get('lastname')
                profil.user.email = request.POST.get('email')
                profil.email = request.POST.get('email')
                profil.number = request.POST.get('number')

                profil.save()
                profil.user.save()
                
            elif form_type == 'form2':
                preferences.diet_preference = request.POST.get('diet_preference', 'none')
                preferences.spicy_food = request.POST.get('spicy_food', 'none')
                preferences.texture_preference = request.POST.get('texture_preference', 'none')
                preferences.nutrition_goal = request.POST.get('nutrition_goal', 'none')

                selected_medical_ids = request.POST.getlist('medical_conditions')
                if selected_medical_ids and selected_medical_ids[0] != 'no_condition':
                    mc_qs = MedicalCondition.objects.filter(id__in=selected_medical_ids)
                    preferences.medical_conditions.set(mc_qs)
                else:
                    preferences.medical_conditions.clear()

                selected_allergens = request.POST.getlist('allergens')
                selected_allergens_ids = [int(i) for i in selected_allergens if i.isdigit()]
                preferences.allergens.set(Allergen.objects.filter(id__in=selected_allergens_ids))

                preferences.custom_medical_notes = request.POST.get('medical_notes')

                preferences.save()

            
    not_completed = Guests.objects.filter(profile__user=request.user, state=False).exists()
    allergens = Allergen.objects.all()
    medical_conditions = MedicalCondition.objects.all()
    temp_choices = TEMP_CHOICES
    texture_choices = TEXTURE_CHOICES
    nutrition_goals = NUTRITION_GOAL_CHOICES
    diet_choices = DIET_CHOICES
    SPICY_LEVELS = [
        ('none', 'None'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]
    hot_levels = SPICY_LEVELS

    context = {
        "not_completed": not_completed,
        "preferences": preferences,
        "profile": profil,
        "allergens": allergens,
        "diet_choices": diet_choices,
        "hot_levels": hot_levels,
        "medical_conditions": medical_conditions,
        "temp_choices": temp_choices,
        "texture_choices": texture_choices,
        "nutrition_goals": nutrition_goals,
    }            

    return render(request, 'base/guest_profile.html', context)


@require_POST
@login_required
def update_profile_picture(request):
    profile = request.user.profile_set.first()
    print("Profilul:", profile)
    image = request.FILES.get('image')
    if image:
        profile.photo = image
        profile.save()
        return JsonResponse({'success': True, 'image_url': profile.photo.url})
    return JsonResponse({'success': False, 'error': 'No image'})


@login_required(login_url='/login')
@user_is_guest
def guest_home(request):
    profil = Profile.objects.get(user = request.user)
    preferences = Guests.objects.get(profile = profil)
    now = timezone.now()
    
    guest_profile = Guests.objects.get(profile = profil)
    print(guest_profile.id)
    confirmed_events = Event.objects.filter(event_date__gte=now, guests=guest_profile).filter(Q(rsvps__response="Accepted") | Q(rsvps__response="Pending")).distinct().order_by('event_date')
    past_events = Event.objects.filter(event_date__lt=now, guests=guest_profile, rsvps__response="Accepted").distinct().order_by('event_date')
    print("past_events:", past_events)
    
    print("Evenimente confirmate:", confirmed_events)
    next_confirmed_event = confirmed_events.first() if confirmed_events.exists() else None
    print("Next confirmed event:", next_confirmed_event)

    if confirmed_events.exists():
        upcoming_events = confirmed_events[1:]
    else:
        upcoming_events = []

    event_data = []

    if next_confirmed_event is not None:
        event_data = [
            {
                'id': next_confirmed_event.id,
                'title': next_confirmed_event.event_name,
                'event_date': datetime.combine(next_confirmed_event.event_date, next_confirmed_event.event_time).strftime('%Y-%m-%d %H:%M:%S')
            }
        ]

    print("Evenimente viitoare:", upcoming_events)
    not_completed = Guests.objects.filter(profile__user=request.user, state=False).exists()

    context = {
        "not_completed": not_completed,
        "preferences": preferences,
        "profile": profil,
        "next_confirmed_event": next_confirmed_event,
        "upcoming_events": upcoming_events,
        "upcoming_events_count": len(upcoming_events),
        "past_events": past_events,
        "past_events_count": past_events.count(),
        "event": next_confirmed_event,
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
    print(event.status)
    location = event.location
    oragniser_profile = event.organized_by.profile_set.first()
    rsvp = RSVP.objects.get(event=event, guest=request.user)
    profile=Profile.objects.get(user=request.user)
    preferences = Guests.objects.get(profile = profile)
    menus=Menu.objects.all()
    appetizers = Menu.objects.filter(category='appetizer')
    main_courses = Menu.objects.filter(category='main')
    desserts = Menu.objects.filter(category='dessert')
    drinks = Menu.objects.filter(category='drink')

    # Prepare complete dish catalog per category (for edit modal)
    categories_map = {
        'appetizer': appetizers,
        'main': main_courses,
        'dessert': desserts,
        'drink': drinks,
    }
    all_dishes_catalog = {}
    for cat, qs in categories_map.items():
        dishes_serialized = []
        for d in qs:
            dishes_serialized.append({
                'id': d.id,
                'name': d.item_name,
                'diet_type': d.diet_type,
                'image': d.item_picture.url if d.item_picture else '',
                'allergens': [a.name for a in d.allergens.all()],
                'region': d.item_cuisine,
            })
        all_dishes_catalog[cat] = dishes_serialized

    guest_allergens = [a.name for a in preferences.allergens.all()]

    if request.method == "POST" and request.POST.get("response"):
        print(request.POST)
        value = request.POST.get("response")
        print(value)
        if value in ["Accepted", "Declined"]:
            rsvp.response = value
            rsvp.responded = True
            rsvp.save() 

            # Redirect to avoid form-resubmission prompt (POST-Redirect-GET)
            return redirect('guest_event_view', pk=pk)

    if request.method == 'POST' and request.POST.get("form_type") == "add_post":
        print("se executa")
        form = EventPostForm(request.POST, event=event, user=request.user)
        if form.is_valid():
            print("Form valid")
            try:
                post = form.save(commit=False)
                post.event = event
                post.author = request.user
                post.save()
                
                for i, image in enumerate(request.FILES.getlist('images')):
                    PostImage.objects.create(
                        post=post,
                        image=image,
                        order=i
                    )
                print("Post saved successfully")
                return redirect('guest_event_view', pk=pk)
            except Exception as e:
                print("Error saving post:", e)
                return redirect('guest_event_view', pk=pk)
        else:
            print("Form not valid but sent trimite")
            print(form.errors)
            # fall through to render template without redirect
    else:
        form = EventPostForm()
        print("Form not valid")

    event_posts = EventPost.objects.filter(event=event).annotate(
            is_liked=Exists(
                PostLike.objects.filter(
                    post=OuterRef('pk'),
                    user=request.user
                )
            )
        ).order_by('-created_at')
    guest_posts = EventPost.objects.filter(event=event, author=request.user).order_by('-created_at')
    rsvp = RSVP.objects.get(event=event, guest=request.user)
    print(rsvp)

    event_data = [
        {
            'id': event.id,
            'title': event.event_name,
            'event_date': datetime.combine(event.event_date, event.event_time).strftime('%Y-%m-%d %H:%M:%S')
        }
    ]

    archives = event.archives.all()
    posts = event.posts.all()
    review_organizer = Review.objects.filter(user=request.user, organizer=event.organized_by).first()
    review_location = Review.objects.filter(user=request.user, location=event.location).first()
    gallery = LocationImages.objects.filter(location=event.location)

    from .models import MenuRating
    chosen_menu = []
    try:
        guest_menu = GuestMenu.objects.get(guest=request.user, event=event)
        all_rated = False
        rated_item = guest_menu.menu_choices.all()
        if rated_item:
            rated_item_count = MenuRating.objects.filter(guest=preferences, menu_item__in=rated_item).count()
        else:
            rated_item_count = 0

        for d in guest_menu.menu_choices.all():
            chosen_menu.append({
                "id": d.id,
                "name": d.item_name,
                "category": d.category,
                "image": d.item_picture.url if d.item_picture else "",
                "allergens": [a.name for a in d.allergens.all()],
                "is_vegan": d.item_vegan,
                "rating": getattr(MenuRating.objects.filter(guest=preferences, menu_item=d).first(), 'rating', 0),
                "diet_type": d.diet_type,
                "item_cuisine": d.item_cuisine,

            })
    except GuestMenu.DoesNotExist:
        rated_item_count = 0
        pass

    context={
        'organiser':oragniser_profile,
        'event':event,
        'profile':profile,
        'preferences':preferences,
        'event_data': json.dumps(event_data),
        'rsvp':rsvp,
        'menus':menus,
        'appetizers': appetizers,
        'main_courses': main_courses,
        'desserts': desserts,
        'drinks': drinks,
        'form': form,
        'guest_posts': guest_posts,
        'guest_posts_count': guest_posts.count(),
        'event_posts': event_posts,
        'event_posts_count': event_posts.count(),
        'location': location,
        'archives': archives,
        'posts': posts,
        'chosen_menu_json': json.dumps(chosen_menu),
        'chosen_menu': chosen_menu,
        'review_organizer': review_organizer,
        'review_location': review_location,
        'gallery': gallery,
        'rated_item_count': rated_item_count,
        'all_dishes_json': json.dumps(all_dishes_catalog),
        'guest_allergens_json': json.dumps(guest_allergens),
    }
    return render(request,'base/guest_event_view.html', context)


def generate_menu(request):
    guest = request.user.profile_set.first().guest_profile
    preferred_region = guest.cuisine_preference
    guest_allergens = guest.allergens.all()
    guest_diet = guest.diet_preference
    guest_texture = guest.texture_preference or 'none'
    guest_nutri = guest.nutrition_goal or 'none'
    guest_temp = guest.temp_preference or 'hot'
    spicy_pref = guest.spicy_food or 'none'

    safe_dishes = Menu.objects.exclude(allergens__in=guest_allergens).distinct()
    if guest_diet != 'none':
        DIET_COMPATIBILITY = {
            'vegan': ['vegan'],
            'vegetarian': ['vegetarian', 'vegan'],
            'pescatarian': ['pescatarian', 'vegetarian', 'vegan'],
            'low_carb': ['low_carb', 'keto'],
            'keto': ['keto'],
            'halal': ['halal'],
            'kosher': ['kosher'],
        }

        allowed_diets = DIET_COMPATIBILITY.get(guest_diet, [guest_diet])
        safe_dishes = safe_dishes.filter(diet_type__in=allowed_diets)

    # spicy level <= preferinţă
    order = ['none','low','medium','high']
    allowed_levels = order[: order.index(spicy_pref)+1] if spicy_pref in order else order
    safe_dishes = safe_dishes.filter(spicy_level__in=allowed_levels)

    categories = ['appetizer', 'main', 'dessert', 'drink']
    menu = {}
    messages = []

    try:
        from .recommender import get_recommender
        recommender = get_recommender()
        
        if recommender.is_loaded:
            print("Folosim modelul LightFM pentru recomandări")
            
            for category in categories:
                filtered_dishes = safe_dishes.filter(category=category)
                
                if filtered_dishes.exists():
                    recommendations = recommender.get_recommendations(guest.id, top_n=20, exclude_rated=False)
                    
                    category_recommendations = []
                    for rec in recommendations:
                        dish_id = rec['dish_id']
                        try:
                            dish = Menu.objects.get(id=dish_id, category=category)
                            if not dish.allergens.filter(id__in=guest_allergens.values_list('id', flat=True)).exists() and dish in filtered_dishes:
                                category_recommendations.append({
                                    'dish': dish,
                                    'score': rec['score']
                                })
                        except Menu.DoesNotExist:
                            continue
                    
                    category_recommendations.sort(key=lambda x: x['score'], reverse=True)
                    selected = [item['dish'] for item in category_recommendations[:3]]
                    
                    if len(selected) < 3:
                        remaining_needed = 3 - len(selected)
                        selected_ids = [d.id for d in selected]
                        
                        regional_dishes = filtered_dishes.filter(
                            item_cuisine=preferred_region
                        ).exclude(id__in=selected_ids)
                        
                        if regional_dishes.exists():
                            additional = list(regional_dishes[:remaining_needed])
                            selected.extend(additional)
                            remaining_needed -= len(additional)
                        
                        if remaining_needed > 0:
                            other_dishes = filtered_dishes.exclude(id__in=[d.id for d in selected])
                            if other_dishes.exists():
                                selected.extend(list(other_dishes[:remaining_needed]))
                    
                else:
                    selected = []
                    messages.append(f"Nicio opțiune disponibilă fără alergeni pentru categoria '{category}'.")
                
                menu[category] = [
                    {
                        'id': dish.id,
                        'name': dish.item_name,
                        'region': dish.item_cuisine if dish.item_cuisine else '',
                        'category': dish.category,
                        'image': dish.item_picture.url if dish.item_picture else "",
                        'allergens': [a.name for a in dish.allergens.all()],
                        'is_vegan': dish.item_vegan,
                        'diet_type': dish.diet_type,
                        'spicy_level': dish.spicy_level,
                        'calories': dish.calories,
                        'protein_g': dish.protein_g,
                    }
                    for dish in selected
                ]
                
        else:
            messages.append("Modelul LightFM nu este încărcat. Folosesc filtrarea de bază.")
            raise Exception("Model not loaded")
            
    except Exception as e:
        print(f"Eroare cu modelul LightFM: {e}")
        messages.append(f"Eroare cu modelul LightFM: {str(e)}. Folosesc filtrarea de bază.")
        
        for category in categories:
            filtered_dishes = safe_dishes.filter(category=category)
            
            if filtered_dishes.exists():
                regional_dishes = filtered_dishes.filter(item_cuisine=preferred_region)
                
                if regional_dishes.exists():
                    selected = list(regional_dishes[:3])
                    count_needed = 3 - len(selected)
                    
                    if count_needed > 0:
                        other_dishes = filtered_dishes.exclude(id__in=[d.id for d in selected])
                        other_selected = list(other_dishes[:count_needed])
                        selected.extend(other_selected)
                else:
                    messages.append(f"Nu există opțiuni din regiunea preferată pentru categoria '{category}'.")
                    selected = list(filtered_dishes[:3])
            else:
                messages.append(f"Nicio opțiune disponibilă fără alergeni pentru categoria '{category}'.")
                selected = []

            menu[category] = [
                {
                    'id': dish.id,
                    'name': dish.item_name,
                    'region': dish.item_cuisine if dish.item_cuisine else '',
                    'category': dish.category,
                    'image': dish.item_picture.url if dish.item_picture else "",
                    'allergens': [a.name for a in dish.allergens.all()],
                    'is_vegan': dish.item_vegan,
                    'diet_type': dish.diet_type,
                    'spicy_level': dish.spicy_level,
                    'calories': dish.calories,
                    'protein_g': dish.protein_g,
                }
                for dish in selected
            ]

    return JsonResponse({'menu': menu, 'messages': messages})


@csrf_exempt
@require_POST
def save_guest_menu(request):
    try:
        data = json.loads(request.body)
        user = request.user  # sau request.user.id
        event_id = data.get("event_id")
        location_id = data.get("location_id")
        dish_ids = data.get("menu_choices", [])

        event = Event.objects.get(id=event_id)
        location = Location.objects.get(id=location_id)
        menu_items = Menu.objects.filter(id__in=dish_ids)

        guest_menu, created = GuestMenu.objects.get_or_create(
            guest=user,
            event=event,
            defaults={"location_menu": location}
        )
        if not created:
            guest_menu.menu_choices.clear()

        guest_menu.location_menu = location
        guest_menu.save()
        guest_menu.menu_choices.set(menu_items)

        chosen = [
            {
                "id": d.id,
                "name": d.item_name,
                "category": d.category,
                "region": d.item_cuisine if d.item_cuisine else '',
                "diet_type": d.diet_type,
                "image": d.item_picture.url if d.item_picture else "",
                "allergens": [a.name for a in d.allergens.all()],
                "is_vegan": d.item_vegan,
            }
            for d in menu_items
        ]

        return JsonResponse({"success": True, "message": "Menu saved successfully", "menu": chosen})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


@require_POST
@login_required(login_url='/login')
def like_post(request, post_id):
    post = get_object_or_404(EventPost, id=post_id)
    print("Post ID:", post)
    like, created = PostLike.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    
    post.like_count = post.likes.count()
    post.save()
    return JsonResponse({'likes': post.like_count, 'liked': created})


@require_POST
@login_required(login_url='/login')
def add_comment(request, post_id):
    post = get_object_or_404(EventPost, id=post_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            PostComment.objects.create(
                post=post,
                author=request.user,
                text=text
            )
    return redirect('guest_event_view', post.event.id) 


@require_POST
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(PostComment, id=comment_id)

    if request.user == comment.author:
        comment.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)


@login_required(login_url='/login')
def delete_post(request, postId):
    if request.method == "DELETE":
        try:
            post = EventPost.objects.get(id=postId)
            post.delete()
            return JsonResponse({"success": True})
        except Menu.DoesNotExist:
            return JsonResponse({"success": False, "error": "Post not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Invalid method"}, status=405)


def event_status_api(request, pk):
    event = Event.objects.get(id=pk)
    previous_status = request.GET.get('current_status')
    rsvp = RSVP.objects.get(event=event, guest=request.user)
    profile=Profile.objects.get(user=request.user)
    preferences = Guests.objects.get(profile = profile)
    menus=Menu.objects.all()


    print(event.status)
    
    response_data = {
        'status': event.status,
        'html': render_to_string('../templates/event_status_content.html', {'event': event,
        'profile':profile,
        'preferences':preferences,
        'rsvp':rsvp,
        'menus':menus})
    }
    
    return JsonResponse(response_data)



def get_food_details(request, food_id):
    food = get_object_or_404(Menu, id=food_id)

    allergen_qs = food.allergens.all()
    allergen_names = [a.name for a in allergen_qs]
    allergen_ids = [a.id for a in allergen_qs]

    data = {
        "id": food.id,
        "name": food.item_name,
        "category": food.get_category_display(),
        "cuisine": dict(REGION_CHOICES).get(food.item_cuisine, food.item_cuisine),
        "diet_type": dict(DIET_CHOICES).get(food.diet_type, food.diet_type),
        "spicy_level": food.spicy_level,
        "cooking_method": food.cooking_method,
        "serving_temp": food.serving_temp,
        "calories": food.calories,
        "protein_g": food.protein_g,
        "carbs_g": food.carbs_g,
        "fat_g": food.fat_g,
        "description": food.description or "",
        "allergens": allergen_ids,
        "allergen_names": allergen_names,
        "image": food.item_picture.url if food.item_picture else "",
    }

    return JsonResponse(data)


def update_food(request, food_id):
    if request.method == 'POST':
        try:
            food = get_object_or_404(Menu, id=food_id)
            
            food.item_name = request.POST.get('item_name')
            food.item_cuisine = request.POST.get('item_cuisine')
            food.item_vegan = request.POST.get('item_vegan') == 'true'
            
            if 'item_picture' in request.FILES:
                food.item_picture = request.FILES['item_picture']
        
            food.save()
            
            allergen_ids = request.POST.getlist('allergens')
            food.allergens.set(allergen_ids)
            
            return JsonResponse({'success': True})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def delete_dish(request, dish_id):
    if request.method == "DELETE":
        try:
            dish = Menu.objects.get(id=dish_id)
            dish.delete()
            return JsonResponse({"success": True})
        except Menu.DoesNotExist:
            return JsonResponse({"success": False, "error": "Dish not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Invalid method"}, status=405)


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
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='/login')
def get_notifications(request):
    profil = Profile.objects.get(user = request.user)
    user_type = profil.user_type
    
    # --- Generare automată notificări pentru profil incomplet (doar pentru invitaţi) ---
    if user_type == "guest" and not profil.is_complete:
        from datetime import timedelta
        today = timezone.now().date()
        upcoming_events = Event.objects.filter(
            rsvps__guest=request.user,
            rsvps__response="Accepted",
        ).distinct()

        for ev in upcoming_events:
            if not EventNotification.objects.filter(
                receiver=request.user,
                event=ev,
                message__icontains="complete your profile",
                timestamp__date=today
            ).exists():
                msg = f"Complete your profile before the event '{ev.event_name}' ({ev.event_date})."

                guest_obj = request.user.profile_set.first().guest_profile
                guest_missing = guest_obj.get_missing_fields() if guest_obj else []
                missing_fields = profil.get_missing_fields() + guest_missing

                if missing_fields:
                    nice_fields = ", ".join(missing_fields)
                    msg = f"Missing info: {nice_fields}. Complete your profile before '{ev.event_name}' on {ev.event_date}."

                    EventNotification.objects.create(
                        sender=ev.location.user_account or ev.organized_by,
                        receiver=request.user,
                        event=ev,
                        message=msg
                    )

    if profil.user_type == "guest":
        rsvp = RSVP.objects.filter(guest = request.user, response = "Accepted").values_list('event', flat=True)
        notifications = EventNotification.objects.filter(event__in=rsvp, receiver=request.user, is_read="False").order_by('-timestamp')
    elif profil.user_type == "staff":
        events = Event.objects.filter(location__user_account = request.user)
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
            "redirect": "/guest_profile" if "Missing info" in n.message and user_type=="guest" else None,
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


@login_required(login_url='/login')
@user_is_organizer
def test_table_arrangement(request, event_id):
    """View pentru testarea algoritmului de aranjare la mese"""
    print("DEBUG: Începe test_table_arrangement")
    print(f"DEBUG: Event ID: {event_id}")
    print(f"DEBUG: User: {request.user}")
    
    try:
        event = get_object_or_404(Event, id=event_id)
        print(f"DEBUG: Event găsit: {event.event_name}")
        
        # Verifică dacă utilizatorul este organizatorul evenimentului
        if event.organized_by != request.user:
            messages.error(request, "Nu aveți permisiunea de a testa aranjamentul!")
            return redirect('event_details', event_id=event.id)
        
        # Verifică dacă evenimentul are locație și invitați
        if not event.location:
            messages.error(request, "Evenimentul nu are o locație asociată!")
            return redirect('event_details', event_id=event.id)
        
        if not event.guests.exists():
            messages.error(request, "Nu există invitați pentru acest eveniment!")
            return redirect('event_details', event_id=event.id)

        # Verifică dacă există mese în locație
        tables = Table.objects.filter(location=event.location)
        if not tables.exists():
            messages.error(request, "Nu există mese configurate în această locație!")
            return redirect('event_details', event_id=event.id)

        # Șterge aranjamentele existente pentru a începe cu un aranjament nou
        TableArrangement.objects.filter(event=event).delete()
        
        # Inițializează algoritmul
        algorithm = TableArrangementAlgorithm(event)
        
        # Generează aranjamentul
        arrangements = algorithm.generate_arrangement()
        
        if not arrangements:
            messages.error(request, "Nu s-a putut genera un aranjament valid!")
            return redirect('event_details', event_id=event.id)

        # Salvează aranjamentele în baza de date
        for arrangement in arrangements:
            arrangement.save()
            print(f"DEBUG: Salvat aranjament: {arrangement}")
        
        # Obține statisticile aranjamentului
        stats = algorithm.get_arrangement_statistics()
        print(f"DEBUG: Statistici calculate: {stats}")
        
        # Grupează aranjamentele pe mese pentru afișare
        table_arrangements = {}
        for arrangement in arrangements:
            if arrangement.table not in table_arrangements:
                table_arrangements[arrangement.table] = []
            table_arrangements[arrangement.table].append(arrangement)

        context = {
            'event': event,
            'table_arrangements': table_arrangements,
            'stats': stats,
            'tables': tables,
        }
        
        return render(request, 'base/test_table_arrangement.html', context)
        
    except Exception as e:
        print(f"DEBUG: Eroare neașteptată: {str(e)}")
        messages.error(request, f"A apărut o eroare: {str(e)}")
        return redirect('event_details', event_id=event_id)

@require_POST
def confirm_table_arrangement(request, event_id):
    """Endpoint pentru confirmarea aranjamentului la mese"""
    event = get_object_or_404(Event, id=event_id)
    
    # Actualizează statusul aranjamentelor la 'confirmed'
    TableArrangement.objects.filter(
        event=event,
        status='pending'
    ).update(status='confirmed')
    
    # Adaugă mesajul în sesiune pentru a fi afișat pe pagina de test
    messages.success(request, "Aranjamentul la mese a fost confirmat cu succes!")
    
    # Redirecționează înapoi la pagina de test
    return redirect('test_table_arrangement', event_id=event.id)

@require_POST
def reset_table_arrangement(request, event_id):
    """Endpoint pentru resetarea aranjamentului la mese"""
    event = get_object_or_404(Event, id=event_id)
    
    # Șterge toate aranjamentele existente
    TableArrangement.objects.filter(event=event).delete()
    
    # Adaugă mesajul în sesiune pentru a fi afișat pe pagina de test
    messages.success(request, "Aranjamentul la mese a fost resetat!")
    
    # Redirecționează înapoi la pagina de test
    return redirect('test_table_arrangement', event_id=event.id)

@login_required(login_url='/login')
@user_is_organizer
def populate_test_data(request, event_id):
    """Populează datele de test pentru aranjamentul la mese"""
    event = get_object_or_404(Event, id=event_id)
    
    # Verifică dacă utilizatorul este organizatorul evenimentului
    if event.organized_by != request.user:
        messages.error(request, "Nu aveți permisiunea de a popula datele de test!")
        return redirect('event_details', event_id=event.id)
    
    if not event.location:
        messages.error(request, "Evenimentul nu are o locație asociată!")
        return redirect('event_details', event_id=event.id)

    # 1. Creează mesele în locație dacă nu există
    if not Table.objects.filter(location=event.location).exists():
        tables_data = [
            {'table_number': 1, 'capacity': 8, 'shape': 'round', 'position_x': 100, 'position_y': 100, 'is_reserved': True},
            {'table_number': 2, 'capacity': 8, 'shape': 'round', 'position_x': 300, 'position_y': 100, 'is_reserved': False},
            {'table_number': 3, 'capacity': 8, 'shape': 'round', 'position_x': 500, 'position_y': 100, 'is_reserved': False},
            {'table_number': 4, 'capacity': 6, 'shape': 'rectangle', 'position_x': 100, 'position_y': 300, 'is_reserved': False},
            {'table_number': 5, 'capacity': 6, 'shape': 'rectangle', 'position_x': 300, 'position_y': 300, 'is_reserved': False},
            {'table_number': 6, 'capacity': 6, 'shape': 'rectangle', 'position_x': 500, 'position_y': 300, 'is_reserved': False},
        ]
        
        for table_data in tables_data:
            Table.objects.create(location=event.location, **table_data)
        
        messages.success(request, "Au fost create 6 mese în locație!")

    # 2. Creează invitați de test dacă nu există
    if not event.guests.exists():
        guests_data = [
            # Familia miresei
            {'username': 'maria.popescu', 'first_name': 'Maria', 'last_name': 'Popescu', 'email': 'maria@test.com', 'gender': 'F', 'age': 45},
            {'username': 'ion.popescu', 'first_name': 'Ion', 'last_name': 'Popescu', 'email': 'ion@test.com', 'gender': 'M', 'age': 48},
            {'username': 'elena.popescu', 'first_name': 'Elena', 'last_name': 'Popescu', 'email': 'elena@test.com', 'gender': 'F', 'age': 42},
            {'username': 'vasile.popescu', 'first_name': 'Vasile', 'last_name': 'Popescu', 'email': 'vasile@test.com', 'gender': 'M', 'age': 40},
            
            # Familia mirelui
            {'username': 'andrei.ionescu', 'first_name': 'Andrei', 'last_name': 'Ionescu', 'email': 'andrei@test.com', 'gender': 'M', 'age': 46},
            {'username': 'ana.ionescu', 'first_name': 'Ana', 'last_name': 'Ionescu', 'email': 'ana@test.com', 'gender': 'F', 'age': 44},
            {'username': 'mihai.ionescu', 'first_name': 'Mihai', 'last_name': 'Ionescu', 'email': 'mihai@test.com', 'gender': 'M', 'age': 41},
            {'username': 'laura.ionescu', 'first_name': 'Laura', 'last_name': 'Ionescu', 'email': 'laura@test.com', 'gender': 'F', 'age': 39},
            
            # Prieteni comuni
            {'username': 'alexandru.constantin', 'first_name': 'Alexandru', 'last_name': 'Constantin', 'email': 'alex@test.com', 'gender': 'M', 'age': 35},
            {'username': 'diana.constantin', 'first_name': 'Diana', 'last_name': 'Constantin', 'email': 'diana@test.com', 'gender': 'F', 'age': 33},
            {'username': 'cristian.radu', 'first_name': 'Cristian', 'last_name': 'Radu', 'email': 'cristi@test.com', 'gender': 'M', 'age': 36},
            {'username': 'simona.radu', 'first_name': 'Simona', 'last_name': 'Radu', 'email': 'simona@test.com', 'gender': 'F', 'age': 34},
            
            # Colegi de la serviciu
            {'username': 'george.marin', 'first_name': 'George', 'last_name': 'Marin', 'email': 'george@test.com', 'gender': 'M', 'age': 38},
            {'username': 'andreea.marin', 'first_name': 'Andreea', 'last_name': 'Marin', 'email': 'andreea@test.com', 'gender': 'F', 'age': 36},
            {'username': 'bogdan.dumitrescu', 'first_name': 'Bogdan', 'last_name': 'Dumitrescu', 'email': 'bogdan@test.com', 'gender': 'M', 'age': 37},
            {'username': 'raluca.dumitrescu', 'first_name': 'Raluca', 'last_name': 'Dumitrescu', 'email': 'raluca@test.com', 'gender': 'F', 'age': 35},
            
            # Vecini
            {'username': 'florin.stoica', 'first_name': 'Florin', 'last_name': 'Stoica', 'email': 'florin@test.com', 'gender': 'M', 'age': 50},
            {'username': 'gabriela.stoica', 'first_name': 'Gabriela', 'last_name': 'Stoica', 'email': 'gabi@test.com', 'gender': 'F', 'age': 48},
            {'username': 'marian.neagu', 'first_name': 'Marian', 'last_name': 'Neagu', 'email': 'marian@test.com', 'gender': 'M', 'age': 52},
            {'username': 'luminita.neagu', 'first_name': 'Luminita', 'last_name': 'Neagu', 'email': 'lumi@test.com', 'gender': 'F', 'age': 50},
            
            # Prieteni din facultate
            {'username': 'stefan.munteanu', 'first_name': 'Stefan', 'last_name': 'Munteanu', 'email': 'stefan@test.com', 'gender': 'M', 'age': 32},
            {'username': 'ioana.munteanu', 'first_name': 'Ioana', 'last_name': 'Munteanu', 'email': 'ioana@test.com', 'gender': 'F', 'age': 30},
            {'username': 'adrian.gheorghe', 'first_name': 'Adrian', 'last_name': 'Gheorghe', 'email': 'adrian@test.com', 'gender': 'M', 'age': 31},
            {'username': 'cristina.gheorghe', 'first_name': 'Cristina', 'last_name': 'Gheorghe', 'email': 'cristina@test.com', 'gender': 'F', 'age': 29},
        ]
        
        for guest_data in guests_data:
            # Creează profilul
            profile = Profile.objects.create(
                username=guest_data['username'],
                email=guest_data['email'],
                first_name=guest_data['first_name'],
                last_name=guest_data['last_name'],
                password=make_password('test123'),  # Parolă default pentru toți invitații
                user_type='guest',
                approved=True
            )
            
            # Creează invitatul
            guest = Guests.objects.create(
                profile=profile,
                gender=guest_data['gender'],
                age=guest_data['age']
            )
            
            # Adaugă invitatul la eveniment
            event.guests.add(guest)
        
        messages.success(request, "Au fost adăugați 24 de invitați de test!")

    # 3. Creează grupuri de invitați
    if not TableGroup.objects.filter(event=event).exists():
        # Grupul familiei miresei
        bride_family = TableGroup.objects.create(
            event=event,
            name="Familia Miresei",
            priority=3,
            notes="Familia apropriată a miresei"
        )
        bride_family.guests.add(*event.guests.filter(profile__last_name='Popescu'))
        
        # Grupul familiei mirelui
        groom_family = TableGroup.objects.create(
            event=event,
            name="Familia Mirelui",
            priority=3,
            notes="Familia apropriată a mirelui"
        )
        groom_family.guests.add(*event.guests.filter(profile__last_name='Ionescu'))
        
        # Grupul prietenilor comuni
        common_friends = TableGroup.objects.create(
            event=event,
            name="Prieteni Comuni",
            priority=2,
            notes="Prieteni apropiați ai cuplului"
        )
        common_friends.guests.add(*event.guests.filter(profile__last_name__in=['Constantin', 'Radu']))
        
        # Grupul colegilor
        colleagues = TableGroup.objects.create(
            event=event,
            name="Colegi de la Serviciu",
            priority=1,
            notes="Colegi de la serviciu"
        )
        colleagues.guests.add(*event.guests.filter(profile__last_name__in=['Marin', 'Dumitrescu']))
        
        messages.success(request, "Au fost create 4 grupuri de invitați!")

    return redirect('test_table_arrangement', event_id=event.id)

@require_GET
@login_required
def table_details_api(request, table_id):
    event_id = request.GET.get('event_id')
    if not event_id:
        return JsonResponse({'error': 'Missing event_id'}, status=400)
    try:
        table = Table.objects.get(id=table_id)
        event = Event.objects.get(id=event_id)
    except (Table.DoesNotExist, Event.DoesNotExist):
        return JsonResponse({'error': 'Table or event not found'}, status=404)

    arrangements = TableArrangement.objects.filter(table=table, event=event).order_by('seat_number')
    guests = []
    menu_items = []

    for arrangement in arrangements:
        guest = arrangement.guest
        user_obj = guest.profile.user
        menu_by_cat = {'appetizer': [], 'main': [], 'dessert': [], 'drink': []}
        try:
            guest_menu = GuestMenu.objects.get(guest=user_obj, event=event)
            for item in guest_menu.menu_choices.all():
                menu_by_cat.setdefault(item.category, []).append(item.item_name)
        except GuestMenu.DoesNotExist:
            pass

        allergens_list = list(guest.allergens.values_list('name', flat=True))
        is_vegan = getattr(guest, 'vegan', False)
        diet_type = guest.diet_preference
        region = getattr(guest, 'region', 'none')

        profile = getattr(guest, 'profile', None)
        name = None
        photo = None
        if profile:
            first_name = getattr(profile, 'first_name', '')
            last_name = getattr(profile, 'last_name', '')
            name = f"{first_name} {last_name}".strip() or getattr(profile, 'username', '')
            photo = profile.photo.url if profile.photo else None

        guests.append({
            'name': name or str(guest),
            'group': ', '.join([g.name for g in getattr(guest, 'table_groups', []).all()]) if hasattr(guest, 'table_groups') else None,
            'status': arrangement.status,
            'photo': photo,
            'menu': menu_by_cat,
            'allergens': allergens_list,
            'is_vegan': is_vegan,
            'diet_type': diet_type,
            'region': region,
        })
    return JsonResponse({'guests': guests})


from django.http import JsonResponse
from django.db.models import Q

@login_required
def guest_table_api(request):
    query   = request.GET.get('q', '').strip().lower()
    event_id = request.GET.get('event_id')

    if not query or not event_id:
        return JsonResponse({'error': 'Missing params'}, status=400)

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)

    # căutăm în aranjament
    arrangement = (
        TableArrangement.objects
        .select_related('table', 'guest__profile')
        .filter(
            event=event,
            guest__profile__first_name__icontains=query
        ) | TableArrangement.objects.filter(
            event=event,
            guest__profile__last_name__icontains=query
        )
    ).first()

    if not arrangement:
        return JsonResponse({'found': False})

    prof = arrangement.guest.profile
    return JsonResponse({
        'found': True,
        'table_id': arrangement.table.id,
        'table_number': arrangement.table.table_number,
        'guest_fullname': f'{prof.first_name} {prof.last_name}'.strip()
    })


def populate_reviews_for_emhasce():
    try:
        organizer = User.objects.get(username='Emhasce')
        # Obținem primii 3 utilizatori din baza de date (excluzând organizatorul)
        reviewers = User.objects.exclude(username='Emhasce')[:3]
        
        if reviewers.exists():
            reviews = [
                {'user': reviewers[0], 'comment': 'Great organizer! Very professional and attentive to details.', 'stars': 5},
                {'user': reviewers[1], 'comment': 'Amazing experience! Everything was perfectly organized.', 'stars': 5},
                {'user': reviewers[2], 'comment': 'Excellent service and communication throughout the event.', 'stars': 4},
            ]
            
            for review_data in reviews:
                Review.objects.get_or_create(
                    user=review_data['user'],
                    organizer=organizer,
                    defaults={
                        'comment': review_data['comment'],
                        'stars': review_data['stars'],
                        'created_at': timezone.now()
                    }
                )
    except User.DoesNotExist:
        print("Organizer 'Emhasce' not found in the database.")
    except Exception as e:
        print(f"Error populating reviews: {str(e)}")

# Apelăm funcția pentru a popula review-urile
populate_reviews_for_emhasce()

@csrf_exempt
@login_required
def save_table_positions(request, event_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        for t in data['tables']:
            table = Table.objects.get(id=t['id'])
            table.position_x = float(t['left'])
            table.position_y = float(t['top'])
            table.save()
        return JsonResponse({'status': 'ok'})

@login_required(login_url='/login')
@require_POST
def save_table_layout(request):
    try:
        data = json.loads(request.body)
        location = Location.objects.get(user_account=request.user)

        # Id-urile meselor rămase pe canvas
        table_ids_on_canvas = [t['id'] for t in data.get('tables', [])]

        # Șterge mesele care nu mai există pe canvas
        Table.objects.filter(location=location).exclude(id__in=table_ids_on_canvas).delete()

        # Salvează/actualizează pozițiile și rotația meselor rămase
        for table_data in data.get('tables', []):
            table = Table.objects.get(
                id=table_data['id'],
                location=location
            )
            table.position_x = table_data['x']
            table.position_y = table_data['y']
            table.rotation = table_data.get('rotation', 0)
            table.width = table_data.get('width', 0) or 0
            table.height = table_data.get('height', 0) or 0
            table.radius = table_data.get('radius', 0) or 0
            table.save()

        # Salvează elementele speciale (ca înainte)
        special_elements = data.get('special_elements', [])
        location.special_elements.all().delete()
        from .models import SpecialElement
        for el in special_elements:
            SpecialElement.objects.create(
                location=location,
                type=el['type'],
                label=el.get('label', ''),
                position_x=el['x'],
                position_y=el['y'],
                rotation=el.get('rotation', 0),
                width=el.get('width', 0) or 0,
                height=el.get('height', 0) or 0,
                radius=el.get('radius', 0) or 0
            )

        # NOTIFICARE pentru organizator
        from .models import EventNotification
        staff_user = request.user
        organizer = location.owner  # presupunem că owner este organizatorul
        if organizer and organizer != staff_user:
            mesaj = f"{staff_user.username} a modificat layout-ul pentru locația {location.name}."
            EventNotification.objects.create(
                sender=staff_user,
                receiver=organizer,
                event=None,
                message=mesaj
            )

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required(login_url='/login')
def add_budget(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    budget, created = EventBudget.objects.get_or_create(event=event)
    if request.method == 'POST':
        for field in budget._meta.fields:
            if isinstance(field, models.DecimalField) and field.name.endswith('_cost'):
                value = request.POST.get(field.name, '0')
                try:
                    value = float(value)
                except ValueError:
                    value = 0
                setattr(budget, field.name, value)
        budget.save()
        return redirect('event_details', event_id=event.id)
    return render(request, 'base/add_budget.html', {'event': event, 'budget': budget})


from django.views.decorators.http import require_POST
from django.http import JsonResponse

@require_POST
@login_required(login_url='/login')
def save_menu_ratings(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    if not isinstance(payload, list):
        return JsonResponse({'success': False, 'error': 'Payload must be a list'}, status=400)

    try:
        guest_profile = request.user.profile_set.first().guest_profile
    except AttributeError:
        return JsonResponse({'success': False, 'error': 'Guest profile not found'}, status=400)

    saved, errors = 0, []

    # variables for organizer/location rating aggregated
    organizer_rating = None
    location_rating = None
    organizer_obj = None
    location_obj = None
    event_obj = None

    for entry in payload:
        kind = entry.get('kind', 'dish')
        rating_val = entry.get('rating')

        # validate rating int 1-5
        try:
            rating_val = int(rating_val)
        except (TypeError, ValueError):
            errors.append('Invalid rating value')
            continue
        if rating_val not in range(1,6):
            errors.append('Rating outside range')
            continue

        if kind == 'dish':
            dish_id = entry.get('dish_id')
            dish = Menu.objects.filter(id=dish_id).first()
            if not dish:
                errors.append(f'Dish {dish_id} not found')
                continue
            MenuRating.objects.update_or_create(
                guest=guest_profile,
                menu_item=dish,
                defaults={'rating': rating_val}
            )
            saved += 1
        elif kind == 'organizer':
            organizer_id = entry.get('organizer_id')
            organizer_obj = User.objects.filter(id=organizer_id).first()
            if not organizer_obj:
                errors.append(f'Organizer {organizer_id} not found')
                continue
            organizer_rating = rating_val
            saved += 1
        elif kind == 'location':
            location_id = entry.get('location_id')
            location_obj = Location.objects.filter(id=location_id).first()
            if not location_obj:
                errors.append(f'Location {location_id} not found')
                continue
            location_rating = rating_val
            saved += 1
        else:
            errors.append('Unknown kind')

    # create or update single Review
    if organizer_rating is not None or location_rating is not None:
        review_defaults = {}
        if organizer_rating is not None:
            review_defaults['organizer_stars'] = organizer_rating
        if location_rating is not None:
            review_defaults['location_stars'] = location_rating

        # attempt to get event by organizer & location if exists
        if organizer_obj and location_obj:
            event_obj = Event.objects.filter(organized_by=organizer_obj, location=location_obj).first()

        Review.objects.update_or_create(
            user=request.user,
            event=event_obj,
            defaults=review_defaults | {
                'organizer': organizer_obj,
                'location': location_obj
            }
        )

    return JsonResponse({'success': True, 'saved': saved, 'errors': errors})

def recommendations_view(request, guest_id):

    try:
        guest = Guests.objects.get(id=guest_id)
        
        # Obține recomandările
        recommendations = get_recommendations_for_guest(guest_id, top_n=10)
        
        # Obține informații despre model
        recommender = get_recommender()
        model_info = recommender.get_model_info()
        
        context = {
            'guest': guest,
            'recommendations': recommendations,
            'model_info': model_info,
        }
        
        return render(request, 'base/recommendations.html', context)
        
    except Guests.DoesNotExist:
        messages.error(request, 'Invitatul nu a fost găsit.')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'Eroare la generarea recomandărilor: {e}')
        return redirect('home')

def similar_dishes_view(request, dish_id):
    """
    View pentru afișarea preparatelor similare
    """
    try:
        dish = Menu.objects.get(id=dish_id)
        
        # Obține preparatele similare
        similar_dishes = get_similar_dishes_for_dish(dish_id, top_n=5)
        
        context = {
            'dish': dish,
            'similar_dishes': similar_dishes,
        }
        
        return render(request, 'base/similar_dishes.html', context)
        
    except Menu.DoesNotExist:   
        messages.error(request, 'Preparatul nu a fost găsit.')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'Eroare la găsirea preparatelor similare: {e}')
        return redirect('home')

def model_status_view(request):
    """
    View pentru afișarea statusului modelului
    """
    try:
        recommender = get_recommender()
        model_info = recommender.get_model_info()
        
        # Verifică dacă antrenarea este necesară
        from .management.commands.schedule_model_training import Command as TrainingCommand
        training_check = TrainingCommand()
        
        context = {
            'model_info': model_info,
            'training_check': training_check,
        }
        
        return render(request, 'base/model_status.html', context)
        
    except Exception as e:
        messages.error(request, f'Eroare la verificarea statusului modelului: {e}')
        return redirect('home')

@csrf_exempt
@login_required
def manual_validate_attendance(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    query = (data.get('query') or '').strip()
    event_id = data.get('event_id')
    target_guest_id = data.get('guest_id')  # optional – explicit guest to mark

    if not query or not event_id:
        return JsonResponse({'success': False, 'error': 'Missing parameters'}, status=400)

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Event not found'}, status=404)

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=403)

    guests_qs = Guests.objects.filter(events=event).filter(
        Q(profile__first_name__icontains=query) | Q(profile__last_name__icontains=query)
    ).select_related('profile__user').distinct()

    if not guests_qs.exists():
        return JsonResponse({'success': False, 'error': 'Guest not found'}, status=404)

    existing_log = Log.objects.filter(event=event, profile=guests_qs.first().profile, is_correct=True).first()
    if existing_log:
        return JsonResponse({'success': False, 'error': 'Guest already attended'}, status=400)

    log = Log(event=event, profile=guests_qs.first().profile, is_correct=True)
    if guests_qs.first().profile and guests_qs.first().profile.photo:
        log.photo = guests_qs.first().profile.photo
    else:
        from django.core.files.base import ContentFile
        import base64
        transparent_png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAqsB9WkQrK8AAAAASUVORK5CYII="
        )
        log.photo.save('placeholder.png', ContentFile(transparent_png), save=False)
    log.save()

    table_number = None
    arrangement = TableArrangement.objects.filter(event=event, guest=guests_qs.first()).select_related('table').first()
    if arrangement and arrangement.table:
        table_number = arrangement.table.table_number

    from django.utils import timezone
    created_at = log.created
    if timezone.is_naive(created_at):
        created_at = timezone.make_aware(created_at)
    created_local = timezone.localtime(created_at)

    user_data = {
        'id': guests_qs.first().profile.user.id if guests_qs.first().profile.user else None,
        'name': f"{guests_qs.first().profile.first_name} {guests_qs.first().profile.last_name}" if guests_qs.first().profile else 'Unknown',
        'email': guests_qs.first().profile.user.email if guests_qs.first().profile.user else '',
        'photo_url': guests_qs.first().profile.photo.url if guests_qs.first().profile and guests_qs.first().profile.photo else '',
        'arriving_time': created_local.strftime("%d, %H:%M"),
        'gender': guests_qs.first().gender,
        'cuisine_preference': guests_qs.first().cuisine_preference,
        'is_vegan': guests_qs.first().vegan,
        'allergens': [a.name for a in guests_qs.first().allergens.all()],
        'table_number': table_number,
    }

    return JsonResponse({'success': True, 'user': user_data})



