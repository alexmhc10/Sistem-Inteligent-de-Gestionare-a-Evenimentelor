from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from base.models import Type, Location, Event # Asigură-te că modelele sunt importate corect

import random
from datetime import date, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Runs the genetic algorithm to optimize event-location assignments for future, uncompleted events.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting event optimization...'))

        # --- Fetch data from database ---
        def fetch_data_from_db_for_command(self):
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
                    'owner': loc_obj.owner # Presupunem că owner este un obiect User
                })

            # Fetch all events initially
            db_events_raw = []
            for event_obj in Event.objects.prefetch_related('types').select_related('location', 'organized_by').all():
                db_events_raw.append({
                    'id': event_obj.id,
                    'name': event_obj.event_name,
                    'type_ids': [t.id for t in event_obj.types.all()],
                    'cost': float(event_obj.cost),
                    'date': event_obj.event_date,
                    'organized_by': event_obj.organized_by, # Obiect User
                    'completed': event_obj.completed,
                    'is_canceled': event_obj.is_canceled,
                    'location_id': event_obj.location.id if event_obj.location else -1 # Store original location ID
                })
            
            # Separate events into optimizable and fixed categories
            optimizable_events = [] # These are the events the GA will actively assign
            fixed_events = []      # These are events that will not be touched by the GA (past, completed, canceled)
            
            # Map original event ID to its index in the raw list for easy lookup
            event_id_to_original_index = {event['id']: i for i, event in enumerate(db_events_raw)}
            
            for event in db_events_raw:
                # An event is optimizable if it's not completed, not canceled, AND its date is in the future
                if not event['completed'] and not event['is_canceled'] and event['date'] > date.today():
                    optimizable_events.append(event)
                else:
                    fixed_events.append(event)


            self.stdout.write(self.style.NOTICE(f"Fetched Users: {len(all_users)}"))
            self.stdout.write(self.style.NOTICE(f"Fetched Types: {all_types}"))

            self.stdout.write(self.style.NOTICE(f"Fetched Locations ({len(db_locations)}):"))
            for loc in db_locations:
                self.stdout.write(self.style.NOTICE(f"    - {loc['name']} (ID: {loc['id']}, Cost: {loc['cost']}, Accepted Types IDs: {loc['accepted_types']}, Owner: {loc['owner'].username})"))
            
            self.stdout.write(self.style.NOTICE(f"Fetched Events (Total: {len(db_events_raw)}, Optimizable: {len(optimizable_events)}, Fixed: {len(fixed_events)}):"))
            for event in db_events_raw:
                organizer_username = event['organized_by'].username if event['organized_by'] else 'N/A'
                # is_locked_for_display includes past date, completed, canceled
                is_locked_for_display = event['completed'] or event['is_canceled'] or event['date'] <= date.today()
                self.stdout.write(self.style.NOTICE(f"    - {event['name']} (ID: {event['id']}, Types IDs: {event['type_ids']}, Date: {event['date']}, Locked: {is_locked_for_display}, Location ID: {event['location_id']}, Organized By: {organizer_username})"))

            return all_users, all_types, db_locations, optimizable_events, fixed_events, event_id_to_original_index, db_events_raw

        # Assign fetched data to variables
        users, types, locations, optimizable_events, fixed_events, event_id_to_original_index, all_events_for_report = fetch_data_from_db_for_command(self)

        BUDGET = 100000
        MAX_GENERATIONS = 30
        POPULATION_SIZE = 20

        # is_locked_by_status: An event is truly "locked" if it's completed or canceled.
        # These events will not be optimized by the GA (they are in fixed_events).
        # We keep this for clarity, though it's mainly used to categorize fixed_events.
        def is_locked_by_status(event): 
            return event['completed'] or event['is_canceled']

        # This function now creates a random initial solution ONLY for optimizable_events.
        def create_solution_for_optimizable_events():
            solution = [-1] * len(optimizable_events) 
            schedule_slots_taken = {}

            # First, populate the schedule with fixed events to avoid conflicts
            for event in fixed_events:
                loc_id = event['location_id']
                loc = next((l for l in locations if l['id'] == loc_id), None)
                if loc: # Only consider if the original location actually exists
                    # Check type compatibility for fixed events (important for schedule tracking)
                    if all(t_id in loc['accepted_types'] for t_id in event['type_ids']):
                        event_date_key = (loc_id, event['date'])
                        # Only add if not already taken by another fixed event (though rare if initial data is clean)
                        if event_date_key not in schedule_slots_taken:
                            schedule_slots_taken[event_date_key] = event['id']
                # If a fixed event had an invalid original assignment or no location, it doesn't block a slot.
                # Penalties for this are handled in the fitness function.

            # Now, try to assign optimizable events randomly
            for i, event in enumerate(optimizable_events):
                valid_and_available_locs = []
                for loc in locations:
                    if all(event_type_id in loc['accepted_types'] for event_type_id in event['type_ids']):
                        if (loc['id'], event['date']) not in schedule_slots_taken:
                            valid_and_available_locs.append(loc['id'])
                if valid_and_available_locs:
                    chosen_loc_id = random.choice(valid_and_available_locs)
                    solution[i] = chosen_loc_id
                    schedule_slots_taken[(chosen_loc_id, event['date'])] = event['id']
                else:
                    solution[i] = -1 # No valid and available location found for this optimizable event
            return solution

        # The fitness function evaluates the profit/cost/penalties of the *entire* schedule,
        # combining fixed events and the proposed solution for optimizable events.
        def fitness(solution_for_optimizable):
            total_profit = 0
            total_cost = 0
            penalty = 0
            location_daily_availability = {} # Tracks slots taken across ALL events
            infeasible_event_details = []

            # First, incorporate fixed events into the schedule and calculate their contribution
            for event in fixed_events:
                loc_id = event['location_id']
                loc = next((l for l in locations if l['id'] == loc_id), None)

                if loc: # If the fixed event has an assigned location
                    # Check type compatibility for fixed events
                    if not all(t_id in loc['accepted_types'] for t_id in event['type_ids']):
                        penalty += 5000 # Penalty for type mismatch in a fixed event's original assignment
                        infeasible_event_details.append(f"Fixed Event {event['name']} (ID: {event['id']}) - Type mismatch with original location {loc['name']}")
                    
                    event_date_key = (loc['id'], event['date'])
                    if event_date_key in location_daily_availability:
                        penalty += 50000 # High penalty for date conflict in fixed event's original assignment
                        infeasible_event_details.append(f"Fixed Event {event['name']} (ID: {event['id']}) - Date conflict at {loc['name']} on {event['date']} with Event {location_daily_availability[event_date_key]}")
                    else:
                        location_daily_availability[event_date_key] = event['id']
                        total_cost += loc['cost']
                        total_profit += event['cost'] # Assuming event['cost'] is profit
                else: # If a fixed event was unassigned or had an invalid original location
                    penalty += 5000 # Penalty for an unassigned fixed event
                    infeasible_event_details.append(f"Fixed Event {event['name']} (ID: {event['id']}) - Original location {loc_id} not found or invalid/unassigned!")


            # Then, evaluate optimizable events based on the proposed solution
            for i, loc_id in enumerate(solution_for_optimizable):
                event = optimizable_events[i] # Get the current optimizable event from its list

                if loc_id == -1: # Optimizable event could not be assigned in this solution
                    penalty += 5000 
                    infeasible_event_details.append(f"Optimizable Event {event['name']} (ID: {event['id']}) - No valid location assigned (-1 ID)")
                    continue

                loc = next((l for l in locations if l['id'] == loc_id), None)
                if not loc: # Should not happen if repair_solution works, but as a safeguard
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
                    location_daily_availability[event_date_key] = event['id'] # Mark slot as taken

                total_cost += loc['cost']
                total_profit += event['cost']

            # Budget constraint penalty
            if total_cost > BUDGET:
                penalty += (total_cost - BUDGET) * 2

            fit_val = total_profit - total_cost - penalty

            # Debugging output for problematic solutions
            if fit_val <= 0 and infeasible_event_details: # Only print debug for truly problematic solutions
                self.stdout.write(self.style.WARNING(f"\n--- DEBUG: Fitness Calculation for current solution ---"))
                self.stdout.write(self.style.WARNING(f"Total Profit: {total_profit}"))
                self.stdout.write(self.style.WARNING(f"Total Cost: {total_cost}"))
                self.stdout.write(self.style.WARNING(f"Total Penalties: {penalty}"))
                self.stdout.write(self.style.WARNING(f"Calculated Fitness (Profit - Cost - Penalties): {total_profit - total_cost - penalty}"))
                self.stdout.write(self.style.WARNING(f"Infeasibility Reasons ({len(infeasible_event_details)} issues):"))
                for detail in infeasible_event_details:
                    self.stdout.write(self.style.WARNING(f"    - {detail}"))
                self.stdout.write(self.style.WARNING(f"--- END DEBUG ---"))
                return 0 # Return 0 for invalid solutions so they are filtered out by selection
            return fit_val

        # Selects the best performing half of the population
        def select_population(population):
            graded = [(fitness(sol), sol) for sol in population]
            graded = [x for x in graded if x[0] > 0] # Filter out solutions with negative or zero fitness
            graded = sorted(graded, key=lambda x: x[0], reverse=True)
            return [x[1] for x in graded[:min(POPULATION_SIZE // 2, len(graded))]]

        # Applies a random mutation to a single assignment in a solution for optimizable events
        def mutate(solution_for_optimizable):
            mutated_solution = list(solution_for_optimizable)
            
            if not optimizable_events: # No events to mutate if list is empty
                return mutated_solution

            # Create a combined schedule including fixed events and current optimizable assignments
            # This is crucial to ensure mutations don't cause conflicts with fixed events or other optimizable events
            current_schedule = {}
            for event in fixed_events:
                loc_id = event['location_id']
                loc = next((l for l in locations if l['id'] == loc_id), None)
                if loc and all(t_id in loc['accepted_types'] for t_id in event['type_ids']):
                    event_date_key = (loc_id, event['date'])
                    current_schedule[event_date_key] = event['id']

            for idx, loc_id in enumerate(mutated_solution):
                event = optimizable_events[idx]
                loc = next((l for l in locations if l['id'] == loc_id), None)
                if loc and all(t_id in loc['accepted_types'] for t_id in event['type_ids']):
                    event_date_key = (loc_id, event['date'])
                    if event_date_key not in current_schedule: # Only add if not already taken by fixed
                        current_schedule[event_date_key] = event['id']

            # Choose a random optimizable event to mutate
            idx_to_mutate = random.choice(range(len(optimizable_events))) 
            event_to_mutate = optimizable_events[idx_to_mutate]
            original_loc_id_of_mutated = mutated_solution[idx_to_mutate]

            # Temporarily remove the event's current assignment from the schedule for re-assignment
            if original_loc_id_of_mutated != -1:
                event_date_key = (original_loc_id_of_mutated, event_to_mutate['date'])
                if event_date_key in current_schedule and current_schedule[event_date_key] == event_to_mutate['id']:
                    del current_schedule[event_date_key]

            # Find all valid and available locations for the event being mutated
            available_valid_locs = []
            for loc in locations:
                if all(event_type_id in loc['accepted_types'] for event_type_id in event_to_mutate['type_ids']):
                    if (loc['id'], event_to_mutate['date']) not in current_schedule:
                        available_valid_locs.append(loc['id'])

            if available_valid_locs:
                mutated_solution[idx_to_mutate] = random.choice(available_valid_locs)
            else:
                mutated_solution[idx_to_mutate] = -1 # No valid and available location found for this mutation
            return mutated_solution

        # Combines parts of two parent solutions to create two offspring solutions
        def crossover(sol1, sol2):
            if len(sol1) < 2: # Not enough events for a meaningful crossover
                return list(sol1), list(sol2)
            pos = random.randint(1, len(sol1) - 1) # Crossover point

            child1 = list(sol1[:pos]) + list(sol2[pos:])
            child2 = list(sol2[:pos]) + list(sol1[pos:])
            
            # Since we are operating only on optimizable_events, no specific handling for "locked" events is needed here.
            # The repair_solution step will ensure overall validity after crossover.
            return child1, child2

        # Repairs a solution by ensuring all assignments are valid and free of conflicts
        def repair_solution(solution_to_repair):
            repaired_solution = list(solution_to_repair)
            schedule_slots_taken = {} # To track taken slots across all events
            
            # First, add fixed events to the schedule (they are immutable)
            for event in fixed_events:
                loc_id = event['location_id']
                loc = next((l for l in locations if l['id'] == loc_id), None)
                if loc: # Only add if location exists and types match for fixed events
                    if all(t_id in loc['accepted_types'] for t_id in event['type_ids']):
                        event_date_key = (loc_id, event['date'])
                        if event_date_key not in schedule_slots_taken:
                            schedule_slots_taken[event_date_key] = event['id']
            
            # Iterate through optimizable events (sorted by ID for consistent repair order)
            optimizable_event_indices_sorted = sorted(range(len(optimizable_events)), key=lambda i: optimizable_events[i]['id'])

            for i in optimizable_event_indices_sorted:
                event = optimizable_events[i]
                current_assigned_loc_id = repaired_solution[i]
                loc_candidate = next((l for l in locations if l['id'] == current_assigned_loc_id), None)

                is_valid_current_assignment = False
                # Check if the current assignment is valid and available (type match, no date conflict)
                if loc_candidate and all(t_id in loc_candidate['accepted_types'] for t_id in event['type_ids']):
                    event_date_key = (loc_candidate['id'], event['date'])
                    if event_date_key not in schedule_slots_taken:
                        schedule_slots_taken[event_date_key] = event['id']
                        is_valid_current_assignment = True

                if not is_valid_current_assignment:
                    # If current assignment is invalid, find an alternative
                    valid_and_available_alternatives = []
                    for alt_loc in locations:
                        if all(event_type_id in alt_loc['accepted_types'] for event_type_id in event['type_ids']):
                            if (alt_loc['id'], event['date']) not in schedule_slots_taken:
                                valid_and_available_alternatives.append(alt_loc['id'])

                    if valid_and_available_alternatives:
                        chosen_alt_loc = random.choice(valid_and_available_alternatives)
                        repaired_solution[i] = chosen_alt_loc
                        schedule_slots_taken[(chosen_alt_loc, event['date'])] = event['id']
                    else:
                        repaired_solution[i] = -1 # Still no valid and available alternative
            return repaired_solution
        
        # Initial population generation for optimizable events
        population = [repair_solution(create_solution_for_optimizable_events()) for _ in range(POPULATION_SIZE)]

        # Main genetic algorithm loop
        for gen in range(MAX_GENERATIONS):
            population = select_population(population)

            # Handle cases where selection might drastically reduce population size
            if len(population) < 2:
                # Reinitialize a portion or all of the population if it's too small
                num_to_add = POPULATION_SIZE - len(population)
                if num_to_add > 0:
                    population.extend([repair_solution(create_solution_for_optimizable_events()) for _ in range(num_to_add)])
                if len(population) < 2 and POPULATION_SIZE >= 2: # Ensure we have at least 2 for crossover
                    self.stdout.write(self.style.WARNING(f"Warning: Population size fell below 2 in generation {gen+1}. Reinitializing entire population."))
                    population = [repair_solution(create_solution_for_optimizable_events()) for _ in range(POPULATION_SIZE)]
                elif len(population) < 2: # If POPULATION_SIZE itself is less than 2, this will still be true
                    break # Cannot perform crossover if less than 2 individuals

            offspring = []
            while len(offspring) + len(population) < POPULATION_SIZE:
                # Ensure there are enough parents for random.sample
                if len(population) < 2:
                    break # Cannot perform crossover if fewer than 2 parents are available

                parents = random.sample(population, 2)
                child1, child2 = crossover(parents[0], parents[1])
                offspring.append(repair_solution(mutate(child1)))
                if len(offspring) + len(population) < POPULATION_SIZE:
                    offspring.append(repair_solution(mutate(child2)))

            population.extend(offspring)
            population = [repair_solution(sol) for sol in population] # Re-repair after population growth

            # Get and display fitness for the best solution in current generation
            if population:
                best_fit_sol = max(population, key=fitness)
                self.stdout.write(f"Gen {gen+1} best fitness: {fitness(best_fit_sol)}")
            else:
                self.stdout.write(self.style.WARNING(f"Gen {gen+1}: No valid solutions in population. Best fitness: N/A"))
                break # Break if no valid solutions remain

        # Final best solution selection (from the last generation's population)
        best_solution_for_optimizable = []
        if population:
            best_solution_for_optimizable = repair_solution(max(population, key=fitness))
        
        # Create a dictionary to easily map optimizable event IDs to their assigned location in the best solution
        optimizable_assignments = {
            optimizable_events[i]['id']: best_solution_for_optimizable[i]
            for i in range(len(optimizable_events))
        }

        self.stdout.write(self.style.SUCCESS("\nBest solution assignment:\n"))
        
        # Report for ALL events, differentiating between fixed and optimized
        for original_event_idx, event in enumerate(all_events_for_report):
            event_types_names = [types[t_id] for t_id in event['type_ids']]
            organizer_display = event['organized_by'].get_full_name() or event['organized_by'].username if event['organized_by'] else 'N/A'

            # Determine if this event was part of the optimizable set or fixed
            if not event['completed'] and not event['is_canceled'] and event['date'] > date.today():
                # This was an optimizable event, get its new assignment
                assigned_loc_id = optimizable_assignments.get(event['id'], -1)
                loc_note = ""
            else:
                # This was a fixed event (completed, canceled, or past date)
                # It retains its original location, or -1 if it never had one or it was invalid
                assigned_loc_id = event['location_id']
                loc_note = " (fixed)" # Indicate it wasn't optimized

            loc = next((l for l in locations if l['id'] == assigned_loc_id), None)

            self.stdout.write(f"Event: {event['name']} (types: {event_types_names}, profit: {event['cost']}, date: {event['date']}, old organizer: {organizer_display})")
            
            if assigned_loc_id == -1 or not loc:
                self.stdout.write(self.style.WARNING(f"    => No valid location found or assigned!{loc_note}\n"))
            else:
                location_accepted_types_names = [types[t_id] for t_id in loc['accepted_types']]
                assigned_owner_display = loc['owner'].get_full_name() or loc['owner'].username if loc['owner'] else 'N/A'
                self.stdout.write(f"    => Assigned to: {loc['name']} (cost: {loc['cost']}, accepted_types: {location_accepted_types_names}, owner: {assigned_owner_display})")
                self.stdout.write(f"    => New organizer: {assigned_owner_display}{loc_note}\n") # New organizer is the assigned location's owner

        self.stdout.write(self.style.SUCCESS('Event optimization completed.'))