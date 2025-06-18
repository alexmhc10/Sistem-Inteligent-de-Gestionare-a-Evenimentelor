from django.core.management.base import BaseCommand
import numpy as np
import os
from django.conf import settings
from base.models import Guests, Menu, MenuRating

class Command(BaseCommand):
    help = "Train a lightweight SVD-based recommender (binary interactions)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--components",
            type=int,
            default=20,
            help="Number of latent factors",
        )

    def handle(self, *args, **options):
        k = options["components"]
        guests = list(Guests.objects.all())
        dishes = list(Menu.objects.all())
        ratings = MenuRating.objects.filter(rating__gte=4)  # positive interactions only

        if not ratings.exists():
            self.stdout.write(self.style.WARNING("No positive MenuRating records – cannot train."))
            return

        user_id_to_idx = {g.id: idx for idx, g in enumerate(guests)}
        item_id_to_idx = {d.id: idx for idx, d in enumerate(dishes)}

        R = np.zeros((len(guests), len(dishes)), dtype=np.float32)
        for r in ratings:
            u = user_id_to_idx.get(r.guest_id)
            i = item_id_to_idx.get(r.menu_item_id)
            if u is not None and i is not None:
                R[u, i] = 1.0  # implicit positive signal

        # center by user mean (optional) – but for implicit binary skip.
        # Truncated SVD via numpy.linalg.svd
        self.stdout.write("Performing SVD…")
        U, s, Vt = np.linalg.svd(R, full_matrices=False)
        k = min(k, s.shape[0])
        U_k = U[:, :k]
        S_k = np.diag(s[:k])
        V_k = Vt[:k, :].T  # items x k

        user_factors = np.dot(U_k, np.sqrt(S_k))
        item_factors = np.dot(V_k, np.sqrt(S_k))

        model_dir = os.path.join(settings.BASE_DIR, "base", "ml_models")
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "simple_recommender.npz")
        np.savez(
            model_path,
            user_factors=user_factors,
            item_factors=item_factors,
            user_ids=np.array([g.id for g in guests]),
            item_ids=np.array([d.id for d in dishes]),
        )

        self.stdout.write(self.style.SUCCESS(
            f"Lightweight model saved to {model_path} (components={k}).")) 