from django.core.management.base import BaseCommand
from base.models import Event, Location, Guests, Profile, TableGroup, Table, TableArrangement, User
from base.table_arrangement_algorithm import TableArrangementAlgorithm
from django.utils import timezone
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Creează o situație realistă de nuntă pentru a demonstra algoritmul de aranjare la mese'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🎉 Creez o situație realistă de nuntă...'))
        
        # 1. Creează/actualizează locația
        location, created = Location.objects.get_or_create(
            name='Perla Coșaului',
            defaults={
                'description': 'Sală de evenimente premium pentru nunți și evenimente speciale',
                'seats_numbers': 120,
                'cost': 2500,
                'location': 'Strada Principală nr. 15, București'
            }
        )
        
        # 2. Șterge și recreează mesele cu poziții realiste
        Table.objects.filter(location=location).delete()
        
        # Masa VIP (miri și părinți)
        Table.objects.create(
            location=location, 
            table_number=1, 
            capacity=12, 
            shape='round', 
            position_x=50, 
            position_y=20, 
            is_reserved=True,
            notes='Masa principală - miri și părinți'
        )
        
        # Mese pentru invitați - aranjament elegant
        table_configs = [
            # Rândul 1 - aproape de masa principală
            {'number': 2, 'capacity': 10, 'x': 20, 'y': 35, 'notes': 'Familia miresei'},
            {'number': 3, 'capacity': 10, 'x': 80, 'y': 35, 'notes': 'Familia mirelui'},
            
            # Rândul 2 - prieteni apropiați
            {'number': 4, 'capacity': 8, 'x': 15, 'y': 55, 'notes': 'Prieteni apropiați miresei'},
            {'number': 5, 'capacity': 8, 'x': 50, 'y': 60, 'notes': 'Prieteni comuni'},
            {'number': 6, 'capacity': 8, 'x': 85, 'y': 55, 'notes': 'Prieteni apropiați mirelui'},
            
            # Rândul 3 - colegi și cunoscuți
            {'number': 7, 'capacity': 8, 'x': 25, 'y': 80, 'notes': 'Colegi miresei'},
            {'number': 8, 'capacity': 8, 'x': 75, 'y': 80, 'notes': 'Colegi mirelui'},
        ]
        
        for config in table_configs:
            Table.objects.create(
                location=location,
                table_number=config['number'],
                capacity=config['capacity'],
                shape='round',
                position_x=config['x'],
                position_y=config['y'],
                is_reserved=False,
                notes=config['notes']
            )
        
        # 3. Creează/actualizează evenimentul
        event, created = Event.objects.get_or_create(
            event_name='Event cu invitati reali',
            defaults={
                'location': location,
                'event_date': datetime.now().date() + timedelta(days=30),
                'event_time': datetime.strptime('18:00', '%H:%M').time(),
                'event_description': 'Nuntă elegantă cu 80 de invitați - demonstrație algoritm aranjare mese',
                'cost': 15000,
                'organized_by': User.objects.first()
            }
        )
        event.location = location
        event.save()
        
        # 4. Șterge invitații existenți și creează invitați realiști
        event.guests.clear()
        
        # Lista de invitați realiști cu relații complexe
        realistic_guests = [
            # Familia miresei (12 persoane)
            {'first_name': 'Maria', 'last_name': 'Popescu', 'age': 25, 'relation': 'mireasa', 'group': 'VIP', 'cuisine': 'traditional'},
            {'first_name': 'Alexandru', 'last_name': 'Ionescu', 'age': 28, 'relation': 'mirele', 'group': 'VIP', 'cuisine': 'traditional'},
            {'first_name': 'Ion', 'last_name': 'Popescu', 'age': 55, 'relation': 'tatal_miresei', 'group': 'VIP', 'cuisine': 'traditional'},
            {'first_name': 'Elena', 'last_name': 'Popescu', 'age': 52, 'relation': 'mama_miresei', 'group': 'VIP', 'cuisine': 'traditional'},
            {'first_name': 'Gheorghe', 'last_name': 'Ionescu', 'age': 58, 'relation': 'tatal_mirelui', 'group': 'VIP', 'cuisine': 'traditional'},
            {'first_name': 'Ana', 'last_name': 'Ionescu', 'age': 54, 'relation': 'mama_mirelui', 'group': 'VIP', 'cuisine': 'traditional'},
            {'first_name': 'Cristina', 'last_name': 'Popescu', 'age': 22, 'relation': 'sora_miresei', 'group': 'VIP', 'cuisine': 'modern'},
            {'first_name': 'Mihai', 'last_name': 'Ionescu', 'age': 30, 'relation': 'fratele_mirelui', 'group': 'VIP', 'cuisine': 'traditional'},
            {'first_name': 'Ioana', 'last_name': 'Ionescu', 'age': 26, 'relation': 'cunada', 'group': 'VIP', 'cuisine': 'modern'},
            {'first_name': 'Vasile', 'last_name': 'Popescu', 'age': 78, 'relation': 'bunicul_miresei', 'group': 'VIP', 'cuisine': 'traditional'},
            {'first_name': 'Ecaterina', 'last_name': 'Popescu', 'age': 75, 'relation': 'bunica_miresei', 'group': 'VIP', 'cuisine': 'traditional'},
            {'first_name': 'Andrei', 'last_name': 'Popescu', 'age': 32, 'relation': 'unchiul_miresei', 'group': 'VIP', 'cuisine': 'traditional'},
            
            # Familia extinsă miresei (10 persoane)
            {'first_name': 'Rodica', 'last_name': 'Constantin', 'age': 48, 'relation': 'matusa_miresei', 'group': 'familia_miresei', 'cuisine': 'traditional'},
            {'first_name': 'Florin', 'last_name': 'Constantin', 'age': 50, 'relation': 'unchiul_miresei', 'group': 'familia_miresei', 'cuisine': 'traditional'},
            {'first_name': 'Diana', 'last_name': 'Constantin', 'age': 20, 'relation': 'verisoara_miresei', 'group': 'familia_miresei', 'cuisine': 'modern'},
            {'first_name': 'Radu', 'last_name': 'Constantin', 'age': 18, 'relation': 'varul_miresei', 'group': 'familia_miresei', 'cuisine': 'modern'},
            {'first_name': 'Gabriela', 'last_name': 'Marinescu', 'age': 45, 'relation': 'matusa_miresei', 'group': 'familia_miresei', 'cuisine': 'traditional'},
            {'first_name': 'Bogdan', 'last_name': 'Marinescu', 'age': 47, 'relation': 'unchiul_miresei', 'group': 'familia_miresei', 'cuisine': 'traditional'},
            {'first_name': 'Andreea', 'last_name': 'Marinescu', 'age': 19, 'relation': 'verisoara_miresei', 'group': 'familia_miresei', 'cuisine': 'modern'},
            {'first_name': 'Stefan', 'last_name': 'Marinescu', 'age': 21, 'relation': 'varul_miresei', 'group': 'familia_miresei', 'cuisine': 'modern'},
            {'first_name': 'Luminita', 'last_name': 'Georgescu', 'age': 42, 'relation': 'verisoara_mama_miresei', 'group': 'familia_miresei', 'cuisine': 'traditional'},
            {'first_name': 'Marian', 'last_name': 'Georgescu', 'age': 44, 'relation': 'varul_mama_miresei', 'group': 'familia_miresei', 'cuisine': 'traditional'},
            
            # Familia extinsă mirelui (10 persoane)
            {'first_name': 'Doina', 'last_name': 'Dumitrescu', 'age': 46, 'relation': 'matusa_mirelui', 'group': 'familia_mirelui', 'cuisine': 'traditional'},
            {'first_name': 'Costel', 'last_name': 'Dumitrescu', 'age': 49, 'relation': 'unchiul_mirelui', 'group': 'familia_mirelui', 'cuisine': 'traditional'},
            {'first_name': 'Raluca', 'last_name': 'Dumitrescu', 'age': 23, 'relation': 'verisoara_mirelui', 'group': 'familia_mirelui', 'cuisine': 'modern'},
            {'first_name': 'Catalin', 'last_name': 'Dumitrescu', 'age': 25, 'relation': 'varul_mirelui', 'group': 'familia_mirelui', 'cuisine': 'modern'},
            {'first_name': 'Silvia', 'last_name': 'Popa', 'age': 43, 'relation': 'matusa_mirelui', 'group': 'familia_mirelui', 'cuisine': 'traditional'},
            {'first_name': 'Liviu', 'last_name': 'Popa', 'age': 45, 'relation': 'unchiul_mirelui', 'group': 'familia_mirelui', 'cuisine': 'traditional'},
            {'first_name': 'Bianca', 'last_name': 'Popa', 'age': 22, 'relation': 'verisoara_mirelui', 'group': 'familia_mirelui', 'cuisine': 'modern'},
            {'first_name': 'Vlad', 'last_name': 'Popa', 'age': 24, 'relation': 'varul_mirelui', 'group': 'familia_mirelui', 'cuisine': 'modern'},
            {'first_name': 'Carmen', 'last_name': 'Stoica', 'age': 41, 'relation': 'verisoara_mama_mirelui', 'group': 'familia_mirelui', 'cuisine': 'traditional'},
            {'first_name': 'Adrian', 'last_name': 'Stoica', 'age': 43, 'relation': 'varul_mama_mirelui', 'group': 'familia_mirelui', 'cuisine': 'traditional'},
            
            # Prieteni apropiați miresei (8 persoane)
            {'first_name': 'Laura', 'last_name': 'Radu', 'age': 26, 'relation': 'cea_mai_buna_prietena', 'group': 'prieteni_miresei', 'cuisine': 'modern'},
            {'first_name': 'Marius', 'last_name': 'Radu', 'age': 29, 'relation': 'prietenul_laurei', 'group': 'prieteni_miresei', 'cuisine': 'modern'},
            {'first_name': 'Simona', 'last_name': 'Vasilescu', 'age': 25, 'relation': 'prietena_facultate', 'group': 'prieteni_miresei', 'cuisine': 'modern'},
            {'first_name': 'George', 'last_name': 'Vasilescu', 'age': 27, 'relation': 'prietenul_simonei', 'group': 'prieteni_miresei', 'cuisine': 'modern'},
            {'first_name': 'Oana', 'last_name': 'Munteanu', 'age': 24, 'relation': 'prietena_liceu', 'group': 'prieteni_miresei', 'cuisine': 'modern'},
            {'first_name': 'Razvan', 'last_name': 'Munteanu', 'age': 26, 'relation': 'prietenul_oanei', 'group': 'prieteni_miresei', 'cuisine': 'modern'},
            {'first_name': 'Alina', 'last_name': 'Cristea', 'age': 25, 'relation': 'prietena_copilarie', 'group': 'prieteni_miresei', 'cuisine': 'traditional'},
            {'first_name': 'Dan', 'last_name': 'Cristea', 'age': 28, 'relation': 'prietenul_alinei', 'group': 'prieteni_miresei', 'cuisine': 'traditional'},
            
            # Prieteni apropiați mirelui (8 persoane)
            {'first_name': 'Ciprian', 'last_name': 'Moldovan', 'age': 29, 'relation': 'cel_mai_bun_prieten', 'group': 'prieteni_mirelui', 'cuisine': 'modern'},
            {'first_name': 'Monica', 'last_name': 'Moldovan', 'age': 27, 'relation': 'prietena_ciprian', 'group': 'prieteni_mirelui', 'cuisine': 'modern'},
            {'first_name': 'Lucian', 'last_name': 'Stanescu', 'age': 28, 'relation': 'prieten_facultate', 'group': 'prieteni_mirelui', 'cuisine': 'modern'},
            {'first_name': 'Irina', 'last_name': 'Stanescu', 'age': 26, 'relation': 'prietena_lucian', 'group': 'prieteni_mirelui', 'cuisine': 'modern'},
            {'first_name': 'Sorin', 'last_name': 'Enache', 'age': 30, 'relation': 'prieten_liceu', 'group': 'prieteni_mirelui', 'cuisine': 'traditional'},
            {'first_name': 'Daniela', 'last_name': 'Enache', 'age': 28, 'relation': 'prietena_sorin', 'group': 'prieteni_mirelui', 'cuisine': 'traditional'},
            {'first_name': 'Florian', 'last_name': 'Barbu', 'age': 29, 'relation': 'prieten_copilarie', 'group': 'prieteni_mirelui', 'cuisine': 'modern'},
            {'first_name': 'Roxana', 'last_name': 'Barbu', 'age': 27, 'relation': 'prietena_florian', 'group': 'prieteni_mirelui', 'cuisine': 'modern'},
            
            # Prieteni comuni (8 persoane)
            {'first_name': 'Tudor', 'last_name': 'Nistor', 'age': 27, 'relation': 'prieten_comun', 'group': 'prieteni_comuni', 'cuisine': 'modern'},
            {'first_name': 'Anca', 'last_name': 'Nistor', 'age': 25, 'relation': 'prietena_tudor', 'group': 'prieteni_comuni', 'cuisine': 'modern'},
            {'first_name': 'Sergiu', 'last_name': 'Lazar', 'age': 26, 'relation': 'prieten_comun', 'group': 'prieteni_comuni', 'cuisine': 'modern'},
            {'first_name': 'Corina', 'last_name': 'Lazar', 'age': 24, 'relation': 'prietena_sergiu', 'group': 'prieteni_comuni', 'cuisine': 'modern'},
            {'first_name': 'Octavian', 'last_name': 'Dobre', 'age': 28, 'relation': 'prieten_comun', 'group': 'prieteni_comuni', 'cuisine': 'traditional'},
            {'first_name': 'Lavinia', 'last_name': 'Dobre', 'age': 26, 'relation': 'prietena_octavian', 'group': 'prieteni_comuni', 'cuisine': 'traditional'},
            {'first_name': 'Calin', 'last_name': 'Toma', 'age': 29, 'relation': 'prieten_comun', 'group': 'prieteni_comuni', 'cuisine': 'modern'},
            {'first_name': 'Adela', 'last_name': 'Toma', 'age': 27, 'relation': 'prietena_calin', 'group': 'prieteni_comuni', 'cuisine': 'modern'},
            
            # Colegi miresei (8 persoane)
            {'first_name': 'Claudia', 'last_name': 'Mihai', 'age': 26, 'relation': 'colega_miresei', 'group': 'colegi_miresei', 'cuisine': 'modern'},
            {'first_name': 'Petru', 'last_name': 'Mihai', 'age': 28, 'relation': 'colegul_claudiei', 'group': 'colegi_miresei', 'cuisine': 'modern'},
            {'first_name': 'Nicoleta', 'last_name': 'Sandu', 'age': 24, 'relation': 'colega_miresei', 'group': 'colegi_miresei', 'cuisine': 'modern'},
            {'first_name': 'Ionut', 'last_name': 'Sandu', 'age': 26, 'relation': 'colegul_nicoletei', 'group': 'colegi_miresei', 'cuisine': 'modern'},
            {'first_name': 'Ramona', 'last_name': 'Preda', 'age': 25, 'relation': 'colega_miresei', 'group': 'colegi_miresei', 'cuisine': 'traditional'},
            {'first_name': 'Cristian', 'last_name': 'Preda', 'age': 27, 'relation': 'colegul_ramonei', 'group': 'colegi_miresei', 'cuisine': 'traditional'},
            {'first_name': 'Valentina', 'last_name': 'Ungureanu', 'age': 23, 'relation': 'colega_miresei', 'group': 'colegi_miresei', 'cuisine': 'modern'},
            {'first_name': 'Dragos', 'last_name': 'Ungureanu', 'age': 25, 'relation': 'colegul_valentinei', 'group': 'colegi_miresei', 'cuisine': 'modern'},
            
            # Colegi mirelui (8 persoane)
            {'first_name': 'Robert', 'last_name': 'Tanase', 'age': 29, 'relation': 'colegul_mirelui', 'group': 'colegi_mirelui', 'cuisine': 'modern'},
            {'first_name': 'Andreea', 'last_name': 'Tanase', 'age': 27, 'relation': 'colega_robert', 'group': 'colegi_mirelui', 'cuisine': 'modern'},
            {'first_name': 'Eugen', 'last_name': 'Badea', 'age': 30, 'relation': 'colegul_mirelui', 'group': 'colegi_mirelui', 'cuisine': 'traditional'},
            {'first_name': 'Mihaela', 'last_name': 'Badea', 'age': 28, 'relation': 'colega_eugen', 'group': 'colegi_mirelui', 'cuisine': 'traditional'},
            {'first_name': 'Viorel', 'last_name': 'Matei', 'age': 31, 'relation': 'colegul_mirelui', 'group': 'colegi_mirelui', 'cuisine': 'traditional'},
            {'first_name': 'Camelia', 'last_name': 'Matei', 'age': 29, 'relation': 'colega_viorel', 'group': 'colegi_mirelui', 'cuisine': 'traditional'},
            {'first_name': 'Darius', 'last_name': 'Ilie', 'age': 28, 'relation': 'colegul_mirelui', 'group': 'colegi_mirelui', 'cuisine': 'modern'},
            {'first_name': 'Larisa', 'last_name': 'Ilie', 'age': 26, 'relation': 'colega_darius', 'group': 'colegi_mirelui', 'cuisine': 'modern'},
        ]
        
        # Creează utilizatorii și invitații
        for guest_data in realistic_guests:
            username = f"{guest_data['first_name'].lower()}_{guest_data['last_name'].lower()}"
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f"{username}@example.com",
                    'first_name': guest_data['first_name'],
                    'last_name': guest_data['last_name']
                }
            )
            
            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'username': username,
                    'email': user.email,
                    'first_name': guest_data['first_name'],
                    'last_name': guest_data['last_name'],
                    'age': guest_data['age'],
                    'approved': True
                }
            )
            
            guest, _ = Guests.objects.get_or_create(
                profile=profile,
                defaults={
                    'age': guest_data['age'],
                    'cuisine_preference': guest_data['cuisine'],
                    'gender': 'M' if guest_data['first_name'] in ['Ion', 'Alexandru', 'Gheorghe', 'Mihai', 'Vasile', 'Andrei', 'Florin', 'Radu', 'Bogdan', 'Stefan', 'Marian', 'Costel', 'Catalin', 'Liviu', 'Vlad', 'Adrian', 'Marius', 'George', 'Razvan', 'Dan', 'Ciprian', 'Lucian', 'Sorin', 'Florian', 'Tudor', 'Sergiu', 'Octavian', 'Calin', 'Petru', 'Ionut', 'Cristian', 'Dragos', 'Robert', 'Eugen', 'Viorel', 'Darius'] else 'F'
                }
            )
            
            event.guests.add(guest)
        
        # 5. Creează grupuri realiste cu priorități
        TableGroup.objects.filter(event=event).delete()
        
        # Grupul VIP - masa principală
        vip_group = TableGroup.objects.create(
            event=event,
            name='VIP - Bride and Groom',
            priority=10,
            notes='Main table with bride, groom, parents and grandparents'
        )
        vip_guests = event.guests.filter(
            profile__first_name__in=['Maria', 'Alexandru', 'Ion', 'Elena', 'Gheorghe', 'Ana', 'Cristina', 'Mihai', 'Ioana', 'Vasile', 'Ecaterina', 'Andrei']
        )
        vip_group.guests.set(vip_guests)
        vip_group.preferred_tables.add(Table.objects.get(location=location, table_number=1))
        
        # Familia miresei
        familia_miresei = TableGroup.objects.create(
            event=event,
            name="Bride's Family",
            priority=8,
            notes="Bride's extended family - aunts, uncles, cousins"
        )
        familia_miresei_guests = event.guests.filter(
            profile__last_name__in=['Constantin', 'Marinescu', 'Georgescu']
        )
        familia_miresei.guests.set(familia_miresei_guests)
        familia_miresei.preferred_tables.add(Table.objects.get(location=location, table_number=2))
        
        # Familia mirelui
        familia_mirelui = TableGroup.objects.create(
            event=event,
            name="Groom's Family",
            priority=8,
            notes="Groom's extended family - aunts, uncles, cousins"
        )
        familia_mirelui_guests = event.guests.filter(
            profile__last_name__in=['Dumitrescu', 'Popa', 'Stoica']
        )
        familia_mirelui.guests.set(familia_mirelui_guests)
        familia_mirelui.preferred_tables.add(Table.objects.get(location=location, table_number=3))
        
        # Prieteni apropiați miresei
        prieteni_miresei = TableGroup.objects.create(
            event=event,
            name="Bride's Close Friends",
            priority=6,
            notes="Bride's best friends and their partners"
        )
        prieteni_miresei_guests = event.guests.filter(
            profile__last_name__in=['Radu', 'Vasilescu', 'Munteanu', 'Cristea']
        )
        prieteni_miresei.guests.set(prieteni_miresei_guests)
        prieteni_miresei.preferred_tables.add(Table.objects.get(location=location, table_number=4))
        
        # Prieteni apropiați mirelui
        prieteni_mirelui = TableGroup.objects.create(
            event=event,
            name="Groom's Close Friends",
            priority=6,
            notes="Groom's best friends and their partners"
        )
        prieteni_mirelui_guests = event.guests.filter(
            profile__last_name__in=['Moldovan', 'Stanescu', 'Enache', 'Barbu']
        )
        prieteni_mirelui.guests.set(prieteni_mirelui_guests)
        prieteni_mirelui.preferred_tables.add(Table.objects.get(location=location, table_number=6))
        
        # Prieteni comuni
        prieteni_comuni = TableGroup.objects.create(
            event=event,
            name='Mutual Friends',
            priority=5,
            notes='Common friends of the couple'
        )
        prieteni_comuni_guests = event.guests.filter(
            profile__last_name__in=['Nistor', 'Lazar', 'Dobre', 'Toma']
        )
        prieteni_comuni.guests.set(prieteni_comuni_guests)
        prieteni_comuni.preferred_tables.add(Table.objects.get(location=location, table_number=5))
        
        # Colegi miresei
        colegi_miresei = TableGroup.objects.create(
            event=event,
            name="Bride's Colleagues",
            priority=3,
            notes="Bride's work colleagues"
        )
        colegi_miresei_guests = event.guests.filter(
            profile__last_name__in=['Mihai', 'Sandu', 'Preda', 'Ungureanu']
        )
        colegi_miresei.guests.set(colegi_miresei_guests)
        colegi_miresei.preferred_tables.add(Table.objects.get(location=location, table_number=7))
        
        # Colegi mirelui
        colegi_mirelui = TableGroup.objects.create(
            event=event,
            name="Groom's Colleagues",
            priority=3,
            notes="Groom's work colleagues"
        )
        colegi_mirelui_guests = event.guests.filter(
            profile__last_name__in=['Tanase', 'Badea', 'Matei', 'Ilie']
        )
        colegi_mirelui.guests.set(colegi_mirelui_guests)
        colegi_mirelui.preferred_tables.add(Table.objects.get(location=location, table_number=8))
        
        # 6. Aplică algoritmul de aranjare
        self.stdout.write(self.style.WARNING('🤖 Aplicând algoritmul inteligent de aranjare...'))
        
        # Șterge aranjamentele existente
        TableArrangement.objects.filter(event=event).delete()
        
        # Inițializează și rulează algoritmul
        algorithm = TableArrangementAlgorithm(event)
        arrangements = algorithm.generate_arrangement()
        
        # Salvează aranjamentele
        for arrangement in arrangements:
            arrangement.save()
        
        # Obține statisticile
        stats = algorithm.get_arrangement_statistics()
        
        # 7. Afișează rezultatele
        self.stdout.write(self.style.SUCCESS('\n🎉 SITUAȚIA REALISTĂ A FOST CREATĂ CU SUCCES!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'📍 Locație: {location.name}')
        self.stdout.write(f'🎊 Eveniment: {event.event_name}')
        self.stdout.write(f'👥 Total invitați: {event.guests.count()}')
        self.stdout.write(f'🪑 Total mese: {location.tables.count()}')
        self.stdout.write(f'👨‍👩‍👧‍👦 Grupuri create: {TableGroup.objects.filter(event=event).count()}')
        self.stdout.write(f'📊 Aranjamente generate: {TableArrangement.objects.filter(event=event).count()}')
        
        self.stdout.write(self.style.SUCCESS('\n📈 STATISTICI ALGORITM:'))
        self.stdout.write(f'• Utilizare mese: {stats["table_utilization"]}%')
        self.stdout.write(f'• Mese folosite: {stats["tables_used"]}/{stats["total_tables"]}')
        self.stdout.write(f'• Grupuri aranjate: {stats["groups_arranged"]}/{stats["total_groups"]}')
        self.stdout.write(f'• Coerență grupuri: {stats["group_cohesion"]:.1%}')
        self.stdout.write(f'• Invitați neasignați: {stats["unassigned_guests"]}')
        self.stdout.write(f'• Media invitați/masă: {stats["average_guests_per_table"]}')
        
        self.stdout.write(self.style.SUCCESS('\n🎯 DEMONSTRAȚIA ALGORITMULUI:'))
        self.stdout.write('• Grupurile VIP au prioritate maximă și sunt plasate la masa principală')
        self.stdout.write('• Familiile sunt păstrate împreună la mese apropiate')
        self.stdout.write('• Cuplurile sunt plasate la aceeași masă')
        self.stdout.write('• Invitații cu preferințe culinare similare sunt grupați')
        self.stdout.write('• Vârstele similare sunt luate în considerare')
        self.stdout.write('• Mesele sunt optimizate pentru socializare')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Pentru a vedea rezultatele:'))
        self.stdout.write('1. Accesează evenimentul "Event cu invitati reali"')
        self.stdout.write('2. Click pe "Table Arrangement" pentru a vedea aranjamentul')
        self.stdout.write('3. Click pe "Testează Aranjament Mese" pentru statistici detaliate')
        self.stdout.write('4. Observă cum algoritmul a optimizat plasarea invitaților!') 