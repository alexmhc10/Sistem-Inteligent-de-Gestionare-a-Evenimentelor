from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from datetime import datetime, timedelta
import os
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from .constants import REGION_CHOICES, DIET_CHOICES, TEXTURE_CHOICES, NUTRITION_GOAL_CHOICES, TEMP_CHOICES, COOKING_METHOD_CHOICES
import uuid
from django.urls import reverse


class EventHistory(models.Model):
    event_name = models.CharField(max_length=255)
    event_date = models.DateTimeField()
    event_time = models.TimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    organized_by = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.event_name} on {self.event_date}"

    class Meta:
        verbose_name = 'Event History'
        verbose_name_plural = 'Event Histories'


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    

class Type(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Location(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    user_account = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='user_account')
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    gallery = models.ImageField(upload_to='images/', null=True, blank=True)
    location = models.TextField(max_length=30)
    types = models.ManyToManyField(Type, blank=True)
    seats_numbers = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2,default=3000)
    number = models.CharField(max_length=20, default="+(40) 74 83 64 823")
    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128) 
    email = models.EmailField()
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True, default="poze_invitati/male.png")
    cv_file = models.FileField(upload_to='cv_folder', null=True, blank=True)
    approved = models.BooleanField(default=False)
    number = models.CharField(max_length=15,default="+(40) 748364823")
    age = models.IntegerField(default=20)
    first_name = models.CharField(null=True, blank=True,max_length=15)
    last_name = models.CharField(null=True, blank=True,max_length=15)
    location = models.CharField(null=True, blank=True,max_length=60)
    street = models.CharField(null=True, blank=True,max_length=100)
    zip_code = models.CharField(null=True, blank=True,max_length=10)
    facebook = models.CharField(null=True, blank=True,max_length=100)
    instagram = models.CharField(null=True, blank=True,max_length=100)
    work_link = models.CharField(null=True, blank=True,max_length=100)
    google_link = models.CharField(null=True, blank=True,max_length=100)
    country = models.CharField(null=True, blank=True,max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    welcome_email_sent = models.BooleanField(default=False)
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('organizer', 'Organizer'),
        ('guest', 'Guest'),
        ('staff', 'Staff')
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='guest'
    )
    def __str__(self):
        # user poate fi None pentru profiluri create înainte de asocierea unui User.
        if self.user:
            return self.user.username
        return self.username or f"Profile #{self.pk}"

    @property
    def is_complete(self):
        required_fields = [
            self.first_name,
            self.last_name,
            self.age,
            self.photo,
        ]
        return all(required_fields)

    def get_missing_fields(self):
        field_mapping = {
            'first_name': 'first name',
            'last_name': 'last name',
            'age': 'age',
            'photo': 'profile picture',
        }
        missing = []
        for field, label in field_mapping.items():
            val = getattr(self, field)
            if not val:
                missing.append(label)
        return missing


class Notification(models.Model):
    ACTION_TYPES = [
        ('created_event', 'Created Event'),
        ('updated_event', 'Updated Event'),
        ('deleted_event', 'Deleted Event'),
        ('created_location', 'Created Location'),
        ('updated_location', 'Updated Location'),
        ('deleted_location', 'Deleted Location'),
        ('updated_profile', 'Updated Profile'),
        ('completed_event', 'Completed Event'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    target_object_id = models.PositiveIntegerField()
    target_object_name = models.CharField(max_length=100, null=True, blank=True)
    target_model = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} at {self.timestamp}"


class DeviceAccess(models.Model):
    device_name = models.CharField(max_length=255)
    os_name = models.CharField(max_length=255)
    last_access_time = models.DateTimeField(auto_now=True)
    user_agent = models.CharField(max_length=512)

    def __str__(self):
        return f"{self.device_name} running {self.os_name} at {self.last_access_time}"

    

def menu_item_upload_path(instance, filename):
    location_name = instance.at_location.name if instance.at_location else "default"
    folder_path = os.path.join(settings.MEDIA_ROOT, location_name, "menu_items")
    
    os.makedirs(folder_path, exist_ok=True)

    return os.path.join(location_name, "menu_items", filename)


class Allergen(models.Model):
    name = models.CharField(max_length=80)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.name  

from .constants import REGION_CHOICES


class Guests(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='guest_profile', null=True)
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Feminin')
        ]
    SPICY_LEVELS = [
        ('none', 'None'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    picture = models.ImageField(upload_to='poze_invitati/', null=True, blank=True)
    cuisine_preference = models.CharField(max_length=50, choices=REGION_CHOICES ,blank=True, null=True)
    diet_preference = models.CharField(max_length=15, choices=DIET_CHOICES, default='none')
    allergens = models.ManyToManyField(Allergen, blank=True)
    medical_conditions = models.ManyToManyField('MedicalCondition', blank=True)
    custom_medical_notes = models.TextField(null=True, blank=True)
    spicy_food = models.CharField(max_length=10, choices=SPICY_LEVELS, default='none', blank=True, null=True)
    state = models.BooleanField(default=False)
    texture_preference = models.CharField(max_length=10, choices=TEXTURE_CHOICES, default='none', blank=True, null=True)
    nutrition_goal = models.CharField(max_length=15, choices=NUTRITION_GOAL_CHOICES, default='none', blank=True, null=True)
    temp_preference = models.CharField(max_length=5, choices=TEMP_CHOICES, default='hot', blank=True, null=True)
    preferred_course = models.CharField(max_length=20, choices=[('appetizer','Appetizer'),('main','Main'),('dessert','Dessert'),('drink','Drink')], blank=True, null=True)
    def __str__(self):
        return self.profile.username

    def get_missing_fields(self):
        field_mapping = {
            'age': 'age',
            'gender': 'gender',
            'cuisine_preference': 'cuisine preference',
            'diet_preference': 'diet preference',
            'texture_preference': 'texture preference',
            'nutrition_goal': 'nutrition goal',
        }
        missing = []
        for field, label in field_mapping.items():
            val = getattr(self, field)
            if not val:
                missing.append(label)
        return missing

    @property
    def vegan(self):
        return self.diet_preference == 'vegan'

    @vegan.setter
    def vegan(self, value: bool):
        """Permit setarea convențională .vegan = True/False.
        Dacă True → diet_preference devine 'vegan'. Dacă False și dieta curentă este 'vegan', se resetează la 'none'."""
        if value:
            self.diet_preference = 'vegan'
        else:
            if self.diet_preference == 'vegan':
                self.diet_preference = 'none'

    def get_safe_menu_items(self):

        from django.db.models import Q

        menu_qs = Menu.objects.all()

        if self.diet_preference and self.diet_preference != 'none':
            DIET_COMPATIBILITY = {
                'vegan': ['vegan'],
                'vegetarian': ['vegetarian', 'vegan'],
                'pescatarian': ['pescatarian', 'vegetarian', 'vegan'],
                'low_carb': ['low_carb', 'keto'],
                'keto': ['keto'],
                'halal': ['halal'],
                'kosher': ['kosher'],
            }
            allowed_diets = DIET_COMPATIBILITY.get(self.diet_preference, [self.diet_preference])
            menu_qs = menu_qs.filter(diet_type__in=allowed_diets)

        if self.allergens.exists():
            menu_qs = menu_qs.exclude(allergens__in=self.allergens.all()).distinct()

        preference = self.spicy_food or 'none'
        order = ['none', 'low', 'medium', 'high']
        if preference in order and preference != 'none':
            allowed_levels = order[: order.index(preference) + 1]
            menu_qs = menu_qs.filter(spicy_level__in=allowed_levels)

        if self.temp_preference:
            menu_qs = menu_qs.filter(serving_temp=self.temp_preference)

        if self.cuisine_preference and self.cuisine_preference != 'no_region':
            from django.db.models import Case, When, Value, IntegerField
            menu_qs = menu_qs.annotate(
                _pref=Case(
                    When(item_cuisine=self.cuisine_preference, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by('_pref')

        return menu_qs.distinct()


class Menu(models.Model):
    CATEGORY_CHOICES = [
        ('appetizer', 'Appetizer'),
        ('main', 'Main'),
        ('dessert', 'Desert'),
        ('drink', 'Drink'),
    ]
    
    at_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    item_name = models.CharField(max_length=80)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='main')
    item_cuisine = models.CharField(max_length=20, choices=REGION_CHOICES, default='No region')
    diet_type = models.CharField(max_length=15, choices=DIET_CHOICES, default='none')

    SPICY_LEVELS = [
        ('none', 'None'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]
    spicy_level = models.CharField(max_length=10, choices=SPICY_LEVELS, default='none')
    allergens = models.ManyToManyField(Allergen, blank=True)
    item_picture = models.ImageField(upload_to=menu_item_upload_path, null=True, blank=True)
    cooking_method = models.CharField(max_length=10, choices=COOKING_METHOD_CHOICES, blank=True, null=True)
    serving_temp = models.CharField(max_length=5, choices=TEMP_CHOICES, default='hot')
    calories = models.PositiveIntegerField(null=True, blank=True, help_text="kcal per serving")
    protein_g = models.PositiveIntegerField(null=True, blank=True)
    carbs_g = models.PositiveIntegerField(null=True, blank=True)
    fat_g = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.item_name} at {self.at_location}"

    @property
    def item_vegan(self):
        return self.diet_type == 'vegan'


class Event(models.Model):
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    event_name = models.CharField(max_length=100)
    event_date = models.DateField()
    event_time = models.TimeField()
    event_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    guests = models.ManyToManyField(Guests, related_name='events', blank=True)
    completed = models.BooleanField(default=False) 
    types = models.ManyToManyField(Type, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=3000)
    updated_at = models.DateTimeField(auto_now=True)
    is_canceled = models.BooleanField(default=False)
    organized_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE, 
        related_name="organized_events",
        blank=True,
        null=True
    )

    def clean(self):
        if self.organized_by and self.organized_by.is_superuser:
            raise ValidationError("Superuser-ul nu poate organiza evenimente.")

        # if self.event_date and self.event_date < now().date():
        #     raise ValidationError("Data evenimentului nu poate fi în trecut.")
        
    def __str__(self):
        return self.event_name

    @property
    def is_completed(self):
        return self.event_date <= now().date()
    
    @property
    def status(self):
        now = timezone.now()
        extended_end = (datetime.combine(self.event_date, self.event_time) + timedelta(hours=12))

        if now < datetime.combine(self.event_date, self.event_time) - timedelta(hours=1):
            return 'upcoming'
        elif now >= datetime.combine(self.event_date, self.event_time) - timedelta(hours=1) and now < extended_end:
            return 'ongoing'
        else:
            return 'completed'

    @property
    def name(self):
        """Return the event name (alias used în diverse alte module)."""
        return self.event_name

    def get_absolute_url(self):
        """Return canonical URL for the event details page."""
        return reverse("event_details", kwargs={"event_id": self.pk})

class OptimisedEvent(models.Model):

    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        related_name='optimisation_results',
        verbose_name="Eveniment"
    )

    original_location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='optimised_original_events',
        verbose_name="Locație inițială"
    )
    original_location_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Cost locație inițială"
    )

    optimized_location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='optimised_new_events',
        verbose_name="Locație optimizată"
    )
    optimized_location_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Cost locație optimizată"
    )

    event_gross_profit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Profit brut eveniment"
    )

    profit_net_old = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Profit net inițial"
    )

    profit_net_new = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Profit net optimizat"
    )

    optimized_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data optimizării"
    )

    run_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False, 
        unique=False,
        verbose_name="ID Rulare Optimizare"
    )

    class Meta:
        ordering = ['-optimized_at', 'event__event_date']
        verbose_name = "Eveniment Optimizat"
        verbose_name_plural = "Evenimente Optimizate"

    def __str__(self):
        return (
            f"Optimizare pentru '{self.event.event_name}' (ID: {self.event.id}) "
            f"la {self.optimized_at.strftime('%Y-%m-%d %H:%M')}"
        )


class GuestMenu(models.Model):
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name="guest", default=None)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event", null=True, blank=True)
    location_menu = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="location_menu", default=None)
    menu_choices = models.ManyToManyField(Menu, blank=True, related_name="menu_choices")

    def __str__(self):
        return f"Menu Choises - {self.guest} for {self.event}"
    

class EventNotification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reciever", null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    def __str__(self):
        return f"From {self.sender} to {self.receiver if self.receiver else 'All'} for {self.event}"


class RSVP(models.Model):
    RESPONSE_CHOICES = [
        ("Accepted", "Accepted"),
        ("Declined", "Declined"),
        ("Pending", "Pending"),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="rsvps")
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rsvps")
    response = models.CharField(max_length=10, choices=RESPONSE_CHOICES, default="Pending")
    responded = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.guest.username} - {self.event.event_name} - {self.response}"


class Log(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    photo = models.ImageField(upload_to='logs')
    is_correct = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) 


class EventMenu(models.Model):
    CATEGORY_CHOICES = [
        ('appetizer', 'Appetizer'),
        ('main', 'Main'),
        ('dessert', 'Desert'),
        ('drink', 'Drink'),
    ]
    event = models.ForeignKey(Event, related_name='menus', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=80)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='main')
    description = models.TextField(null=True, blank=True)
    item_cuisine = models.CharField(max_length=20)
    item_vegan = models.BooleanField(default=False)
    allergens = models.JSONField(default=list, blank=True, null=True)
    item_picture = models.ImageField(upload_to='event_menus/', null=True, blank=True)

    def __str__(self):
        return self.item_name


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username}: {self.body}'
    
    class Meta:
        ordering = ['-created']


from decimal import Decimal

class Budget(models.Model):
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    initial_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_budget = models.DecimalField(max_digits=12, decimal_places=2, default=100000)
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    last_location_update = models.DateField(null=True, blank=True)
    
    def update_budget_for_event(self, event_cost):
        self.total_revenue += event_cost
        self.final_budget += event_cost 
        self.save()
    def update_locations(self, locations_param_unused): 
        current_month_start_date = now().date().replace(day=1)

        if self.last_location_update is None or self.last_location_update < current_month_start_date:
            self.initial_budget = self.total_budget

            all_active_locations = Location.objects.all()
            monthly_location_cost = sum(location.cost for location in all_active_locations)

            self.total_expenses += monthly_location_cost

            self.final_budget = self.initial_budget - monthly_location_cost

            self.last_location_update = current_month_start_date
            self.save()
    
    def add_new_location(self, location_cost):
        self.total_expenses += location_cost
        self.final_budget -= self.location_cost
        self.save()
    
    def calc_profit(self):
        today = now().date()
        next_day = today.replace(day=28) + timedelta(days=4)
        if next_day.month != today.month:
            self.profit = ((self.final_budget - self.initial_budget) / self.initial_budget) * 100
            self.total_budget = self.final_budget
            self.initial_budget = 0
            self.final_budget = 0
            company_profit = CompanyProfit(profit=self.profit)
            company_profit.save()


class CompanyProfit(models.Model):
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Profit of {self.profit} at {self.created_at}"


class Salary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=1500)  
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    total_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    initial_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    last_month_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_total_salary(self):
        self.total_salary = self.base_salary + self.bonus
        self.final_salary = self.total_salary
        self.last_month_salary = self.final_salary
        self.save()

    def update_bonus_for_event(self, event_cost):
        bonus_percentage = Decimal("0.40") 
        self.bonus += event_cost * bonus_percentage
        self.calculate_total_salary()
        self.save()

    def __str__(self):
        return f"Salary for {self.user.username}: {self.total_salary}"


class LocationImages(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Imagine pentru {self.location.name}"


class EventGallery(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='archives')
    archive = models.FileField(upload_to='event_archives/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class EventPost(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    like_count = models.PositiveIntegerField(default=0)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)],null=True, blank=True)

    def __str__(self):
        return f"{self.author}: {self.title} for {self.event.event_name}"


class PostImage(models.Model):
    post = models.ForeignKey(EventPost, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='post_images/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
    def __str__(self):
        return f"Image {self.order} for {self.post.title}"


class PostLike(models.Model):
    post = models.ForeignKey(EventPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
    def __str__(self):
        return f"{self.user} liked {self.post.title}"


class PostComment(models.Model):
    post = models.ForeignKey(EventPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


class Table(models.Model):
    SHAPE_CHOICES = [
        ('round', 'Round'),
        ('rectangle', 'Rectangle'),
        ('square', 'Square')
    ]
    
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='tables')
    table_number = models.IntegerField()
    capacity = models.IntegerField(help_text="Number of seats at this table")
    shape = models.CharField(max_length=20, choices=SHAPE_CHOICES, default='round')
    position_x = models.FloatField(default=0) 
    position_y = models.FloatField(default=0)
    width = models.FloatField(default=0, null=True, blank=True)
    height = models.FloatField(default=0, null=True, blank=True)
    radius = models.FloatField(default=0, null=True, blank=True)
    is_reserved = models.BooleanField(default=False, help_text="Reserved for special groups (e.g., bride and groom)")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the table")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rotation = models.FloatField(default=0)
    class Meta:
        ordering = ['table_number']
        unique_together = ['location', 'table_number']

    def __str__(self):
        return f"Table {self.table_number} at {self.location.name}"


class EventLayout(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='layouts')
    event = models.OneToOneField('Event', on_delete=models.SET_NULL, null=True, blank=True, related_name='layout')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cloned_from = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    is_default  = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.location.name} – {self.name}"


class TableGroup(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='table_groups')
    name = models.CharField(max_length=100, help_text="Name of the group (e.g., 'Bride's Family', 'Groom's Colleagues')")
    guests = models.ManyToManyField(Guests, related_name='table_groups')
    preferred_tables = models.ManyToManyField(Table, blank=True, related_name='preferred_by_groups')
    notes = models.TextField(blank=True, null=True, help_text="Special notes about this group")
    priority = models.IntegerField(default=0, help_text="Higher number means higher priority in table assignment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'name']

    def __str__(self):
        return f"{self.name} for {self.event.event_name}"


class TableArrangement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected')
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='table_arrangements')
    guest = models.ForeignKey(Guests, on_delete=models.CASCADE, related_name='table_arrangements')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='arrangements')
    seat_number = models.IntegerField(help_text="Specific seat number at the table")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_requirements = models.TextField(blank=True, null=True, help_text="Any special requirements for this guest")
    is_priority = models.BooleanField(default=False, help_text="Whether this guest has priority seating")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['table__table_number', 'seat_number']
        unique_together = ['event', 'guest']  # One guest can only be assigned to one table per event

    def __str__(self):
        return f"{self.guest} at Table {self.table.table_number} (Seat {self.seat_number})"


class TableArrangementLog(models.Model):
    """Model to track changes in table arrangements"""
    arrangement = models.ForeignKey(TableArrangement, on_delete=models.CASCADE, related_name='logs')
    previous_table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, related_name='previous_arrangements')
    previous_seat = models.IntegerField(null=True)
    reason = models.TextField(help_text="Reason for the change")
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.arrangement} - {self.created_at}"


class SpecialElement(models.Model):
    ELEMENT_TYPES = [
        ('entrance', 'Entrance'),
        ('dancefloor', 'Dance Floor'),
        ('dj', 'DJ/Band'),
        ('restrooms', 'Restrooms'),
        ('bar', 'Bar'),
        ('kitchen', 'Kitchen'),
        ('emergency', 'Emergency Exit'),
        ('photobooth', 'Photo Booth'),
        ('kids', 'Kids Area'),
        ('custom', 'Custom'),
    ]
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='special_elements')
    type = models.CharField(max_length=32, choices=ELEMENT_TYPES)
    label = models.CharField(max_length=64, blank=True)
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    width = models.FloatField(default=0, null=True, blank=True)
    height = models.FloatField(default=0, null=True, blank=True)
    radius = models.FloatField(default=0, null=True, blank=True)
    rotation = models.FloatField(default=0)

    def __str__(self):
        return f"{self.get_type_display()} at {self.location.name}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organizer_reviews', null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    organizer_stars = models.IntegerField(choices=[(i, f"{i} stele") for i in range(1, 6)], default=5)
    location_stars = models.IntegerField(choices=[(i, f"{i} stele") for i in range(1, 6)], default=5)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.user.username


class EventBudget(models.Model):
    event = models.OneToOneField('Event', on_delete=models.CASCADE, related_name='eventbudget')
    # Venue & Ceremony
    venue_rental_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ceremony_location_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    furniture_rental_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    decorations_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Attire & Accessories
    wedding_dress_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    groom_suit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    accessories_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shoes_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Photography & Video
    photographer_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    videographer_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    photo_booth_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Entertainment
    band_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dj_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sound_system_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Beauty and Health
    hair_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    makeup_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    spa_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Flowers & Decorations
    bouquet_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    centerpieces_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ceremony_flowers_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Catering
    food_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    beverages_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cake_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    snacks_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Stationery & Gifts
    invitations_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    favors_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    thank_you_cards_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Transportation
    wedding_car_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    guest_shuttle_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Miscellaneous
    insurance_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    license_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    planner_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Organizer Payment
    organizer_payment_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def total_budget(self):
        fields = [
            'venue_rental_cost', 'ceremony_location_cost', 'furniture_rental_cost', 'decorations_cost',
            'wedding_dress_cost', 'groom_suit_cost', 'accessories_cost', 'shoes_cost',
            'photographer_cost', 'videographer_cost', 'photo_booth_cost',
            'band_cost', 'dj_cost', 'sound_system_cost',
            'hair_cost', 'makeup_cost', 'spa_cost',
            'bouquet_cost', 'centerpieces_cost', 'ceremony_flowers_cost',
            'food_cost', 'beverages_cost', 'cake_cost', 'snacks_cost',
            'invitations_cost', 'favors_cost', 'thank_you_cards_cost',
            'wedding_car_cost', 'guest_shuttle_cost',
            'insurance_cost', 'license_cost', 'planner_cost', 'organizer_payment_cost',
        ]
        return sum(getattr(self, f) or 0 for f in fields)

    def __str__(self):
        return f"Budget for {self.event.event_name}"


class MenuRating(models.Model):
    guest = models.ForeignKey('Guests', on_delete=models.CASCADE, related_name='menu_ratings')
    menu_item = models.ForeignKey('Menu', on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("guest", "menu_item")

    def __str__(self):
        return f"{self.guest} rated {self.menu_item} - {self.rating}★"


class MedicalCondition(models.Model):
    """Common health conditions that impact food choices."""
    name = models.CharField(max_length=100, unique=True)  # e.g. "Diabetes", "Lactose intolerance"
    is_common = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Medical Condition"
        verbose_name_plural = "Medical Conditions"

    def __str__(self):
        return self.name