# base/management/commands/train_recommender.py
from django.core.management.base import BaseCommand
from lightfm import LightFM
from lightfm.data import Dataset
import joblib
from base.models import Guests, Menu, MenuRating
import os
from django.conf import settings
import time
import numpy as np
import scipy.sparse as sp

class Command(BaseCommand):
    help = "Re-train LightFM model"

    def add_arguments(self, parser):
        parser.add_argument(
            "--progress",
            action="store_true",
            help="Show per-epoch training progress (LightFM verbose mode)",
        )

    def handle(self, *args, **options):
        ratings = MenuRating.objects.all()

        verbosity = int(options.get("verbosity", 1))

        # Verbose diagnostic information
        if verbosity >= 2:
            self.stdout.write(f"Total ratings: {ratings.count()}")

        if ratings.count() == 0:
            self.stdout.write(self.style.WARNING(
                "Nu există niciun MenuRating în baza de date – modelul nu poate fi antrenat."))
            return

        # Găsește invitații care au cel puțin un review
        active_guest_ids = set(ratings.values_list('guest_id', flat=True).distinct())
        guests = Guests.objects.filter(id__in=active_guest_ids)

        # Găsește preparatele care au cel puțin un review
        active_dish_ids = set(ratings.values_list('menu_item_id', flat=True).distinct())
        dishes = Menu.objects.filter(id__in=active_dish_ids)

        if verbosity >= 2:
            self.stdout.write(f"Active Guests (cu review-uri): {guests.count()}")
            self.stdout.write(f"Active Dishes (cu review-uri): {dishes.count()}")

        # Verifică dacă avem suficiente date
        if guests.count() < 2:
            self.stdout.write(self.style.WARNING(
                "Nu sunt suficienți invitați cu review-uri pentru antrenare (minimum 2 necesari)."))
            return

        if dishes.count() < 2:
            self.stdout.write(self.style.WARNING(
                "Nu sunt suficiente preparate cu review-uri pentru antrenare (minimum 2 necesare)."))
            return

        # -------- helpers --------
        def user_tokens(g):
            tokens = []
            if g.diet_preference != 'none':
                tokens.append(f"diet_{g.diet_preference}")
            else:
                tokens.append("diet_any")
            if g.spicy_food:
                tokens.append(f"spicy_{g.spicy_food}")
            if g.temp_preference:
                tokens.append(f"temp_{g.temp_preference}")
            if g.cuisine_preference and g.cuisine_preference != 'no_region':
                tokens.append(f"cuisine_{g.cuisine_preference}")
            else:
                tokens.append("cuisine_any")
            if g.texture_preference and g.texture_preference != 'none':
                tokens.append(f"texture_{g.texture_preference}")
            else:
                tokens.append("texture_any")
            if g.nutrition_goal and g.nutrition_goal != 'none':
                tokens.append(f"goal_{g.nutrition_goal}")
            else:
                tokens.append("goal_any")
            if g.preferred_course:
                tokens.append(f"course_{g.preferred_course}")
            else:
                tokens.append("course_any")
            return tokens

        def item_tokens(d):
            tokens = []
            if d.diet_type and d.diet_type != 'none':
                tokens.append(f"diet_{d.diet_type}")    
            else:
                tokens.append("diet_any")
            if d.spicy_level:
                tokens.append(f"spicy_{d.spicy_level}")
            if d.serving_temp:
                tokens.append(f"temp_{d.serving_temp}")
            tokens.append(f"course_{d.category}")
            if d.item_cuisine and d.item_cuisine != 'no_region':
                tokens.append(f"cuisine_{d.item_cuisine}")
            else:
                tokens.append("cuisine_any")
            if d.cooking_method:
                tokens.append(f"cook_{d.cooking_method}")
            else:
                tokens.append("cook_unknown")  
            if d.protein_g and d.protein_g >= 20:
                tokens.append("macro_high_protein")
            if d.calories and d.calories <= 400:
                tokens.append("macro_low_kcal")
            return tokens

        # -------------------------

        user_feature_tokens = set().union(*[user_tokens(g) for g in guests])
        item_feature_tokens = set().union(*[item_tokens(d) for d in dishes])

        ds = Dataset()
        start_time = time.perf_counter()
        ds.fit(
            users=guests.values_list('id', flat=True),
            items=dishes.values_list('id', flat=True),
            user_features=user_feature_tokens,
            item_features=item_feature_tokens,
        )
        end_time = time.perf_counter() - start_time
        self.stdout.write(f"Dataset fit time: {end_time:.2f} seconds")

        # Filtrează ratingurile pentru a include doar invitații și preparatele active
        filtered_ratings = ratings.filter(
            guest_id__in=active_guest_ids,
            menu_item_id__in=active_dish_ids
        )

        interactions, _ = ds.build_interactions(
            (
                ((r.guest_id, r.menu_item_id) for r in filtered_ratings)
            )
        )
        
        print("Interactions nnz:", interactions.nnz)
        print("Positives per user min:", interactions.sum(axis=1).min())
        print("Positives per item min:", interactions.sum(axis=0).min())
        
        # Verifică dacă avem suficiente interacțiuni
        if interactions.nnz < 10:
            self.stdout.write(self.style.WARNING(
                "Nu sunt suficiente interacțiuni pentru antrenare (minimum 10 necesare)."))
            return

        # Verifică dacă toți utilizatorii și elementele au cel puțin o interacțiune
        user_interactions = interactions.sum(axis=1).A1
        item_interactions = interactions.sum(axis=0).A1
        
        # Acum ar trebui să avem toți utilizatorii cu cel puțin o interacțiune
        if user_interactions.min() == 0:
            self.stdout.write(self.style.WARNING(
                f"Există utilizatori fără interacțiuni. Utilizatori cu interacțiuni: {np.sum(user_interactions > 0)}/{len(user_interactions)}"))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"✓ Toți utilizatorii au cel puțin o interacțiune!"))
        
        if item_interactions.min() == 0:
            self.stdout.write(self.style.WARNING(
                f"Există elemente fără interacțiuni. Elemente cu interacțiuni: {np.sum(item_interactions > 0)}/{len(item_interactions)}"))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"✓ Toate elementele au cel puțin o interacțiune!"))

        if verbosity >= 2:
            self.stdout.write(f"Interactions: {interactions.getnnz()} non-zero entries")

        user_features = ds.build_user_features([
            (g.id, user_tokens(g))
            for g in guests
        ])

        item_features = ds.build_item_features([
            (d.id, item_tokens(d))
            for d in dishes
        ])

        # Verifică dimensiunile features
        self.stdout.write(f"User features shape: {user_features.shape}")
        self.stdout.write(f"Item features shape: {item_features.shape}")
        self.stdout.write(f"Interactions shape: {interactions.shape}")

        show_progress = options.get("progress", False)

        # Încearcă cu parametri mai conservatori
        model = LightFM(
            loss="warp", 
            no_components=8,  # Redus de la 16 la 8
            random_state=42,
            learning_rate=0.05,  # Adăugat learning rate explicit
            learning_schedule='adagrad'  # Adăugat learning schedule
        )
        
        try:
            self.stdout.write("Începe antrenarea modelului...")
            
            # Încearcă mai întâi fără features pentru a testa
            self.stdout.write("Testare antrenare fără features...")
            model_simple = LightFM(loss="warp", no_components=8, random_state=42)
            model_simple.fit(
                interactions,
                epochs=5,
                num_threads=1,  # Forțează single thread
                verbose=show_progress,
            )
            self.stdout.write(self.style.SUCCESS("✓ Antrenarea simplă a funcționat!"))
            
            # Acum încearcă cu features
            self.stdout.write("Începe antrenarea cu features...")
            model.fit(
                interactions,
                user_features=user_features,
                item_features=item_features,
                epochs=5,  # Redus de la 10 la 5
                num_threads=1,  # Forțează single thread
                verbose=show_progress,
            )
            self.stdout.write(self.style.SUCCESS("✓ Antrenarea cu features a funcționat!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Eroare la antrenare: {str(e)}"))
            self.stdout.write("Încearcă să rulezi cu --progress pentru mai multe detalii")
            return

        model_dir = os.path.join(settings.BASE_DIR, "base", "ml_models")
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "recommender_model.pkl")

        joblib.dump((model, ds, user_features, item_features), model_path)

        if verbosity >= 2:
            size_mb = os.path.getsize(model_path) / 2 ** 20
            self.stdout.write(f"Artefact salvat: {model_path} ({size_mb:.1f} MB)")

        self.stdout.write(self.style.SUCCESS(
            f"Model trained & saved to {model_path}."))