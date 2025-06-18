# base/management/commands/train_recommender.py
from django.core.management.base import BaseCommand
from lightfm import LightFM
from lightfm.data import Dataset
import joblib
from base.models import Guests, Menu, MenuRating
import os
from django.conf import settings
import time

class Command(BaseCommand):
    help = "Re-train LightFM model"

    def add_arguments(self, parser):
        parser.add_argument(
            "--progress",
            action="store_true",
            help="Show per-epoch training progress (LightFM verbose mode)",
        )

    def handle(self, *args, **options):
        guests = Guests.objects.all()
        dishes = Menu.objects.all()
        ratings = MenuRating.objects.all()

        verbosity = int(options.get("verbosity", 1))

        # Verbose diagnostic information
        if verbosity >= 2:
            self.stdout.write(f"Guests:   {guests.count()}")
            self.stdout.write(f"Dishes:   {dishes.count()}")
            self.stdout.write(f"Ratings:  {ratings.count()}")

        if ratings.count() == 0:
            self.stdout.write(self.style.WARNING(
                "Nu există niciun MenuRating în baza de date – modelul nu poate fi antrenat."))
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

        interactions, _ = ds.build_interactions(
            (
                ((r.guest_id, r.menu_item_id) for r in ratings)
            )
        )
        print("Interactions nnz:", interactions.nnz)
        print("Positives per user min:", interactions.sum(axis=1).min())
        print("Positives per item min:", interactions.sum(axis=0).min())
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

        show_progress = options.get("progress", False)

        model = LightFM(loss="warp", no_components=32, random_state=42)
        model.fit(
            interactions,
            user_features=user_features,
            item_features=item_features,
            epochs=30,
            num_threads=4,
            verbose=show_progress,
        )
        model_dir = os.path.join(settings.BASE_DIR, "base", "ml_models")
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "recommender_model.pkl")

        joblib.dump((model, ds, user_features, item_features), model_path)

        if verbosity >= 2:
            size_mb = os.path.getsize(model_path) / 2 ** 20
            self.stdout.write(f"Artefact salvat: {model_path} ({size_mb:.1f} MB)")

        self.stdout.write(self.style.SUCCESS(
            f"Model trained & saved to {model_path}."))