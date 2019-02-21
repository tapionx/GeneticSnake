import random
import numpy as np
import nn
import snake
from operator import attrgetter

POPULATION_SIZE = 500
PARENTS_POOL_SIZE = 5
MUTATION_COUNT = 10
MUTATION_PROBABILITY = 0.20
WAIT = 300
FPS = 1000

# COLORS
class colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    BLUE = '\033[34m'
    END = '\033[0m'

def initial_population():
    population = []
    for _ in range(0, POPULATION_SIZE):
        population.append(nn.NeuralNetwork())
    return population

def calculate_fitness(population):
    game = snake.Game()
    for _ in population:
        game.snakes.append(snake.Snake(snake.CELL_COUNT/2, snake.CELL_COUNT/2, 5))

    count = 0
    while count < WAIT:
        game.render()
        for i in range(len(population)):
            distance, angle = game.snakes[i].observe_apple()
            obstacle_front, obstacle_right, obstacle_left = game.snakes[i].observe_obstacle()
            inputs = [distance, angle, obstacle_front, obstacle_right, obstacle_left]
            action = np.argmax(population[i].compute_outputs(inputs))
            if action == 1:
                game.snakes[i].turn_right()
            elif action == 2:
                game.snakes[i].turn_left()
        best = max(game.snakes, key=attrgetter('score'))
        old_apple = best.apple
        game.update(FPS)
        game.stop = True
        for s in game.snakes:
            if not s.dead:
                game.stop = False
        if game.stop:
            break
        best = max(game.snakes, key=attrgetter('score'))
        if old_apple is not best.apple:
            count = 0
        count += 1
    fitness = []
    for s in game.snakes:
        fitness.append(s.score)
    game.end()
    return fitness

def select_parents(population, fitness, pool_size):
    sorted_index = list(np.argsort(fitness)[::-1])
    parents = []
    parents_fitness = []
    for i in range(pool_size):
        parents.append(population[sorted_index[i]])
        parents_fitness.append(fitness[sorted_index[i]])
    return parents, parents_fitness

def crossover(mother, father):
    offspring = nn.NeuralNetwork()
    for i in range(len(offspring.weights)):
        if random.random() >= 0.5:
            offspring.weights[i] = mother.weights[i]
        else:
            offspring.weights[i] = father.weights[i]
    return offspring

def mutate(offspring):
    mutations = random.randint(1, MUTATION_COUNT)
    mutating_index = random.sample(range(len(offspring.weights)), mutations)
    for i in mutating_index:
        offspring.weights[i] = random.random()*2 - 1
    return offspring

def genetic_algorithm(population):
    fitness = calculate_fitness(population)
    parents_pool, parents_fitness = select_parents(population, fitness, PARENTS_POOL_SIZE)
    print(colors.BOLD + colors.GREEN + "Generation fitness: " + colors.END + colors.BOLD + str(np.average(parents_fitness)))
    print(colors.END)
    next_population = parents_pool
    mutations = 0
    while len(next_population) < POPULATION_SIZE:
        parents = random.sample(parents_pool, 2)
        mother = parents[0]
        father = parents[1]
        offspring = crossover(mother, father)
        if random.random() < MUTATION_PROBABILITY:
            mutations += 1
            next_population.append(mutate(offspring))
        else:
            next_population.append(offspring)
    print(colors.BOLD + colors.BLUE + "Mutation percentage: " +
            colors.END + colors.BOLD + "%.2f%%" % ((mutations/POPULATION_SIZE)*100))
    print(colors.END, end='')
    return next_population[:POPULATION_SIZE]

if __name__ == '__main__':
    population = initial_population()
    generation = 0
    while True:
        generation += 1
        print(colors.BOLD)
        print('{:-^100}'.format(' Generation # ' + colors.YELLOW + str(generation) + ' ' + colors.END + colors.BOLD))
        print(colors.END)
        next_population = genetic_algorithm(population)
        population = next_population