import random
from typing import Dict, List, Tuple

def fitness_function(schedule: List[str], ratings: Dict[str, List[float]]) -> float:
    """Sum the rating of the assigned program at each of the 18 time slots."""
    return sum(ratings[program][slot] for slot, program in enumerate(schedule))

def initialize_population(programs: List[str], population_size: int, chromosome_length: int,
                          rng: random.Random) -> List[List[str]]:
    """Create schedules with one program assignment for each time slot."""
    return [
        [rng.choice(programs) for _ in range(chromosome_length)]
        for _ in range(population_size)
    ]

def crossover(parent1: List[str], parent2: List[str], rng: random.Random) -> Tuple[List[str], List[str]]:
    """Single-point crossover. Repeated programs are allowed in this scheduling problem."""
    point = rng.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

def mutate(schedule: List[str], programs: List[str], rng: random.Random) -> List[str]:
    """Replace one time-slot assignment with a randomly selected program."""
    mutated = schedule.copy()
    point = rng.randrange(len(mutated))
    mutated[point] = rng.choice(programs)
    return mutated

def select_parent(population: List[List[str]], ratings: Dict[str, List[float]],
                  rng: random.Random, tournament_size: int = 3) -> List[str]:
    """Tournament selection: return the fittest schedule among sampled candidates."""
    candidates = rng.sample(population, k=min(tournament_size, len(population)))
    return max(candidates, key=lambda item: fitness_function(item, ratings))

def run_genetic_algorithm(
    ratings: Dict[str, List[float]],
    generations: int = 100,
    population_size: int = 50,
    crossover_rate: float = 0.8,
    mutation_rate: float = 0.2,
    elitism_size: int = 2,
    seed: int = 42,
):
    programs = list(ratings.keys())
    chromosome_length = len(next(iter(ratings.values())))
    rng = random.Random(seed)

    if not programs:
        raise ValueError("The CSV does not contain any TV programs.")
    if any(len(values) != chromosome_length for values in ratings.values()):
        raise ValueError("Every program must have the same number of hourly ratings.")
    if population_size < 2:
        raise ValueError("Population size must be at least 2.")
    if not 1 <= elitism_size < population_size:
        raise ValueError("Elitism size must be between 1 and population size - 1.")

    population = initialize_population(programs, population_size, chromosome_length, rng)
    best_schedule = None
    best_rating = float("-inf")
    history = []

    for generation in range(generations + 1):
        population.sort(key=lambda item: fitness_function(item, ratings), reverse=True)
        generation_best = population[0]
        generation_rating = fitness_function(generation_best, ratings)

        if generation_rating > best_rating:
            best_schedule = generation_best.copy()
            best_rating = generation_rating

        history.append({
            "Generation": generation,
            "Best Rating": round(best_rating, 4),
        })

        if generation == generations:
            break

        new_population = [item.copy() for item in population[:elitism_size]]

        while len(new_population) < population_size:
            parent1 = select_parent(population, ratings, rng)
            parent2 = select_parent(population, ratings, rng)

            if rng.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2, rng)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            if rng.random() < mutation_rate:
                child1 = mutate(child1, programs, rng)
            if rng.random() < mutation_rate:
                child2 = mutate(child2, programs, rng)

            new_population.append(child1)
            if len(new_population) < population_size:
                new_population.append(child2)

        population = new_population

    return best_schedule, best_rating, history
