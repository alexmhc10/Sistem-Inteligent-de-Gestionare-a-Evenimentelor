from django.core.management.base import BaseCommand
from base.models import Event

class Command(BaseCommand):
    help = 'Populează automat first_name și last_name pentru invitații evenimentului real.'

    def handle(self, *args, **kwargs):
        event = Event.objects.filter(event_name__icontains='invitati reali').first()
        if not event:
            self.stdout.write(self.style.ERROR('Evenimentul nu a fost găsit!'))
            return
        guests = event.guests.all()
        count = 0
        for idx, guest in enumerate(guests, 1):
            profile = guest.profile
            profile.first_name = 'Invitat'
            profile.last_name = str(idx)
            profile.save()
            count += 1
        self.stdout.write(self.style.SUCCESS(f'A fost actualizat numele pentru {count} invitați.')) 