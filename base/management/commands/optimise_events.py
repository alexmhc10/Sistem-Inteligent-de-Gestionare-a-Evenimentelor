
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from base.models import  *
import random
from datetime import date, timedelta
from django.utils import timezone
import uuid # Pentru run_id

def fetch_data_from_db_for_command(stdout, style): 
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
    
    optimizable_events = []
    fixed_events = []
    
    for event in db_events_raw:
        if not event['completed'] and not event['is_canceled'] and event['date'] > date.today():
            optimizable_events.append(event)
        else:
            fixed_events.append(event)

    stdout.write(style.NOTICE(f"Fetched Users: {len(all_users)}"))
    stdout.write(style.NOTICE(f"Fetched Types: {all_types}"))
    stdout.write(style.NOTICE(f"Fetched Locations ({len(db_locations)}):"))

    return all_users, all_types, db_locations, locations_by_id, optimizable_events, fixed_events, db_events_raw


def run_genetic_optimization(stdout, style):

    stdout.write(style.SUCCESS('Fetching data for optimization...'))
    all_users, all_types, db_locations, locations_by_id, optimizable_events, fixed_events, all_events_for_report = fetch_data_from_db_for_command(stdout, style)

    BUDGET = 100000
    MAX_GENERATIONS = 30
    POPULATION_SIZE = 20

    def is_locked_by_status(event): 
        return event['completed'] or event['is_canceled']

    def create_solution_for_optimizable_events():
        solution = [-1] * len(optimizable_events) 
        schedule_slots_taken = {}

        for event in fixed_events:
            original_loc_data = event['original_location']
            loc = locations_by_id.get(original_loc_data['id']) if original_loc_data else None
            if loc:
                if all(t_id in loc['accepted_types'] for t_id in event['type_ids']):
                    event_date_key = (loc['id'], event['date'])
                    if event_date_key not in schedule_slots_taken:
                        schedule_slots_taken[event_date_key] = event['id']

        for i, event in enumerate(optimizable_events):
            valid_and_available_locs = []
            for loc in db_locations: # Folosește db_locations aici
                if all(event_type_id in loc['accepted_types'] for event_type_id in event['type_ids']):
                    if (loc['id'], event['date']) not in schedule_slots_taken:
                        valid_and_available_locs.append(loc['id'])
            if valid_and_available_locs:
                chosen_loc_id = random.choice(valid_and_available_locs)
                solution[i] = chosen_loc_id
                schedule_slots_taken[(chosen_loc_id, event['date'])] = event['id']
            else:
                solution[i] = -1
        return solution

    def fitness(solution_for_optimizable):
        total_profit = 0
        total_cost = 0
        penalty = 0
        location_daily_availability = {}
        infeasible_event_details = []

        for event in fixed_events:
            original_loc_data = event['original_location']
            loc = locations_by_id.get(original_loc_data['id']) if original_loc_data else None
            if loc:
                if not all(t_id in loc['accepted_types'] for t_id in event['type_ids']):
                    penalty += 5000
                    infeasible_event_details.append(f"Fixed Event {event['name']} (ID: {event['id']}) - Type mismatch with original location {loc['name']}")
                
                event_date_key = (loc['id'], event['date'])
                if event_date_key in location_daily_availability:
                    penalty += 50000
                    infeasible_event_details.append(f"Fixed Event {event['name']} (ID: {event['id']}) - Date conflict at {loc['name']} on {event['date']} with Event {location_daily_availability[event_date_key]}")
                else:
                    location_daily_availability[event_date_key] = event['id']
                    total_cost += loc['cost']
                    total_profit += event['cost']
            else:
                penalty += 5000
                infeasible_event_details.append(f"Fixed Event {event['name']} (ID: {event['id']}) - Original location not found or invalid/unassigned!")

        for i, loc_id in enumerate(solution_for_optimizable):
            event = optimizable_events[i]
            if loc_id == -1:
                penalty += 5000 
                infeasible_event_details.append(f"Optimizable Event {event['name']} (ID: {event['id']}) - No valid location assigned (-1 ID)")
                continue

            loc = locations_by_id.get(loc_id)
            if not loc:
                penalty += 50000 
                infeasible_event_details.append(f"Optimizable Event {event['name']} (ID: {event['id']}) - Assigned to non-existent location ID {loc_id}")
                continue

            if not all(t_id in loc['accepted_types'] for t_id in event['type_ids']):
                penalty += 5000 
                infeasible_event_details.append(f"Optimizable Event {event['name']} (ID: {event['id']}) - Type mismatch: {event['type_ids']} with {loc['name']} (accepts {loc['accepted_types']})")

            event_date_key = (loc['id'], event['date'])
            if event_date_key in location_daily_availability:
                penalty += 50000 
                infeasible_event_details.append(f"Optimizable Event {event['name']} (ID: {event['id']}) - Date conflict at {loc['name']} on {event['date']} with Event {location_daily_availability[event_date_key]}")
            else:
                location_daily_availability[event_date_key] = event['id']

            total_cost += loc['cost']
            total_profit += event['cost']

        if total_cost > BUDGET:
            penalty += (total_cost - BUDGET) * 2

        fit_val = total_profit - total_cost - penalty

        if fit_val <= 0 and infeasible_event_details:
            stdout.write(style.WARNING(f"\n--- DEBUG: Fitness Calculation for current solution ---"))
            return 0
        return fit_val

    def select_population(population):
        graded = [(fitness(sol), sol) for sol in population]
        graded = [x for x in graded if x[0] > 0]
        graded = sorted(graded, key=lambda x: x[0], reverse=True)
        return [x[1] for x in graded[:min(POPULATION_SIZE // 2, len(graded))]]

    def mutate(solution_for_optimizable):
        mutated_solution = list(solution_for_optimizable)
        if not optimizable_events:
            return mutated_solution

        current_schedule = {}
        for event in fixed_events:
            original_loc_data = event['original_location']
            loc = locations_by_id.get(original_loc_data['id']) if original_loc_data else None
            if loc and all(t_id in loc['accepted_types'] for t_id in event['type_ids']):
                event_date_key = (loc['id'], event['date'])
                current_schedule[event_date_key] = event['id']

        for idx, loc_id in enumerate(mutated_solution):
            event = optimizable_events[idx]
            loc = locations_by_id.get(loc_id)
            if loc and all(t_id in loc['accepted_types'] for t_id in event['type_ids']):
                event_date_key = (loc['id'], event['date'])
                if event_date_key not in current_schedule:
                    current_schedule[event_date_key] = event['id']

        idx_to_mutate = random.choice(range(len(optimizable_events))) 
        event_to_mutate = optimizable_events[idx_to_mutate]
        original_loc_id_of_mutated = mutated_solution[idx_to_mutate]

        if original_loc_id_of_mutated != -1:
            event_date_key = (original_loc_id_of_mutated, event_to_mutate['date'])
            if event_date_key in current_schedule and current_schedule[event_date_key] == event_to_mutate['id']:
                del current_schedule[event_date_key]

        available_valid_locs = []
        for loc in db_locations: 
            if all(event_type_id in loc['accepted_types'] for event_type_id in event_to_mutate['type_ids']):
                if (loc['id'], event_to_mutate['date']) not in current_schedule:
                    available_valid_locs.append(loc['id'])

        if available_valid_locs:
            mutated_solution[idx_to_mutate] = random.choice(available_valid_locs)
        else:
            mutated_solution[idx_to_mutate] = -1
        return mutated_solution

    def crossover(sol1, sol2):
        if len(sol1) < 2:
            return list(sol1), list(sol2)
        pos = random.randint(1, len(sol1) - 1)
        child1 = list(sol1[:pos]) + list(sol2[pos:])
        child2 = list(sol2[:pos]) + list(sol1[pos:])
        return child1, child2

    def repair_solution(solution_to_repair):
        repaired_solution = list(solution_to_repair)
        schedule_slots_taken = {}
        
        for event in fixed_events:
            original_loc_data = event['original_location']
            loc = locations_by_id.get(original_loc_data['id']) if original_loc_data else None
            if loc:
                if all(t_id in loc['accepted_types'] for t_id in event['type_ids']):
                    event_date_key = (loc['id'], event['date'])
                    if event_date_key not in schedule_slots_taken:
                        schedule_slots_taken[event_date_key] = event['id']
            
        optimizable_event_indices_sorted = sorted(range(len(optimizable_events)), key=lambda i: optimizable_events[i]['id'])

        for i in optimizable_event_indices_sorted:
            event = optimizable_events[i]
            current_assigned_loc_id = repaired_solution[i]
            loc_candidate = locations_by_id.get(current_assigned_loc_id)

            is_valid_current_assignment = False
            if loc_candidate and all(t_id in loc_candidate['accepted_types'] for t_id in event['type_ids']):
                event_date_key = (loc_candidate['id'], event['date'])
                if event_date_key not in schedule_slots_taken:
                    schedule_slots_taken[event_date_key] = event['id']
                    is_valid_current_assignment = True

            if not is_valid_current_assignment:
                valid_and_available_alternatives = []
                for alt_loc in db_locations: # Folosește db_locations aici
                    if all(event_type_id in alt_loc['accepted_types'] for event_type_id in event['type_ids']):
                        if (alt_loc['id'], event['date']) not in schedule_slots_taken:
                            valid_and_available_alternatives.append(alt_loc['id'])

                if valid_and_available_alternatives:
                    chosen_alt_loc = random.choice(valid_and_available_alternatives)
                    repaired_solution[i] = chosen_alt_loc
                    schedule_slots_taken[(chosen_alt_loc, event['date'])] = event['id']
                else:
                    repaired_solution[i] = -1
        return repaired_solution
    


    population = [repair_solution(create_solution_for_optimizable_events()) for _ in range(POPULATION_SIZE)]

    for gen in range(MAX_GENERATIONS):
        population = select_population(population)
        if len(population) < 2:
            num_to_add = POPULATION_SIZE - len(population)
            if num_to_add > 0:
                population.extend([repair_solution(create_solution_for_optimizable_events()) for _ in range(num_to_add)])
            if len(population) < 2 and POPULATION_SIZE >= 2:
                stdout.write(style.WARNING(f"Warning: Population size fell below 2 in generation {gen+1}. Reinitializing entire population."))
                population = [repair_solution(create_solution_for_optimizable_events()) for _ in range(POPULATION_SIZE)]
            elif len(population) < 2:
                break

        offspring = []
        while len(offspring) + len(population) < POPULATION_SIZE:
            if len(population) < 2:
                break
            parents = random.sample(population, 2)
            child1, child2 = crossover(parents[0], parents[1])
            offspring.append(repair_solution(mutate(child1)))
            if len(offspring) + len(population) < POPULATION_SIZE:
                offspring.append(repair_solution(mutate(child2)))

        population.extend(offspring)
        population = [repair_solution(sol) for sol in population]

        if population:
            best_fit_sol = max(population, key=fitness)
            stdout.write(f"Gen {gen+1} best fitness: {fitness(best_fit_sol)}")
        else:
            stdout.write(style.WARNING(f"Gen {gen+1}: No valid solutions in population. Best fitness: N/A"))
            break

    best_solution_for_optimizable = []
    if population:
        best_solution_for_optimizable = repair_solution(max(population, key=fitness))
    
    optimizable_assignments = {
        optimizable_events[i]['id']: best_solution_for_optimizable[i]
        for i in range(len(optimizable_events))
    }

    stdout.write(style.SUCCESS("\nSaving optimized assignments to OptimisedEvent model..."))
    
    current_run_id = uuid.uuid4() 

    for event_data in all_events_for_report: 
        event_obj = Event.objects.get(id=event_data['id'])
        
        original_loc_obj = event_obj.location 
        original_loc_cost = float(original_loc_obj.cost) if original_loc_obj else 0.0

        optimized_loc_obj = None
        optimized_loc_cost = 0.0

        if not event_data['completed'] and not event_data['is_canceled'] and event_data['date'] > date.today():
            assigned_loc_id = optimizable_assignments.get(event_data['id'], -1)
            if assigned_loc_id != -1:
                try:
                    optimized_loc_obj = Location.objects.get(id=assigned_loc_id)
                    optimized_loc_cost = float(optimized_loc_obj.cost)
                except Location.DoesNotExist:
                    stdout.write(style.ERROR(f"Location with ID {assigned_loc_id} not found for event {event_obj.event_name}. Setting optimized location to None."))
                    optimized_loc_obj = None 
            else:
                 stdout.write(style.WARNING(f"Event {event_obj.event_name} was optimizable but not assigned a valid location by GA."))
        else:
            optimized_loc_obj = original_loc_obj
            optimized_loc_cost = original_loc_cost

        event_gross_profit = float(event_obj.cost)

        profit_net_old = event_gross_profit - original_loc_cost
        profit_net_new = event_gross_profit - optimized_loc_cost


        OptimisedEvent.objects.create(
            event=event_obj,
            original_location=original_loc_obj,
            original_location_cost=original_loc_cost,
            optimized_location=optimized_loc_obj,
            optimized_location_cost=optimized_loc_cost,
            event_gross_profit=event_gross_profit,
            profit_net_old=profit_net_old,
            profit_net_new=profit_net_new,
            optimized_at=timezone.now(),
            run_id=current_run_id
        )
        stdout.write(style.SUCCESS(f"  - Optimization result for '{event_obj.event_name}' (ID: {event_obj.id}) saved."))
    
    stdout.write(style.SUCCESS("Optimized assignments saved to OptimisedEvent model successfully."))

class Command(BaseCommand):
    help = 'Runs the genetic algorithm to optimize event-location assignments.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting event optimization from management command...'))
        run_genetic_optimization(self.stdout, self.style)
        self.stdout.write(self.style.SUCCESS('Event optimization completed from management command.'))