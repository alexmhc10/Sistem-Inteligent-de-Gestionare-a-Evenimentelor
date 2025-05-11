from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from base.models import Event, Profile
from datetime import timedelta

class Command(BaseCommand):
    help = 'Send daily notifications to users with incomplete profiles'

    def handle(self, *args, **options):

        users_with_incomplete_profile = User.objects.filter(
            profile__is_complete=False
        )

        for event in Event.objects.filter(
            date__gte=timezone.now(),
            date__lte=timezone.now() + timedelta(days=7)
        ):
            incomplete_invitees = event.invitees.filter(
                profile__is_complete=False
            )

            for user in incomplete_invitees:
                self.send_reminder_email(user, event)

    def send_reminder_email(self, user, event):
        subject = f"Completează-ți profilul pentru {event.name}"
        message = render_to_string('emails/profile_reminder.txt', {
            'user': user,
            'event': event,
        })
        send_mail(
            subject,
            message,
            'noreply@example.com',
            [user.email],
            fail_silently=False,
        )