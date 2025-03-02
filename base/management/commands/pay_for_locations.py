from django.core.management.base import BaseCommand
from django.utils.timezone import now
from base.models import Budget, Location

class Command(BaseCommand):
    help = "Paying for locations"

    def handle(self, *args, **kwargs):
        current_month = now().date().replace(day=1)
        budget = Budget.objects.first()
        
        if budget and (budget.last_location_update is None or budget.last_location_update < current_month):
            budget.update_locations(Location.objects.all())
            self.stdout.write(self.style.SUCCESS("Success"))
        else:
            self.stdout.write(self.style.WARNING("Not needed"))
