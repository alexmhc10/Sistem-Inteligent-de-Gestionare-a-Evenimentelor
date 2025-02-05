from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Event
from .models import Profile, Guests

@receiver(pre_save, sender=Event)
def update_completed_status(sender, instance, **kwargs):
    if instance.event_date <= now().date():
        instance.completed = True


@receiver(post_save, sender=Profile)
def create_guest_for_profile(sender, instance, created, **kwargs):
    if created:
        Guests.objects.create(
            profile=instance,
            preferences='',  # Inițializează câmpurile default, dacă este necesar
            additional_info=''  # Exemplu de câmp specific din tabela Guests
        )