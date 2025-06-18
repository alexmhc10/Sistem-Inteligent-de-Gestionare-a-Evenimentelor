from django.core.management.base import BaseCommand
from base.models import Guests, Menu, MenuRating

class Command(BaseCommand):
    help = "Test rapid pentru a verifica dacă avem suficiente ratinguri pentru antrenare"

    def handle(self, *args, **options):
        ratings = MenuRating.objects.all()
        
        self.stdout.write("=== TEST RAPID RATINGURI ===\n")
        
        if ratings.count() == 0:
            self.stdout.write(self.style.ERROR("❌ Nu există ratinguri în baza de date!"))
            return
        
        # Găsește invitații cu ratinguri
        active_guest_ids = set(ratings.values_list('guest_id', flat=True).distinct())
        active_guests = Guests.objects.filter(id__in=active_guest_ids)
        
        # Găsește preparatele cu ratinguri
        active_dish_ids = set(ratings.values_list('menu_item_id', flat=True).distinct())
        active_dishes = Menu.objects.filter(id__in=active_dish_ids)
        
        self.stdout.write(f"Total ratinguri: {ratings.count()}")
        self.stdout.write(f"Invitați cu ratinguri: {active_guests.count()}")
        self.stdout.write(f"Preparate cu ratinguri: {active_dishes.count()}")
        
        # Verifică dacă avem suficiente date
        if active_guests.count() >= 2 and active_dishes.count() >= 2:
            self.stdout.write(self.style.SUCCESS("✅ Suficiente date pentru antrenare!"))
            self.stdout.write("Poți rula: python manage.py train_recommender --progress")
        else:
            self.stdout.write(self.style.WARNING("⚠️  Insuficiente date pentru antrenare."))
            if active_guests.count() < 2:
                self.stdout.write(f"  - Necesar: cel puțin 2 invitați cu ratinguri (ai {active_guests.count()})")
            if active_dishes.count() < 2:
                self.stdout.write(f"  - Necesar: cel puțin 2 preparate cu ratinguri (ai {active_dishes.count()})")
            
            self.stdout.write("\nPentru a genera ratinguri de test:")
            self.stdout.write("python manage.py populate_test_ratings --count 500") 