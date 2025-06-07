from django.core.management.base import BaseCommand
from base.models import Event, Location, Guests, Profile, TableGroup, Table, TableArrangement, User
from base.table_arrangement_algorithm import TableArrangementAlgorithm
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Repară complet datele pentru evenimentul real de la Perla Coșaului.'

    def handle(self, *args, **kwargs):
        # 1. Șterge duplicatele de locație
        Location.objects.filter(name__icontains="Perla Coșaului").exclude(id=1).delete()
        # 2. Creează/actualizează locația cu mese
        location, _ = Location.objects.get_or_create(id=1, defaults={
            'name': 'Perla Coșaului',
            'description': 'Locație test',
            'seats_numbers': 100,
            'cost': 1000,
        })
        # Șterge mesele vechi
        Table.objects.filter(location=location).delete()
        # Creează 10 mese
        for i in range(1, 11):
            Table.objects.create(location=location, table_number=i, capacity=10, shape='round', position_x=10*i, position_y=10*i, is_reserved=False)
        # 3. Asociază evenimentul la această locație
        event, _ = Event.objects.get_or_create(event_name__icontains="invitati reali", defaults={'location': location})
        event.location = location
        event.save()
        # 4. Adaugă invitați corect
        event.guests.clear()
        for i in range(1, 31):
            username = f"invitat_real_{i}"
            user, _ = User.objects.get_or_create(username=username, defaults={
                'email': f"{username}@test.com"
            })
            profile, _ = Profile.objects.get_or_create(user=user, defaults={
                'username': username,
                'email': user.email,
                'password': 'test1234',
            })
            guest, _ = Guests.objects.get_or_create(profile=profile)
            event.guests.add(guest)
        # 5. Adaugă grupuri
        TableGroup.objects.filter(event=event).delete()
        guests = list(event.guests.all())
        random.shuffle(guests)
        group_size = 6
        for idx in range(0, len(guests), group_size):
            group = TableGroup.objects.create(event=event, name=f'Grup {idx//group_size+1}', priority=idx//group_size+1)
            group.guests.set(guests[idx:idx+group_size])
        # 6. Status final
        self.stdout.write(self.style.SUCCESS(f'Locație: {location.name} (mese: {location.tables.count()})'))
        self.stdout.write(self.style.SUCCESS(f'Eveniment: {event.event_name} (invitați: {event.guests.count()})'))
        self.stdout.write(self.style.SUCCESS(f'Grupuri: {TableGroup.objects.filter(event=event).count()}')) 