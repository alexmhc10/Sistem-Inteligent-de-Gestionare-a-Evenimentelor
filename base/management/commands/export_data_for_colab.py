from django.core.management.base import BaseCommand
from base.models import Guests, Menu, MenuRating
import json
import os
from django.conf import settings

class Command(BaseCommand):
    help = "Exportă datele pentru antrenarea LightFM în Google Colab"

    def add_arguments(self, parser):
        parser.add_argument(
            "--format",
            choices=['json', 'csv'],
            default='json',
            help="Formatul de export (json sau csv)",
        )
        parser.add_argument(
            "--output",
            default='colab_data',
            help="Numele fișierului de output (fără extensie)",
        )

    def handle(self, *args, **options):
        format_type = options['format']
        output_name = options['output']
        
        self.stdout.write("Exporting data for Google Colab...")
        
        # Obține datele
        ratings = MenuRating.objects.all()
        guests = Guests.objects.all()
        dishes = Menu.objects.all()
        
        # Găsește invitații și preparatele active (cu ratinguri)
        active_guest_ids = set(ratings.values_list('guest_id', flat=True).distinct())
        active_dish_ids = set(ratings.values_list('menu_item_id', flat=True).distinct())
        
        active_guests = guests.filter(id__in=active_guest_ids)
        active_dishes = dishes.filter(id__in=active_dish_ids)
        
        self.stdout.write(f"Exporting {active_guests.count()} guests, {active_dishes.count()} dishes, {ratings.count()} ratings")
        
        if format_type == 'json':
            self._export_json(active_guests, active_dishes, ratings, output_name)
        else:
            self._export_csv(active_guests, active_dishes, ratings, output_name)
        
        self.stdout.write(self.style.SUCCESS(f"✓ Data exported to {output_name, 'fisier_nou'}.{format_type}"))
        self.stdout.write("Upload this file to Google Colab!")

    def _export_json(self, guests, dishes, ratings, output_name):
        # Export guests
        guests_data = []
        for guest in guests:
            guest_data = {
                'id': guest.id,
                'first_name': guest.profile.first_name if guest.profile else '',
                'last_name': guest.profile.last_name if guest.profile else '',
                'diet_preference': guest.diet_preference or 'none',
                'spicy_food': guest.spicy_food or 'none',
                'temp_preference': guest.temp_preference or 'hot',
                'cuisine_preference': guest.cuisine_preference or 'no_region',
                'texture_preference': guest.texture_preference or 'none',
                'nutrition_goal': guest.nutrition_goal or 'none',
                'preferred_course': guest.preferred_course or 'main',
                'allergens': list(guest.allergens.values_list('name', flat=True))
            }
            guests_data.append(guest_data)
        
        # Export dishes
        dishes_data = []
        for dish in dishes:
            dish_data = {
                'id': dish.id,
                'name': dish.item_name,
                'category': dish.category,
                'cuisine': dish.item_cuisine or 'no_region',
                'diet_type': dish.diet_type or 'none',
                'spicy_level': dish.spicy_level or 'none',
                'serving_temp': dish.serving_temp or 'hot',
                'cooking_method': dish.cooking_method or 'unknown',
                'calories': dish.calories,
                'protein_g': dish.protein_g,
                'allergens': list(dish.allergens.values_list('name', flat=True))
            }
            dishes_data.append(dish_data)
        
        # Export ratings
        ratings_data = []
        for rating in ratings:
            rating_data = {
                'guest_id': rating.guest_id,
                'dish_id': rating.menu_item_id,
                'rating': rating.rating,
                'created_at': rating.created_at.isoformat()
            }
            ratings_data.append(rating_data)
        
        # Combine all data
        export_data = {
            'guests': guests_data,
            'dishes': dishes_data,
            'ratings': ratings_data,
            'metadata': {
                'total_guests': len(guests_data),
                'total_dishes': len(dishes_data),
                'total_ratings': len(ratings_data),
                'export_date': ratings.first().created_at.isoformat() if ratings.exists() else ''
            }
        }
        
        # Save to file
        output_path = os.path.join(settings.BASE_DIR, f"{output_name}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def _export_csv(self, guests, dishes, ratings, output_name):
        import csv
        
        # Export guests
        guests_path = os.path.join(settings.BASE_DIR, f"{output_name}_guests.csv")
        with open(guests_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'first_name', 'last_name', 'diet_preference', 'spicy_food', 
                           'temp_preference', 'cuisine_preference', 'texture_preference', 
                           'nutrition_goal', 'preferred_course', 'allergens'])
            
            for guest in guests:
                allergens_str = ','.join(guest.allergens.values_list('name', flat=True))
                writer.writerow([
                    guest.id,
                    guest.profile.first_name if guest.profile else '',
                    guest.profile.last_name if guest.profile else '',
                    guest.diet_preference or 'none',
                    guest.spicy_food or 'none',
                    guest.temp_preference or 'hot',
                    guest.cuisine_preference or 'no_region',
                    guest.texture_preference or 'none',
                    guest.nutrition_goal or 'none',
                    guest.preferred_course or 'main',
                    allergens_str
                ])
        
        # Export dishes
        dishes_path = os.path.join(settings.BASE_DIR, f"{output_name}_dishes.csv")
        with open(dishes_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'category', 'cuisine', 'diet_type', 'spicy_level',
                           'serving_temp', 'cooking_method', 'calories', 'protein_g', 'allergens'])
            
            for dish in dishes:
                allergens_str = ','.join(dish.allergens.values_list('name', flat=True))
                writer.writerow([
                    dish.id,
                    dish.item_name,
                    dish.category,
                    dish.item_cuisine or 'no_region',
                    dish.diet_type or 'none',
                    dish.spicy_level or 'none',
                    dish.serving_temp or 'hot',
                    dish.cooking_method or 'unknown',
                    dish.calories,
                    dish.protein_g,
                    allergens_str
                ])
        
        # Export ratings
        ratings_path = os.path.join(settings.BASE_DIR, f"{output_name}_ratings.csv")
        with open(ratings_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['guest_id', 'dish_id', 'rating', 'created_at'])
            
            for rating in ratings:
                writer.writerow([
                    rating.guest_id,
                    rating.menu_item_id,
                    rating.rating,
                    rating.created_at.isoformat()
                ]) 