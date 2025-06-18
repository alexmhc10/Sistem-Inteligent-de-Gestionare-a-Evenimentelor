from django.core.management.base import BaseCommand
from base.models import Guests, Menu, MenuRating
import joblib
import os
from django.conf import settings
import numpy as np

class Command(BaseCommand):
    help = "Testează modelul LightFM antrenat"

    def handle(self, *args, **options):
        model_path = os.path.join(settings.BASE_DIR, "base", "ml_models", "recommender_model.pkl")
        
        if not os.path.exists(model_path):
            self.stdout.write(self.style.ERROR("Modelul nu a fost găsit. Rulează mai întâi 'train_recommender'."))
            return

        try:
            # Încarcă modelul
            model, dataset, user_features, item_features = joblib.load(model_path)
            self.stdout.write("✓ Model încărcat cu succes.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Eroare la încărcarea modelului: {str(e)}"))
            return

        # Testează cu câțiva invitați
        guests = Guests.objects.all()[:5]  # Testează cu primii 5 invitați
        
        for guest in guests:
            self.stdout.write(f"\n--- Test pentru {guest.profile.first_name} {guest.profile.last_name} ---")
            
            try:
                # Găsește indexul invitatului în dataset
                guest_id = guest.id
                guest_idx = None
                
                # Caută în user_features pentru a găsi indexul
                for i, (uid, features) in enumerate(user_features):
                    if uid == guest_id:
                        guest_idx = i
                        break
                
                if guest_idx is None:
                    self.stdout.write(f"  Invitatul nu a fost găsit în model.")
                    continue

                # Generează predicții pentru toate preparatele
                scores = model.predict(guest_idx, np.arange(item_features.shape[0]))
                
                # Găsește top 5 preparate
                top_indices = np.argsort(scores)[-5:][::-1]
                
                self.stdout.write(f"  Top 5 recomandări:")
                for i, idx in enumerate(top_indices, 1):
                    # Găsește preparatul corespunzător
                    dish_id = None
                    for j, (did, features) in enumerate(item_features):
                        if j == idx:
                            dish_id = did
                            break
                    
                    if dish_id:
                        try:
                            dish = Menu.objects.get(id=dish_id)
                            score = scores[idx]
                            self.stdout.write(f"    {i}. {dish.item_name} (scor: {score:.3f})")
                        except Menu.DoesNotExist:
                            self.stdout.write(f"    {i}. Preparat ID {dish_id} (scor: {scores[idx]:.3f})")
                
            except Exception as e:
                self.stdout.write(f"  Eroare la predicție: {str(e)}")

        self.stdout.write(self.style.SUCCESS("\n✓ Testul s-a terminat cu succes.")) 