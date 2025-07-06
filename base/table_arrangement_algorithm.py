from django.db.models import Q
from .models import Event, Table, TableGroup, TableArrangement, Guests
from typing import List, Dict, Set, Tuple
import logging

logger = logging.getLogger(__name__)

class TableArrangementAlgorithm:
    def __init__(self, event: Event):
        self.event = event
        self.tables = list(Table.objects.filter(location=event.location).order_by('table_number'))
        self.guests = list(event.guests.all())
        self.groups = list(TableGroup.objects.filter(event=event).order_by('-priority'))
        self.arrangements = {}                                                      
        self.constraints = {
            'max_guests_per_table': 10,                                      
            'min_guests_per_table': 4,                                       
            'preferred_group_size': 8,                                            
            'max_distance_between_tables': 5,                                                    
        }

    def _calculate_table_distances(self) -> Dict[Tuple[int, int], float]:
        distances = {}
        for t1 in self.tables:
            for t2 in self.tables:
                if t1.id != t2.id:
                    distance = ((t1.position_x - t2.position_x) ** 2 + 
                              (t1.position_y - t2.position_y) ** 2) ** 0.5
                    distances[(t1.id, t2.id)] = distance
        return distances

    def _get_available_seats(self, table: Table) -> int:
        current_arrangements = TableArrangement.objects.filter(
            event=self.event,
            table=table,
            status='confirmed'
        ).count()
        return table.capacity - current_arrangements

    def _check_table_compatibility(self, table: Table, guest: Guests) -> bool:
                                                               
        if table.is_reserved:
            reserved_groups = TableGroup.objects.filter(
                event=self.event,
                preferred_tables=table,
                guests=guest
            )
            if not reserved_groups.exists():
                return False

                                                  
        if self._get_available_seats(table) < 1:
            return False

                                                                                   
        if guest.allergens.exists():
                                                              
                                                                
            pass

        return True

    def _find_best_table_for_group(self, group: TableGroup) -> List[Table]:
        available_tables = []
        for table in self.tables:
            if self._check_table_compatibility(table, group.guests.first()):
                available_seats = self._get_available_seats(table)
                if available_seats >= len(group.guests.all()):
                    available_tables.append((table, available_seats))

                                                            
        available_tables.sort(key=lambda x: (
            x[0] in group.preferred_tables.all(),              
            -x[1]                                                                   
        ), reverse=True)

        return [table for table, _ in available_tables]

    def _assign_guests_to_tables(self) -> Dict[int, List[Guests]]:
        assignments = {table.id: [] for table in self.tables}
        unassigned_guests = set(self.guests)

                                                     
        for group in self.groups:
            if not group.guests.exists():
                continue

            group_guests = list(group.guests.all())
            best_tables = self._find_best_table_for_group(group)

            if best_tables:
                                                                
                for table in best_tables:
                    if len(group_guests) <= self._get_available_seats(table):
                                                                 
                        for guest in group_guests:
                            if guest in unassigned_guests:
                                assignments[table.id].append(guest)
                                unassigned_guests.remove(guest)
                        break

                                                   
        for guest in list(unassigned_guests):
            best_table = None
            best_score = float('-inf')

            for table in self.tables:
                if not self._check_table_compatibility(table, guest):
                    continue

                                                        
                score = 0
                current_guests = assignments[table.id]
                
                                                                           
                if len(current_guests) < self.constraints['preferred_group_size']:
                    score += 1

                                                               
                if current_guests:
                    avg_age = sum(g.age or 0 for g in current_guests) / len(current_guests)
                    if guest.age and abs(guest.age - avg_age) < 10:
                        score += 2

                                                                            
                if guest.cuisine_preference:
                    similar_preferences = sum(1 for g in current_guests 
                                           if g.cuisine_preference == guest.cuisine_preference)
                    score += similar_preferences

                if score > best_score:
                    best_score = score
                    best_table = table

            if best_table:
                assignments[best_table.id].append(guest)
                unassigned_guests.remove(guest)

        return assignments

    def _validate_arrangements(self, assignments: Dict[int, List[Guests]]) -> bool:
        for table_id, guests in assignments.items():
            table = next(t for t in self.tables if t.id == table_id)
            
                                        
            if len(guests) > table.capacity:
                logger.warning(f"Table {table.table_number} exceeds capacity")
                return False

                                                
            if len(guests) < self.constraints['min_guests_per_table']:
                logger.warning(f"Table {table.table_number} has too few guests")
                return False

                                                                 
            for guest in guests:
                if not self._check_table_compatibility(table, guest):
                    logger.warning(f"Guest {guest} is not compatible with table {table.table_number}")
                    return False

        return True

    def generate_arrangement(self):
      
        print("DEBUG: Începe algoritmul de aranjare inteligentă")
        
                                                               
        assignments = self._assign_guests_to_tables()
        
                                 
        if not self._validate_arrangements(assignments):
            print("DEBUG: Aranjamentele nu respectă toate constrângerile, se încearcă o abordare mai permisivă")
                                                                               
            return self._generate_permissive_arrangement()
        
                                                               
        arrangements = []
        for table_id, guests in assignments.items():
            table = next(t for t in self.tables if t.id == table_id)
            for seat_number, guest in enumerate(guests, 1):
                arrangement = TableArrangement(
                    event=self.event,
                    guest=guest,
                    table=table,
                    seat_number=seat_number,
                    status='pending',
                    is_priority=guest.is_priority if hasattr(guest, 'is_priority') else False
                )
                arrangements.append(arrangement)
                print(f"DEBUG: Invitat {guest} plasat la masa {table.table_number}, loc {seat_number}")
        
        return arrangements

    def _generate_permissive_arrangement(self):
        arrangements = []
        guests = list(self.guests)
        tables = list(self.tables)
        table_seats = {table: [] for table in tables}
        table_capacities = {table: table.capacity for table in tables}
        seat_counter = {table: 1 for table in tables}

        print("DEBUG: Folosire algoritm permisiv ca fallback")
        for guest in guests:
            placed = False
            for table in tables:
                if len(table_seats[table]) < table_capacities[table]:
                    arrangement = TableArrangement(
                        event=self.event,
                        guest=guest,
                        table=table,
                        seat_number=seat_counter[table],
                        status='pending',
                        is_priority=guest.is_priority if hasattr(guest, 'is_priority') else False
                    )
                    arrangements.append(arrangement)
                    table_seats[table].append(guest)
                    seat_counter[table] += 1
                    print(f"DEBUG: Invitat {guest} plasat la masa {table.table_number}, loc {seat_counter[table]-1}")
                    placed = True
                    break
            if not placed:
                print(f"DEBUG: Nu există locuri libere pentru invitatul {guest}")
        
        return arrangements

    def optimize_arrangement(self) -> List[TableArrangement]:
        current_arrangements = TableArrangement.objects.filter(
            event=self.event,
            status='confirmed'
        )

                                             
                                                      
                                                        
                                               
                                                

                                                  
        return list(current_arrangements)

    def get_arrangement_statistics(self) -> Dict:
                                                           
        arrangements = TableArrangement.objects.filter(event=self.event)
        
                                         
        total_guests = len(self.guests)
        total_tables = len(self.tables)
        tables_used = arrangements.values('table').distinct().count()
        
                                       
        total_seats = sum(table.capacity for table in self.tables)
        used_seats = arrangements.count()
        table_utilization = round((used_seats / total_seats) * 100, 1) if total_seats else 0
        
                                                
        total_groups = len(self.groups)
        groups_arranged = 0
        
                               
        for group in self.groups:
            if not group.guests.exists():
                continue
                
            group_guests = set(group.guests.all())
            if not group_guests:
                continue
                
                                                                                     
            group_arrangements = arrangements.filter(guest__in=group_guests)
            if group_arrangements.count() == len(group_guests):
                groups_arranged += 1
        
                                               
        avg_guests_per_table = round(used_seats / tables_used, 1) if tables_used > 0 else 0
        
                                        
        group_cohesion = self._calculate_group_cohesion()
        
        stats = {
            'total_guests': total_guests,
            'total_tables': total_tables,
            'tables_used': tables_used,
            'average_guests_per_table': avg_guests_per_table,
            'unassigned_guests': total_guests - used_seats,
            'group_cohesion': group_cohesion,
            'groups_arranged': groups_arranged,
            'total_groups': total_groups,
            'table_utilization': table_utilization,
        }
        
        print(f"DEBUG: Statistici calculate: {stats}")
        return stats

    def _calculate_group_cohesion(self) -> float:
        total_cohesion = 0
        total_groups = 0

        for group in self.groups:
            if not group.guests.exists():
                continue

            group_guests = set(group.guests.all())
            if not group_guests:
                continue

                                                       
            guest_tables = TableArrangement.objects.filter(
                event=self.event,
                guest__in=group_guests
            ).values_list('table', flat=True).distinct()

                                                                                      
            if guest_tables:
                cohesion = max(
                    len(group_guests.intersection(
                        set(TableArrangement.objects.filter(
                            event=self.event,
                            table=table
                        ).values_list('guest', flat=True))
                    )) / len(group_guests)
                    for table in guest_tables
                )
                total_cohesion += cohesion
                total_groups += 1

        return total_cohesion / total_groups if total_groups > 0 else 0.0 