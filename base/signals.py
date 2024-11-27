from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Event

@receiver(pre_save, sender=Event)
def update_completed_status(sender, instance, **kwargs):
    if instance.event_date <= now().date():
        instance.completed = True
