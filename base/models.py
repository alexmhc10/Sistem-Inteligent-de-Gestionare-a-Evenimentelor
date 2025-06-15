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
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True, default="poze_invitati/male.jpg")
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
        return self.user.username


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


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organizer_reviews', null=True, blank=True)
    comment = models.TextField()
    stars = models.IntegerField(choices=[(i, f"{i} stele") for i in range(1, 6)], default=5)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.comment[0:20]

    

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


class Guests(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='guest_profile', null=True)
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Feminin')
        ]
    REGION_CHOICES = [
        ('no_region', 'No region'),
        ('italian', 'Italian'),
        ('french', 'French'),
        ('mexican', 'Mexican'),
        ('indian', 'Indian'),
        ('chinese', 'Chinese'),
        ('japanese', 'Japanese'),
        ('american', 'American'),
        ('mediterranean', 'Mediterranean'),
        ('romanian', 'Romanian'),
        ('spanish', 'Spanish'),
        ('thai', 'Thai'),
        ('greek', 'Greek'),
        ('turkish', 'Turkish'),
        ('german', 'German'),
        ('korean', 'Korean'),
        ('vietnamese', 'Vietnamese'),
        ('lebanese', 'Lebanese'),
        ('brazilian', 'Brazilian'),
        ('ethiopian', 'Ethiopian'),
        ('russian', 'Russian'),
        ('moroccan', 'Moroccan'),
        ('caribbean', 'Caribbean'),
        ('african', 'African'),
        ('british', 'British'),
        ('australian', 'Australian'),
        ('persian', 'Persian'),
        ('polish', 'Polish'),
        ('portuguese', 'Portuguese'),
        ('cuban', 'Cuban'),
        ('jamaican', 'Jamaican'),
        ('swedish', 'Swedish'),
        ('egyptian', 'Egyptian'),
        ('indonesian', 'Indonesian'),
        ('malaysian', 'Malaysian'),
        ('pakistani', 'Pakistani'),
        ('syrian', 'Syrian'),
        ('argentinian', 'Argentinian'),
        ('peruvian', 'Peruvian'),
        ('filipino', 'Filipino'),
    ]
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    picture = models.ImageField(upload_to='poze_invitati/', null=True, blank=True)
    cuisine_preference = models.CharField(max_length=50, choices=REGION_CHOICES ,blank=True, null=True)
    vegan = models.BooleanField(default=False)
    allergens = models.ManyToManyField(Allergen, blank=True)
    state = models.BooleanField(default=False)
    def __str__(self):
        return self.profile.username


class Menu(models.Model):
    CATEGORY_CHOICES = [
        ('appetizer', 'Appetizer'),
        ('main', 'Main'),
        ('dessert', 'Desert'),
        ('drink', 'Drink'),
    ]
    REGION_CHOICES = [
        ('no_region', 'No region'),
        ('italian', 'Italian'),
        ('french', 'French'),
        ('mexican', 'Mexican'),
        ('indian', 'Indian'),
        ('chinese', 'Chinese'),
        ('japanese', 'Japanese'),
        ('american', 'American'),
        ('mediterranean', 'Mediterranean'),
        ('romanian', 'Romanian'),
        ('spanish', 'Spanish'),
        ('thai', 'Thai'),
        ('greek', 'Greek'),
        ('turkish', 'Turkish'),
        ('german', 'German'),
        ('korean', 'Korean'),
        ('vietnamese', 'Vietnamese'),
        ('lebanese', 'Lebanese'),
        ('brazilian', 'Brazilian'),
        ('ethiopian', 'Ethiopian'),
        ('russian', 'Russian'),
        ('moroccan', 'Moroccan'),
        ('caribbean', 'Caribbean'),
        ('african', 'African'),
        ('british', 'British'),
        ('australian', 'Australian'),
        ('persian', 'Persian'),
        ('polish', 'Polish'),
        ('portuguese', 'Portuguese'),
        ('cuban', 'Cuban'),
        ('jamaican', 'Jamaican'),
        ('swedish', 'Swedish'),
        ('egyptian', 'Egyptian'),
        ('indonesian', 'Indonesian'),
        ('malaysian', 'Malaysian'),
        ('pakistani', 'Pakistani'),
        ('syrian', 'Syrian'),
        ('argentinian', 'Argentinian'),
        ('peruvian', 'Peruvian'),
        ('filipino', 'Filipino'),
    ]
    at_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    item_name = models.CharField(max_length=80)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='main')
    item_cuisine = models.CharField(max_length=20, choices=REGION_CHOICES, default='No region')
    item_vegan = models.BooleanField(default=False)
    allergens = models.ManyToManyField(Allergen, blank=True)
    item_picture = models.ImageField(upload_to=menu_item_upload_path, null=True, blank=True)
    def __str__(self):
        return f"{self.item_name} at {self.at_location}"


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


class GuestMenu(models.Model):
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name="guest")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event")
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
    def update_locations(self, locations):
        locations = Location.objects.all()
        current_month = now().date().replace(day=1)
        if self.last_location_update != current_month:
            self.initial_budget = self.total_budget
            total_location_cost = sum(location.cost for location in locations)
            self.total_expenses += total_location_cost
            self.final_budget = self.total_budget - self.total_expenses
            self.last_location_update = current_month
            self.save()
    
    def add_new_location(self, location_cost):
        self.total_expenses += location_cost
        self.final_budget -= self.total_expenses
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
    position_x = models.FloatField(default=0)  # procent din lățimea containerului
    position_y = models.FloatField(default=0)  # procent din înălțimea containerului
    is_reserved = models.BooleanField(default=False, help_text="Reserved for special groups (e.g., bride and groom)")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the table")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['table_number']
        unique_together = ['location', 'table_number']

    def __str__(self):
        return f"Table {self.table_number} at {self.location.name}"


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