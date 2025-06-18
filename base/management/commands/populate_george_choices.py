from django.core.management.base import BaseCommand
import random
from base.models import User, Guests, Menu, MenuRating, GuestMenu, Event, Location

class Command(BaseCommand):
    help = "Populate GuestMenu and MenuRating for user George with safe choices."

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='MoldovanDaniela')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User 'George' not found."))
            return

        guest_profile = user.profile_set.first().guest_profile
        if not guest_profile:
            self.stdout.write(self.style.ERROR("Guest profile missing for George."))
            return

        # Choose safe dishes respecting constraints
        safe_dishes = guest_profile.get_safe_menu_items()
        if not safe_dishes.exists():
            self.stdout.write(self.style.WARNING("No safe dishes found for George."))
            return

        # group by category, pick up to 3 per category
        choices = []
        categories = ['appetizer', 'main', 'dessert', 'drink']
        for cat in categories:
            cat_dishes = safe_dishes.filter(category=cat)
            sample_size = min(3, cat_dishes.count())
            choices += random.sample(list(cat_dishes), sample_size)

        if not choices:
            self.stdout.write(self.style.WARNING("No dishes selected."))
            return
        location = Location.objects.get(id=19)
        # ensure GuestMenu
        gm = GuestMenu.objects.create(guest=user, location_menu = location)
        gm.menu_choices.set(choices)

        # add ratings 4 or 5
        for dish in choices:
            MenuRating.objects.update_or_create(
                guest=guest_profile,
                menu_item=dish,
                defaults={'rating': random.choice([3,5])}
            )

        self.stdout.write(self.style.SUCCESS(f"Populated {len(choices)} choices and ratings for George.")) 