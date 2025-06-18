from django.core.management.base import BaseCommand
from base.models import Guests, Menu, MenuRating
from collections import Counter, defaultdict
import numpy as np

class Command(BaseCommand):
    help = "Analizează distribuția ratingurilor și interacțiunilor"

    def handle(self, *args, **options):
        guests = Guests.objects.all()
        dishes = Menu.objects.all()
        ratings = MenuRating.objects.all()

        self.stdout.write("=== ANALIZA RATINGURILOR ===\n")

        # Statistici generale
        self.stdout.write(f"Total invitați: {guests.count()}")
        self.stdout.write(f"Total preparate: {dishes.count()}")
        self.stdout.write(f"Total ratinguri: {ratings.count()}")
        
        if ratings.count() == 0:
            self.stdout.write(self.style.WARNING("Nu există ratinguri în baza de date!"))
            return

        # Distribuția ratingurilor
        rating_counts = Counter(ratings.values_list('rating', flat=True))
        self.stdout.write(f"\nDistribuția ratingurilor:")
        for rating in sorted(rating_counts.keys()):
            count = rating_counts[rating]
            percentage = (count / ratings.count()) * 100
            self.stdout.write(f"  {rating} stele: {count} ({percentage:.1f}%)")

        # Câți invitați au dat ratinguri
        guests_with_ratings = set(ratings.values_list('guest_id', flat=True).distinct())
        guests_without_ratings = guests.count() - len(guests_with_ratings)
        
        self.stdout.write(f"\nInvitați cu ratinguri: {len(guests_with_ratings)}")
        self.stdout.write(f"Invitați fără ratinguri: {guests_without_ratings}")
        
        if guests_without_ratings > 0:
            self.stdout.write(self.style.WARNING(
                f"  {guests_without_ratings} invitați nu au dat nicio evaluare!"))

        # Câte preparate au fost evaluate
        dishes_with_ratings = set(ratings.values_list('menu_item_id', flat=True).distinct())
        dishes_without_ratings = dishes.count() - len(dishes_with_ratings)
        
        self.stdout.write(f"\nPreparate evaluate: {len(dishes_with_ratings)}")
        self.stdout.write(f"Preparate neevaluate: {dishes_without_ratings}")
        
        if dishes_without_ratings > 0:
            self.stdout.write(self.style.WARNING(
                f"  {dishes_without_ratings} preparate nu au fost evaluate!"))

        # Analiză detaliată per invitat
        self.stdout.write(f"\n=== ANALIZĂ PER INVITAT ===")
        guest_rating_counts = defaultdict(int)
        for rating in ratings:
            guest_rating_counts[rating.guest_id] += 1

        if guest_rating_counts:
            min_ratings = min(guest_rating_counts.values())
            max_ratings = max(guest_rating_counts.values())
            avg_ratings = np.mean(list(guest_rating_counts.values()))
            
            self.stdout.write(f"Ratinguri per invitat:")
            self.stdout.write(f"  Minim: {min_ratings}")
            self.stdout.write(f"  Maxim: {max_ratings}")
            self.stdout.write(f"  Medie: {avg_ratings:.1f}")

            # Invitații cu cele mai multe ratinguri
            top_guests = sorted(guest_rating_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            self.stdout.write(f"\nTop 5 invitați cu cele mai multe ratinguri:")
            for guest_id, count in top_guests:
                try:
                    guest = Guests.objects.get(id=guest_id)
                    name = f"{guest.profile.first_name} {guest.profile.last_name}"
                    self.stdout.write(f"  {name}: {count} ratinguri")
                except:
                    self.stdout.write(f"  Invitat ID {guest_id}: {count} ratinguri")

        # Analiză detaliată per preparat
        self.stdout.write(f"\n=== ANALIZĂ PER PREPARAT ===")
        dish_rating_counts = defaultdict(int)
        for rating in ratings:
            dish_rating_counts[rating.menu_item_id] += 1

        if dish_rating_counts:
            min_ratings = min(dish_rating_counts.values())
            max_ratings = max(dish_rating_counts.values())
            avg_ratings = np.mean(list(dish_rating_counts.values()))
            
            self.stdout.write(f"Ratinguri per preparat:")
            self.stdout.write(f"  Minim: {min_ratings}")
            self.stdout.write(f"  Maxim: {max_ratings}")
            self.stdout.write(f"  Medie: {avg_ratings:.1f}")

            # Preparatele cu cele mai multe ratinguri
            top_dishes = sorted(dish_rating_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            self.stdout.write(f"\nTop 5 preparate cu cele mai multe ratinguri:")
            for dish_id, count in top_dishes:
                try:
                    dish = Menu.objects.get(id=dish_id)
                    self.stdout.write(f"  {dish.item_name}: {count} ratinguri")
                except:
                    self.stdout.write(f"  Preparat ID {dish_id}: {count} ratinguri")

        # Verifică dacă există ratinguri pozitive (4-5 stele)
        positive_ratings = ratings.filter(rating__gte=4)
        self.stdout.write(f"\nRatinguri pozitive (4-5 stele): {positive_ratings.count()}")
        
        if positive_ratings.count() < 10:
            self.stdout.write(self.style.WARNING(
                "FOARTE PUȚINE RATINGURI POZITIVE! Modelul nu va putea antrena corect."))

        # Sfaturi pentru îmbunătățire
        self.stdout.write(f"\n=== SFATURI PENTRU ÎMBUNĂTĂȚIRE ===")
        
        if guests_without_ratings > 0:
            self.stdout.write(f"• {guests_without_ratings} invitați nu au dat ratinguri")
            self.stdout.write(f"  → Rulează 'populate_test_ratings' pentru a genera ratinguri de test")
        
        if dishes_without_ratings > 0:
            self.stdout.write(f"• {dishes_without_ratings} preparate nu au fost evaluate")
            self.stdout.write(f"  → Asigură-te că toate preparatele sunt disponibile pentru evaluare")
        
        if positive_ratings.count() < 50:
            self.stdout.write(f"• Doar {positive_ratings.count()} ratinguri pozitive")
            self.stdout.write(f"  → Generează mai multe ratinguri pozitive pentru antrenare")

        self.stdout.write(self.style.SUCCESS("\n✓ Analiza completă!")) 