import random, json_handle, policy_eval
from policy_op import gen_individual, my_initRepeat, mut_policy, get_prev_policy
from deap import tools, base, creator
from pathlib import Path

# create class - first: name, second: base, rest params: variable and values
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)      # policy set class

toolbox = base.Toolbox()

# register a function in the toolbox with alias.
# first: alias, second: method, rest params: arguments
# policy set (10 will be the the number of polices in a policy set)
toolbox.register("individual", my_initRepeat, creator.Individual, gen_individual, max_size=10)
toolbox.register("prev_individual", get_prev_policy, creator.Individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", mut_policy, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", policy_eval.evaluate)


def main():
    # Generate a population of 'policy_set'
    p_population = toolbox.population(n=5)
    print("Population before read")
    for ind in p_population:
        print(ind)
    print("Population size: ", len(p_population))
    prev_policy_file = Path("./json/previousPolicy.json")
    if prev_policy_file.is_file():
        print("Previous policy file exists.")
        p_population.append(toolbox.prev_individual(filename=prev_policy_file))  # previous policy also has to be "individual" type
        print("Finish reading a previous policy file.")

    print("Population after read")
    for ind in p_population:
        print(ind)
    print("Updated population size: ", len(p_population))

    CXPB, MUTPB, NGEN = 0.5, 0.2, 5

    # Evaluate the entire population
    fitnesses = map(toolbox.evaluate, p_population)
    for ind, fit in zip(p_population, fitnesses):
        ind.fitness.values = fit

    for g in range(NGEN):
        # Select the next generation individuals
        offspring = toolbox.select(p_population, len(p_population))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))
        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            # [::] nothing for the first argument, nothing for the second, and jump by three
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # The population is entirely replaced by the offspring
        p_population[:] = offspring

    return p_population

result_pop = main()
for ind in result_pop:
    print(ind.fitness.values)