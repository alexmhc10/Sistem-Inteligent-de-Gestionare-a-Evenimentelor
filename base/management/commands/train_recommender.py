# base/management/commands/train_recommender.py
from django.core.management.base import BaseCommand
from lightfm import LightFM
from lightfm.data import Dataset
import joblib
from base.models import Guests, Menu, MenuRating
import os
from django.conf import settings

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

        ds = Dataset()
        ds.fit(
            users=guests.values_list('id', flat=True),
            items=dishes.values_list('id', flat=True),
            user_features=set(sum([
                [g.diet_preference, g.cuisine_preference,
                 g.texture_preference, g.nutrition_goal,
                 g.spicy_food, g.temp_preference] for g in guests
            ], [])),
            item_features=set(sum([
                [d.category, d.item_cuisine, d.diet_type,
                 d.cooking_method, d.serving_temp,
                 d.spicy_level] for d in dishes
            ], []))
        )

        # interactions matrix (sparse)
        (interactions, weights) = ds.build_interactions(
            (
                (r.guest_id, r.menu_item_id, r.rating)
                for r in ratings
            )
        )

        if verbosity >= 2:
            self.stdout.write(f"Interactions: {interactions.getnnz()} non-zero entries")

        user_features = ds.build_user_features([
            (g.id, [g.diet_preference, g.cuisine_preference,
                    g.texture_preference, g.nutrition_goal,
                    g.spicy_food, g.temp_preference])
            for g in guests
        ])

        item_features = ds.build_item_features([
            (d.id, [d.category, d.item_cuisine, d.diet_type,
                    d.cooking_method, d.serving_temp,
                    d.spicy_level])
            for d in dishes
        ])

        show_progress = options.get("progress", False)

        model = LightFM(loss="warp", no_components=32)
        model.fit(
            interactions,
            sample_weight=weights,
            user_features=user_features,
            item_features=item_features,
            epochs=15,
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