from django.core.management.base import BaseCommand
from base.models import Location, Table, Type
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Configurează locația Perla Coșaului cu mesele necesare'

    def handle(self, *args, **kwargs):
        # Creăm sau obținem locația
        location, created = Location.objects.get_or_create(
            name="Perla Coșaului",
            defaults={
                'description': "O locație elegantă pentru evenimente deosebite",
                'location': "București, Sector 1",
                'seats_numbers': 200,
                'cost': 5000
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Locația Perla Coșaului a fost creată cu succes!'))
        else:
            self.stdout.write(self.style.SUCCESS('Locația Perla Coșaului există deja!'))

        # Ștergem mesele existente pentru a evita duplicarea
        Table.objects.filter(location=location).delete()

        # Configurăm mesele
        tables_config = [
            # Mese rotunde pentru grupurile principale
            {'number': 1, 'capacity': 10, 'shape': 'round', 'x': 100, 'y': 100, 'reserved': True, 'notes': 'Masa principală'},
            {'number': 2, 'capacity': 8, 'shape': 'round', 'x': 200, 'y': 100, 'reserved': False, 'notes': ''},
            {'number': 3, 'capacity': 8, 'shape': 'round', 'x': 300, 'y': 100, 'reserved': False, 'notes': ''},
            {'number': 4, 'capacity': 8, 'shape': 'round', 'x': 100, 'y': 200, 'reserved': False, 'notes': ''},
            {'number': 5, 'capacity': 8, 'shape': 'round', 'x': 200, 'y': 200, 'reserved': False, 'notes': ''},
            {'number': 6, 'capacity': 8, 'shape': 'round', 'x': 300, 'y': 200, 'reserved': False, 'notes': ''},
            
            # Mese dreptunghiulare pentru grupurile mai mari
            {'number': 7, 'capacity': 12, 'shape': 'rectangle', 'x': 400, 'y': 100, 'reserved': False, 'notes': ''},
            {'number': 8, 'capacity': 12, 'shape': 'rectangle', 'x': 400, 'y': 200, 'reserved': False, 'notes': ''},
            
            # Mese pătrate pentru grupurile mai mici
            {'number': 9, 'capacity': 6, 'shape': 'square', 'x': 500, 'y': 100, 'reserved': False, 'notes': ''},
            {'number': 10, 'capacity': 6, 'shape': 'square', 'x': 500, 'y': 200, 'reserved': False, 'notes': ''},
        ]

        # Creăm mesele
        for table_config in tables_config:
            Table.objects.create(
                location=location,
                table_number=table_config['number'],
                capacity=table_config['capacity'],
                shape=table_config['shape'],
                position_x=table_config['x'],
                position_y=table_config['y'],
                is_reserved=table_config['reserved'],
                notes=table_config['notes']
            )

        self.stdout.write(self.style.SUCCESS(f'S-au creat {len(tables_config)} mese pentru Perla Coșaului!')) 