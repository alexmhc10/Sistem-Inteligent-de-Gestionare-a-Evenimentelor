from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from base.models import *
import random
from datetime import date, timedelta
from django.utils import timezone
import uuid
from django.db import transaction

class Command(BaseCommand):
    help = 'Runs the genetic algorithm to optimize event-location assignments.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting event optimization...'))
        self.run_genetic_optimization()
        self.stdout.write(self.style.SUCCESS('Optimization completed.'))

    def fetch_data_from_db(self):
        """Fetch all required data from database"""
        User = get_user_model()
        all_users = {user.id: user for user in User.objects.all()}
        all_types = {type_obj.id: type_obj.name for type_obj in Type.objects.all()}

        db_locations = []
        for loc_obj in Location.objects.prefetch_related('types').all():
            db_locations.append({
                'id': loc_obj.id,
                'name': loc_obj.name,
                'cost': float(loc_obj.cost),
                'accepted_types': [t.id for t in loc_obj.types.all()],
                'owner': loc_obj.owner
            })
        locations_by_id = {loc['id']: loc for loc in db_locations}

        db_events_raw = []
        for event_obj in Event.objects.prefetch_related('types').select_related('location', 'organized_by').all():
            original_location_data = None
            if event_obj.location:
                original_location_data = {
                    'id': event_obj.location.id,
                    'name': event_obj.location.name,
                    'cost': float(event_obj.location.cost)
                }
            db_events_raw.append({
                'id': event_obj.id,
                'name': event_obj.event_name,
                'type_ids': [t.id for t in event_obj.types.all()],
                'cost': float(event_obj.cost),
                'date': event_obj.event_date,
                'organized_by': event_obj.organized_by,
                'completed': event_obj.completed,
                'is_canceled': event_obj.is_canceled,
                'original_location': original_location_data
            })
        
        return all_users, all_types, db_locations, locations_by_id, db_events_raw

    def run_genetic_optimization(self):
        """Main genetic algorithm optimization function"""
        budget = Budget.objects.first()
        total_budget = budget.final_budget
        BUDGET = total_budget
        MAX_GENERATIONS = 30
        POPULATION_SIZE = 20
        STAGNATION_LIMIT = 5
        
        # Fetch data
        all_users, all_types, db_locations, locations_by_id, db_events_raw = self.fetch_data_from_db()
        
        # Split events into optimizable and fixed
        optimizable_events = []
        fixed_events = []
        for event in db_events_raw:
            if not event['completed'] and not event['is_canceled'] and event['date'] > date.today():
                optimizable_events.append(event)
            else:
                fixed_events.append(event)

        self.stdout.write(self.style.SUCCESS(f'Found {len(optimizable_events)} optimizable events and {len(fixed_events)} fixed events.'))

        def create_initial_solution():
            """Create a valid initial solution"""
            solution = [-1] * len(optimizable_events)
            schedule_slots_taken = {}

            # Mark fixed events slots as taken
            for event in fixed_events:
                if event['original_location'] and event['date'] >= date.today():
                    loc = locations_by_id.get(event['original_location']['id'])
                    if loc and all(t_id in loc['accepted_types'] for t_id in event['type_ids']):
                        schedule_slots_taken[(loc['id'], event['date'])] = event['id']

            # Assign locations to optimizable events
            for i, event in enumerate(optimizable_events):
                valid_locs = [
                    loc['id'] for loc in db_locations 
                    if all(t_id in loc['accepted_types'] for t_id in event['type_ids'])
                    and (loc['id'], event['date']) not in schedule_slots_taken
                ]
                if valid_locs:
                    chosen_loc = random.choice(valid_locs)
                    solution[i] = chosen_loc
                    schedule_slots_taken[(chosen_loc, event['date'])] = event['id']

            return solution

        def fitness(solution):
            """Calculate fitness of a solution"""
            total_cost = 0
            total_profit = 0
            penalty = 0
            used_slots = {}

            # Process fixed events first
            for event in fixed_events:
                if event['original_location']:
                    loc = locations_by_id.get(event['original_location']['id'])
                    if loc:
                        slot = (loc['id'], event['date'])
                        if slot in used_slots:
                            penalty += 5000  # Double booking penalty
                        else:
                            used_slots[slot] = True
                            total_cost += loc['cost']
                            total_profit += event['cost']

            # Process optimizable events
            for i, loc_id in enumerate(solution):
                if loc_id == -1:
                    penalty += 1000  # Unassigned event penalty
                    continue
                    
                loc = locations_by_id.get(loc_id)
                if not loc:
                    penalty += 2000  # Invalid location penalty
                    continue
                    
                event = optimizable_events[i]
                slot = (loc_id, event['date'])
                
                if slot in used_slots:
                    penalty += 5000  # Double booking penalty
                else:
                    used_slots[slot] = True
                    total_cost += loc['cost']
                    total_profit += event['cost']

            # Budget constraint
            if total_cost > BUDGET:
                penalty += (total_cost - BUDGET) * 2

            return total_profit - total_cost - penalty

        def mutate(solution):
            """Mutate a solution"""
            new_solution = list(solution)
            if not optimizable_events:
                return new_solution

            # Find all currently used slots
            used_slots = {}
            for event in fixed_events:
                if event['original_location']:
                    loc = locations_by_id.get(event['original_location']['id'])
                    if loc:
                        used_slots[(loc['id'], event['date'])] = True

            for i, loc_id in enumerate(new_solution):
                if loc_id != -1:
                    event = optimizable_events[i]
                    used_slots[(loc_id, event['date'])] = True

            # Select a random event to mutate
            idx = random.randint(0, len(optimizable_events)-1)
            event = optimizable_events[idx]
            
            # Find all valid alternative locations
            valid_locs = [
                loc['id'] for loc in db_locations 
                if all(t_id in loc['accepted_types'] for t_id in event['type_ids'])
                and (loc['id'], event['date']) not in used_slots
            ]
            
            if valid_locs:
                new_solution[idx] = random.choice(valid_locs)
            else:
                new_solution[idx] = -1

            return new_solution

        def crossover(parent1, parent2):
            """Crossover two parents to produce offspring"""
            if len(parent1) <= 1:
                return parent1, parent2
                
            point = random.randint(1, len(parent1)-1)
            child1 = parent1[:point] + parent2[point:]
            child2 = parent2[:point] + parent1[point:]
            return child1, child2

        def select_parents(population):
            """Select parents using tournament selection"""
            tournament_size = min(5, len(population))
            parents = []
            
            for _ in range(2):
                candidates = random.sample(population, tournament_size)
                parents.append(max(candidates, key=lambda x: fitness(x)))
                
            return parents[0], parents[1]

        # Initialize population
        population = [create_initial_solution() for _ in range(POPULATION_SIZE)]
        best_solution = None
        best_fitness = -float('inf')
        stagnation_count = 0

        # Main GA loop
        for generation in range(MAX_GENERATIONS):
            # Evaluate population
            population = sorted(population, key=lambda x: fitness(x), reverse=True)
            current_best = population[0]
            current_fitness = fitness(current_best)
            
            # Check for improvement
            if current_fitness > best_fitness:
                best_fitness = current_fitness
                best_solution = current_best
                stagnation_count = 0
            else:
                stagnation_count += 1
                
            self.stdout.write(f'Generation {generation+1}: Best fitness = {best_fitness}')

            # Check termination conditions
            if stagnation_count >= STAGNATION_LIMIT:
                self.stdout.write(self.style.SUCCESS(f'Stopping early due to stagnation after {generation+1} generations.'))
                break

            # Create new generation
            new_population = population[:2]  # Keep top 2 solutions (elitism)
            
            while len(new_population) < POPULATION_SIZE:
                parent1, parent2 = select_parents(population)
                child1, child2 = crossover(parent1, parent2)
                new_population.append(mutate(child1))
                if len(new_population) < POPULATION_SIZE:
                    new_population.append(mutate(child2))
                    
            population = new_population

        # Save results
        if best_solution:
            self.save_optimization_results(optimizable_events, fixed_events, db_events_raw, 
                                         locations_by_id, best_solution)
        else:
            self.stdout.write(self.style.ERROR('No valid solution found!'))

    def save_optimization_results(self, optimizable_events, fixed_events, all_events, 
                                locations_by_id, best_solution):
        """Save optimization results to database"""
        current_run_id = uuid.uuid4()
        optimization_time = timezone.now()
        
        # Create mapping from event ID to optimized location ID
        optimizable_assignments = {
            optimizable_events[i]['id']: best_solution[i]
            for i in range(len(optimizable_events))
        }

        # Disable signals temporarily to prevent infinite loops
        from django.db.models.signals import post_save
        from base.signals import event_changed_handler, location_changed_handler
        post_save.disconnect(event_changed_handler, sender=Event)
        post_save.disconnect(location_changed_handler, sender=Location)

        try:
            for event_data in all_events:
                event_obj = Event.objects.get(id=event_data['id'])
                
                # Skip if event is completed/canceled or in the past
                if event_data['completed'] or event_data['is_canceled'] or event_data['date'] <= date.today():
                    optimized_loc_obj = event_obj.location
                else:
                    # Get optimized location for this event
                    optimized_loc_id = optimizable_assignments.get(event_data['id'], -1)
                    optimized_loc_obj = Location.objects.get(id=optimized_loc_id) if optimized_loc_id != -1 else None
                
                # Calculate financial metrics
                original_loc_cost = float(event_obj.location.cost) if event_obj.location else 0.0
                optimized_loc_cost = float(optimized_loc_obj.cost) if optimized_loc_obj else 0.0
                event_gross_profit = float(event_obj.cost)
                
                # Create optimization record
                OptimisedEvent.objects.create(
                    event=event_obj,
                    original_location=event_obj.location,
                    original_location_cost=original_loc_cost,
                    optimized_location=optimized_loc_obj,
                    optimized_location_cost=optimized_loc_cost,
                    event_gross_profit=event_gross_profit,
                    profit_net_old=event_gross_profit - original_loc_cost,
                    profit_net_new=event_gross_profit - optimized_loc_cost,
                    optimized_at=optimization_time,
                    run_id=current_run_id
                )
                
                if optimized_loc_obj and event_obj.location != optimized_loc_obj:
                    event_obj.location = optimized_loc_obj
                    event_obj.save(update_fields=['location'])
                    
                self.stdout.write(self.style.SUCCESS(f"Processed event: {event_obj.event_name}"))
                
        finally:
            post_save.connect(event_changed_handler, sender=Event)
            post_save.connect(location_changed_handler, sender=Location)