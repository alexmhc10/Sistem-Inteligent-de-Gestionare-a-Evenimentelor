from django.core.management.base import BaseCommand
from base.models import Guests, Menu, MenuRating
from collections import Counter

class Command(BaseCommand):
    help = "Îmbunătățește preferințele invitaților bazate pe ratingurile lor"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Arată ce s-ar schimba fără a face modificări",
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write("DRY-RUN MODE - Nu se vor face modificări\n")
        
        guests = Guests.objects.all()
        ratings = MenuRating.objects.all()
        
        self.stdout.write("=== ÎMBUNĂTĂȚIRE PREFERINȚE ===\n")
        
        changes_made = 0
        
        for guest in guests:
            guest_ratings = ratings.filter(guest=guest)
            if not guest_ratings.exists():
                continue
                
            self.stdout.write(f"\n--- {guest.profile.first_name if guest.profile else 'Invitat'} {guest.profile.last_name if guest.profile else ''} ---")
            
            # Analizează ratingurile
            positive_dishes = []
            for rating in guest_ratings.filter(rating__gte=4):
                dish = rating.menu_item
                positive_dishes.append({
                    'diet_type': dish.diet_type,
                    'spicy_level': dish.spicy_level,
                    'serving_temp': dish.serving_temp,
                    'cuisine': dish.item_cuisine,
                    'category': dish.category,
                    'protein_g': dish.protein_g,
                    'calories': dish.calories
                })
            
            if not positive_dishes:
                continue
            
            # Generează preferințe
            preferences = {}
            
            # Dietă
            if guest.diet_preference == 'none':
                diet_types = [d['diet_type'] for d in positive_dishes if d['diet_type'] and d['diet_type'] != 'none']
                if diet_types:
                    diet_counter = Counter(diet_types)
                    most_common = diet_counter.most_common(1)[0][0]
                    preferences['diet_preference'] = most_common
            
            # Picant
            if guest.spicy_food == 'none':
                spicy_levels = [d['spicy_level'] for d in positive_dishes if d['spicy_level']]
                if spicy_levels:
                    spicy_counter = Counter(spicy_levels)
                    most_common = spicy_counter.most_common(1)[0][0]
                    preferences['spicy_food'] = most_common
            
            # Bucătărie
            if not guest.cuisine_preference or guest.cuisine_preference == 'no_region':
                cuisines = [d['cuisine'] for d in positive_dishes if d['cuisine'] and d['cuisine'] != 'no_region']
                if cuisines:
                    cuisine_counter = Counter(cuisines)
                    most_common = cuisine_counter.most_common(1)[0][0]
                    preferences['cuisine_preference'] = most_common
            
            # Obiectiv nutrițional
            if guest.nutrition_goal == 'none':
                high_protein = [d for d in positive_dishes if d['protein_g'] and d['protein_g'] >= 20]
                low_calorie = [d for d in positive_dishes if d['calories'] and d['calories'] <= 400]
                
                if len(high_protein) > len(positive_dishes) * 0.3:
                    preferences['nutrition_goal'] = 'high_protein'
                elif len(low_calorie) > len(positive_dishes) * 0.3:
                    preferences['nutrition_goal'] = 'low_fat'
                else:
                    preferences['nutrition_goal'] = 'balanced'
            
            # Cursă preferată
            if not guest.preferred_course:
                categories = [d['category'] for d in positive_dishes]
                if categories:
                    category_counter = Counter(categories)
                    most_common = category_counter.most_common(1)[0][0]
                    preferences['preferred_course'] = most_common
            
            # Aplică preferințele
            for field, value in preferences.items():
                if not dry_run:
                    setattr(guest, field, value)
                    self.stdout.write(f"    {field}: {value}")
                else:
                    self.stdout.write(f"    {field}: {value} (DRY-RUN)")
                changes_made += 1
            
            if preferences and not dry_run:
                guest.save()
        
        self.stdout.write(f"\n=== REZULTAT ===\n")
        self.stdout.write(f"Total modificări: {changes_made}")
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS("Preferințele au fost îmbunătățite!"))
        else:
            self.stdout.write("Rulează fără --dry-run pentru a aplica modificările") 