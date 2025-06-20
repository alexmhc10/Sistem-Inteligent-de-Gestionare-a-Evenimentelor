import django
import os
import sys

# --- Setup Django environment dacă rulezi direct din fisier ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistem_inteligent_de_gestionare_a_evenimentelor.settings")
django.setup()
# ------------------------------------------------------------

from django.contrib.auth.models import User
from base.models import Location, Profile

def create_missing_user_accounts():
    locations = Location.objects.filter(user_account__isnull=True)
    print(f"Found {locations.count()} locations without user_account.")

    for location in locations:
        base_username = f"{location.name.replace(' ', '_').lower()}_staff"
        username = base_username
        counter = 1

        # Găsește username unic
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        email = f"{username}@eventplanner.com"
        password = location.number if location.number else "defaultPass123"  # fallback parolă

        # Creează user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=location.name,
            is_active=True
        )

        # Creează profil staff
        Profile.objects.create(
            user=user,
            username=username,
            password=password,
            email=email,
            user_type='staff'
        )

        # Leagă user de location
        location.user_account = user
        location.save()

        print(f"Created user_account {username} for location '{location.name}'.")

if __name__ == "__main__":
    create_missing_user_accounts()
