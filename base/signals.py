from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Event
from .models import Profile, Guests
from .models import *
from django.db.models.signals import post_save
from decimal import Decimal
from base.tasks import run_optimization_task

@receiver(pre_save, sender=Event)
def update_completed_status(sender, instance, **kwargs):
    if instance.event_date <= now().date():
        instance.completed = True
        Notification.objects.create(
                    user=instance.organized_by,
                    action_type='completed_event',
                    target_object_id=instance.id,
                    target_object_name=instance.event_name,
                    target_model='Event'
                )
        event_cost = instance.cost
        budget = Budget.objects.first()
        if budget:
            budget.update_budget_for_event(event_cost * Decimal("0.60"))
    else:
        instance.completed = False

@receiver(post_save, sender=Location)
def update_location_cost(sender, instance, created, **kwargs):
    if created:
        location_cost = instance.cost
        budget = Budget.objects.first()
        if budget:
            budget.add_new_location(location_cost)

@receiver(pre_save, sender=Event)
def update_completed_event(sender, instance, **kwargs):
    if instance.event_date <= now().date():
        instance.completed = True
        event_cost = instance.cost
        organizer = instance.organized_by  
        if organizer:
            salary, created = Salary.objects.get_or_create(user=organizer)
            salary.update_bonus_for_event(event_cost)

@receiver(post_save, sender=Event)
def event_changed_handler(sender, instance, created, **kwargs):

    print(f"DEBUG: Semnal post_save pentru Eveniment '{instance.event_name}' (ID: {instance.id}) detectat. Se declanșează sarcina de optimizare.")
    run_optimization_task.delay() 

@receiver(post_save, sender=Location)
def location_changed_handler(sender, instance, created, **kwargs):
    """
    Declanșează sarcina de optimizare când un obiect Location este salvat (creat sau actualizat).
    """
    print(f"DEBUG: Semnal post_save pentru Locație '{instance.name}' (ID: {instance.id}) detectat. Se declanșează sarcina de optimizare.")
    run_optimization_task.delay() 

@receiver(post_delete, sender=Event)
def event_deleted_handler(sender, instance, **kwargs):
    print(f"DEBUG: Semnal post_delete pentru Eveniment '{instance.event_name}' detectat. Se declanșează sarcina de optimizare.")
    run_optimization_task.delay()