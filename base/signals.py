from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.utils.timezone import now
from django.db import transaction
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from decimal import Decimal
from .models import *

def import_tasks():
    from base.tasks import run_optimization_task, send_email_task
    return run_optimization_task, send_email_task

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
        run_optimization_task, _ = import_tasks()
        run_optimization_task.delay()

@receiver(post_save, sender=Location)
def location_changed_handler(sender, instance, created, **kwargs):
    if not created:
        run_optimization_task, _ = import_tasks()
        run_optimization_task.delay()

@receiver(post_delete, sender=Event)
def event_deleted_handler(sender, instance, **kwargs):
    run_optimization_task, _ = import_tasks()
    run_optimization_task.delay()
    
@receiver(post_delete, sender=Location)
def location_deleted_handler(sender, instance, **kwargs):
    run_optimization_task, _ = import_tasks()
    run_optimization_task.delay()

@receiver(post_save, sender=Profile)
def send_welcome_email(sender, instance, **kwargs):
    if not instance.email:
        return
    if instance.welcome_email_sent:
        return
    _, send_email_task = import_tasks()
    base_url = settings.FRONTEND_BASE_URL.rstrip('/')
    if instance.user_type == 'guest':
        home_path = reverse('guest_home')
        home_url = f"{base_url}{home_path}"
        context = {
            "guest": instance,
            "site_url": base_url,
            "guest_home_url": home_url,
        }
        subject = "Welcome to our app EventEase!"
        html_body = render_to_string("base/welcome_guests.html", context)
        text_body = render_to_string("base/welcome_guests.txt", context)
        send_email_task.delay(subject, text_body, html_body, instance.email)
        Profile.objects.filter(pk=instance.pk).update(welcome_email_sent=True)
    elif instance.user_type == 'staff':
        staff_home_path = reverse('staff_home') if 'staff_home' in [url.name for url in __import__('django.urls').get_resolver().url_patterns] else '/'
        staff_home_url = f"{base_url}{staff_home_path}"
        context = {
            "staff": instance,
            "site_url": base_url,
            "staff_home_url": staff_home_url,
        }
        subject = "Now you can accest you'r staff account! Welcome to EventEase!"
        html_body = render_to_string("base/welcome_staff.html", context)
        text_body = render_to_string("base/welcome_staff.txt", context)
        send_email_task.delay(subject, text_body, html_body, instance.email)
        Profile.objects.filter(pk=instance.pk).update(welcome_email_sent=True)

@receiver(post_save, sender=RSVP)
def send_invitation_email(sender, instance, created, **kwargs):
    if created:
        _, send_email_task = import_tasks()
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

        send_email_task.delay(subject, text_body, html_body, guest.email)

@receiver(m2m_changed, sender=Event.guests.through)
def sync_rsvp_with_event_guests(sender, instance, action, pk_set, **kwargs):
    if action != "post_add":
        return

    new_rsvps = []
    for guest_pk in pk_set:
        guest = Guests.objects.select_related("profile__user").filter(pk=guest_pk).first()
        if not guest or not guest.profile.user:
            continue
        if not RSVP.objects.filter(event=instance, guest=guest.profile.user).exists():
            new_rsvps.append(RSVP(event=instance, guest=guest.profile.user))

    if not new_rsvps:
        return

    def _bulk_create_rsvps():
        RSVP.objects.bulk_create(new_rsvps)

    transaction.on_commit(_bulk_create_rsvps)