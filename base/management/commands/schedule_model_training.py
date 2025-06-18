from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta, datetime
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Antrenează modelul periodic și verifică dacă trebuie reantrenat"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Forțează antrenarea chiar dacă nu este necesară",
        )
        parser.add_argument(
            "--check-only",
            action="store_true",
            help="Doar verifică dacă antrenarea este necesară, fără a antrena",
        )

    def handle(self, *args, **options):
        force = options['force']
        check_only = options['check_only']
        
        self.stdout.write("=== VERIFICARE ANTENARE PERIODICĂ ===\n")
        
        model_path = os.path.join(settings.BASE_DIR, 'lightfm_model.pkl')
        model_exists = os.path.exists(model_path)
        
        if not model_exists:
            self.stdout.write("❌ Modelul nu există. Antrenarea este necesară.")
            if not check_only:
                self._train_model()
            return
        
        model_age_days = self._get_model_age_days(model_path)
        max_age_days = 7 
        
        self.stdout.write(f"📅 Vârsta modelului: {model_age_days} zile")
        self.stdout.write(f"⏰ Limită pentru reantrenare: {max_age_days} zile")
        
        new_ratings_count = self._get_new_ratings_count_days(model_age_days)
        self.stdout.write(f"📊 Ratinguri noi în ultimele {model_age_days} zile: {new_ratings_count}")
        
        should_retrain = (
            force or 
            model_age_days >= max_age_days or 
            new_ratings_count >= 50
        )
        
        if should_retrain:
            self.stdout.write("🔄 Antrenarea este necesară!")
            if not check_only:
                self._train_model()
        else:
            self.stdout.write("✅ Modelul este încă valid. Nu este necesară antrenarea.")
    
    def _get_model_age_days(self, model_path):
        import os
        from datetime import datetime
        
        stat = os.stat(model_path)
        model_time = datetime.fromtimestamp(stat.st_mtime)
        current_time = datetime.now()
        
        time_diff = current_time - model_time
        return time_diff.days
    
    def _get_new_ratings_count_days(self, days):
        from base.models import MenuRating
        
        cutoff_date = timezone.now() - timedelta(days=days)
        return MenuRating.objects.filter(
            created_at__gte=cutoff_date
        ).count()
    
    def _train_model(self):
        self.stdout.write("🚀 Începe antrenarea modelului...")
        
        try:
            self.stdout.write("📈 Îmbunătățesc preferințele...")
            call_command('improve_preferences', verbosity=0)
            
            self.stdout.write("📤 Export datele pentru Colab...")
            call_command('export_colab_data_improved', verbosity=0)
            
            self._backup_old_model()
            
            self.stdout.write("✅ Antrenarea a fost inițiată!")
            self.stdout.write("📝 Următorii pași:")
            self.stdout.write("   1. Upload colab_data_IMPROVED.json în Google Colab")
            self.stdout.write("   2. Rulează codul de antrenare")
            self.stdout.write("   3. Descarcă lightfm_model.pkl")
            self.stdout.write("   4. Pune-l în directorul rădăcină al proiectului")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Eroare la antrenare: {e}"))
    
    def _backup_old_model(self):
        import shutil
        
        model_path = os.path.join(settings.BASE_DIR, 'lightfm_model.pkl')
        backup_path = os.path.join(settings.BASE_DIR, 'lightfm_model_backup.pkl')
        
        if os.path.exists(model_path):
            shutil.copy2(model_path, backup_path)
            self.stdout.write(f"💾 Backup creat: {backup_path}")
