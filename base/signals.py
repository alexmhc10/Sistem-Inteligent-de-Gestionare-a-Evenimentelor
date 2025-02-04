from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import *
from django.db.models.signals import post_save
from decimal import Decimal

@receiver(pre_save, sender=Event)
def update_completed_status(sender, instance, **kwargs):
    if instance.event_date <= now().date():
        instance.completed = True
        event_cost = instance.cost
        budget = Budget.objects.first()
        if budget:
            budget.update_budget_for_event(event_cost * Decimal("0.60"))

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

        # 1️⃣ Găsim organizatorul evenimentului și îi actualizăm bonusul
        organizer = instance.organized_by  # Asigură-te că Event are un câmp `organizer`
        if organizer:
            salary, created = Salary.objects.get_or_create(user=organizer)
            salary.update_bonus_for_event(event_cost)
