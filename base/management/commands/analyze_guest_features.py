from django.core.management.base import BaseCommand
from base.models import Guests, MenuRating
from collections import Counter, defaultdict

class Command(BaseCommand):
    help = "Analizează distribuția caracteristicilor invitaților"

    def handle(self, *args, **options):
        guests = Guests.objects.all()
        ratings = MenuRating.objects.all()
        
        # Găsește invitații activi (cu ratinguri)
        active_guest_ids = set(ratings.values_list('guest_id', flat=True).distinct())
        active_guests = guests.filter(id__in=active_guest_ids)
        
        self.stdout.write("=== ANALIZA CARACTERISTICILOR INVITAȚILOR ===\n")
        
        # Statistici generale
        self.stdout.write(f"Total invitați: {guests.count()}")
        self.stdout.write(f"Invitați activi (cu ratinguri): {active_guests.count()}")
        self.stdout.write(f"Invitați inactivi: {guests.count() - active_guests.count()}\n")
        
        # Analizează fiecare caracteristică
        characteristics = [
            ('diet_preference', 'Preferință dietă'),
            ('spicy_food', 'Preferință picant'),
            ('temp_preference', 'Preferință temperatură'),
            ('cuisine_preference', 'Preferință bucătărie'),
            ('texture_preference', 'Preferință textură'),
            ('nutrition_goal', 'Obiectiv nutrițional'),
            ('preferred_course', 'Cursă preferată'),
        ]
        
        for field, label in characteristics:
            self.stdout.write(f"--- {label} ---")
            
            # Pentru toți invitații
            all_values = list(guests.values_list(field, flat=True))
            all_counter = Counter(all_values)
            
            # Pentru invitații activi
            active_values = list(active_guests.values_list(field, flat=True))
            active_counter = Counter(active_values)
            
            self.stdout.write(f"Toți invitații:")
            for value, count in all_counter.most_common():
                percentage = (count / len(all_values)) * 100
                self.stdout.write(f"  {value}: {count} ({percentage:.1f}%)")
            
            self.stdout.write(f"Invitații activi:")
            for value, count in active_counter.most_common():
                percentage = (count / len(active_values)) * 100 if active_values else 0
                self.stdout.write(f"  {value}: {count} ({percentage:.1f}%)")
            
            # Calculează câți au preferințe setate vs none
            none_values = ['none', 'no_region', 'no_preference', None]
            all_none_count = sum(all_counter.get(val, 0) for val in none_values)
            active_none_count = sum(active_counter.get(val, 0) for val in none_values)
            
            all_set_count = len(all_values) - all_none_count
            active_set_count = len(active_values) - active_none_count
            
            self.stdout.write(f"  → Preferințe setate: {all_set_count}/{len(all_values)} ({all_set_count/len(all_values)*100:.1f}%)")
            self.stdout.write(f"  → Preferințe setate (activi): {active_set_count}/{len(active_values)} ({active_set_count/len(active_values)*100:.1f}%)")
            self.stdout.write("")
        
        # Analizează alergiile
        self.stdout.write("--- Alergii ---")
        guests_with_allergens = guests.filter(allergens__isnull=False).distinct()
        active_with_allergens = active_guests.filter(allergens__isnull=False).distinct()
        
        self.stdout.write(f"Invitați cu alergii: {guests_with_allergens.count()}/{guests.count()} ({guests_with_allergens.count()/guests.count()*100:.1f}%)")
        self.stdout.write(f"Invitați activi cu alergii: {active_with_allergens.count()}/{active_guests.count()} ({active_with_allergens.count()/active_guests.count()*100:.1f}%)")
        
        # Top alergii
        all_allergens = []
        for guest in guests:
            all_allergens.extend(guest.allergens.values_list('name', flat=True))
        
        if all_allergens:
            allergen_counter = Counter(all_allergens)
            self.stdout.write("Top alergii:")
            for allergen, count in allergen_counter.most_common(5):
                self.stdout.write(f"  {allergen}: {count}")
        
        # Recomandări pentru îmbunătățire
        self.stdout.write("\n=== RECOMANDĂRI ===\n")
        
        # Calculează procentul general de preferințe setate
        total_preferences = 0
        total_none_preferences = 0
        
        for field, _ in characteristics:
            values = list(active_guests.values_list(field, flat=True))
            none_values = ['none', 'no_region', 'no_preference', None]
            none_count = sum(1 for val in values if val in none_values)
            total_preferences += len(values)
            total_none_preferences += none_count
        
        preference_rate = ((total_preferences - total_none_preferences) / total_preferences) * 100 if total_preferences > 0 else 0
        
        self.stdout.write(f"Rata generală de preferințe setate: {preference_rate:.1f}%")
        
        if preference_rate < 50:
            self.stdout.write(self.style.WARNING("⚠️  Rata de preferințe este foarte mică! Antrenarea poate fi afectată."))
            self.stdout.write("Recomandări:")
            self.stdout.write("1. Încurajează invitații să completeze preferințele")
            self.stdout.write("2. Folosește date implicite pentru invitații fără preferințe")
            self.stdout.write("3. Generează preferințe bazate pe ratingurile existente")
        elif preference_rate < 70:
            self.stdout.write(self.style.WARNING("⚠️  Rata de preferințe este moderată. Antrenarea va funcționa, dar poate fi îmbunătățită."))
        else:
            self.stdout.write(self.style.SUCCESS("✅ Rata de preferințe este bună pentru antrenare!")) 