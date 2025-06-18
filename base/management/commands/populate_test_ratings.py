from django.core.management.base import BaseCommand
from base.models import Guests, Menu, MenuRating
import random

class Command(BaseCommand):
    help = "Populează ratinguri de test pentru antrenarea modelului LightFM"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=500,
            help="Numărul de ratinguri de test de creat",
        )

    def handle(self, *args, **options):
        guests = list(Guests.objects.all())
        dishes = list(Menu.objects.all())
        count = options['count']

        if not guests:
            self.stdout.write(self.style.WARNING("Nu există invitați în baza de date."))
            return

        if not dishes:
            self.stdout.write(self.style.WARNING("Nu există preparate în baza de date."))
            return

        # Șterge ratingurile existente pentru a începe cu date curate
        MenuRating.objects.all().delete()
        self.stdout.write("Ratingurile existente au fost șterse.")

        ratings_created = 0
        
        for _ in range(count):
            guest = random.choice(guests)
            dish = random.choice(dishes)
            
            # Generează ratinguri realiste bazate pe preferințe
            rating = self._generate_realistic_rating(guest, dish)
            
            # Creează ratingul doar dacă nu există deja
            MenuRating.objects.get_or_create(
                guest=guest,
                menu_item=dish,
                defaults={'rating': rating}
            )
            ratings_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Au fost create {ratings_created} ratinguri de test."))

    def _generate_realistic_rating(self, guest, dish):
        """Generează un rating realist bazat pe preferințele invitatului"""
        base_rating = random.randint(3, 5)  # Majoritatea ratingurilor sunt pozitive
        
        # Bonus pentru potrivirea cu preferințele
        if guest.diet_preference != 'none' and dish.diet_type == guest.diet_preference:
            base_rating += 1
        
        if guest.cuisine_preference and dish.item_cuisine == guest.cuisine_preference:
            base_rating += 1
        
        if guest.spicy_food and dish.spicy_level == guest.spicy_food:
            base_rating += 1
        
        if guest.temp_preference and dish.serving_temp == guest.temp_preference:
            base_rating += 1
        
        # Penalizare pentru alergeni
        if guest.allergens.exists() and dish.allergens.exists():
            common_allergens = guest.allergens.filter(id__in=dish.allergens.values_list('id', flat=True))
            if common_allergens.exists():
                base_rating -= 2
        
        # Asigură-te că ratingul este între 1 și 5
        return max(1, min(5, base_rating)) 