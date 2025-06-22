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
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import Site
from base.tasks import send_email_task
from django.conf import settings
from django.urls import reverse

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
    if not created:
        print(f"DEBUG: Semnal post_save (update) pentru Eveniment '{instance.event_name}' (ID: {instance.id}) detectat. Se declanșează sarcina de optimizare.")
        run_optimization_task.delay()

@receiver(post_save, sender=Location)
def location_changed_handler(sender, instance, created, **kwargs):
    if not created:
        print(f"DEBUG: Semnal post_save (update) pentru Locație '{instance.name}' (ID: {instance.id}) detectat. Se declanșează sarcina de optimizare.")
        run_optimization_task.delay()

@receiver(post_delete, sender=Event)
def event_deleted_handler(sender, instance, **kwargs):
    print(f"DEBUG: Semnal post_delete pentru Eveniment '{instance.event_name}' detectat. Se declanșează sarcina de optimizare.")
    run_optimization_task.delay()

@receiver(post_save, sender=Profile)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        current_site = Site.objects.get_current()
        context = {
            "guest": instance,
            "site_url": f"https://{current_site.domain}",
        }
        subject = "Welcome to our app Eventsmart!"
        html_body = render_to_string("base/welcome_guests.html", context)
        text_body = render_to_string("base/welcome_guests.txt", context)
        msg = EmailMultiAlternatives(
            subject, text_body, None, [instance.email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
    
        send_email_task.delay(subject, text_body, html_body, instance.email)


@receiver(post_save, sender=RSVP)
def send_invitation_email(sender, instance, created, **kwargs):
    if created:
        guest = instance.guest
        event = instance.event
        base_url = settings.FRONTEND_BASE_URL.rstrip('/')
        context = {
            "guest": guest,
            "event": event,
            "site_url": base_url,
            "event_url": f"{base_url}{reverse('guest_event_view', kwargs={'pk': event.id})}",
        }

        subject = f"Invitaţie la {event.name}"
        html_body = render_to_string("base/invite_email.html", context)
        text_body = render_to_string("base/invite_form.txt", context)

        msg = EmailMultiAlternatives(subject, text_body, None, [guest.email])
        msg.attach_alternative(html_body, "text/html")
        msg.send()
    
        send_email_task.delay(subject, text_body, html_body, guest.email)