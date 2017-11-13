import random, json_handle, policy_eval
from policy_op import gen_individual_all, my_initRepeat, mut_policy, get_prev_policy
from deap import tools, base, creator
from operator import attrgetter
import os
# create class - first: name, second: base, rest params: variable and values
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)      # policy set class

toolbox = base.Toolbox()

# register a function in the toolbox with alias.
# first: alias, second: method, rest params: arguments

# toolbox.register("individual", my_initRepeat, creator.Individual, gen_individual, max_size=10)
toolbox.register("individual", my_initRepeat, creator.Individual, gen_individual_all)
toolbox.register("prev_individual", get_prev_policy, creator.Individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", mut_policy, m_portion=0.1)           # NOTE mutate portion
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", policy_eval.evaluate)



def main():
    # Generate a population of 'policy_set'
    if os.path.exists("./simulation.log"):
        os.remove("./simulation.log")
    print(">> Framework Start.")
    p_population = toolbox.population(n=10)
    print(">> Initial population is generated. Population size: ", len(p_population))
    # prev_policy_file = Path("./json/previousPolicy.json")
    # if prev_policy_file.is_file():
    #     print("Previous policy file exists.")
    #     p_population.append(toolbox.prev_individual(filename=prev_policy_file))
    #     print("Finish reading a previous policy file.")

    CXPB, MUTPB, NGEN = 0.5, 0.2, 5

    # Evaluate the entire population
    print(">> Evaluate the initial population.")
    fitnesses = map(toolbox.evaluate, p_population)
    # fitnesses = map(toolbox.evaluate, p_population, range(0, len(p_population)-1), itertools.repeat(0, len(p_population)))
    for ind, fit in zip(p_population, fitnesses):
        ind.fitness.values = fit
    print(">> Finish the evaluation of the initial population.")
    for g in range(NGEN):
        print("<<<<Generation: ", g, ">>>>")
        # Select the next generation individuals
        best = sorted(p_population, key=attrgetter("fitness"), reverse=True)[0:10]
        print("Current Best: ", best[0].fitness.values)
        print("Selection...")
        offspring = toolbox.select(p_population, len(p_population)-10)
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))
        print("Crossover...")
        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            # [start:end:step]
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values
        print("Mutation...")
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        print("Re-evaluation...")
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        # fitnesses = map(toolbox.evaluate, invalid_ind, range(0, len(p_population)-1), itertools.repeat(g, len(invalid_ind)))
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        # The population is entirely replaced by the offspring
        p_population[:] = offspring+best

    return p_population


def print_fitness(individuals):
    for ind in individuals:
        print(ind.fitness.values,)


def print_individual(individuals):
    for ind in individuals:
        print("*", ind)

result_pop = main()
for ind in result_pop:
    print(ind.fitness.values)

s_inds = sorted(result_pop, key=attrgetter("fitness"), reverse=True)

json_handle.make_policy_json("output_policy.json", s_inds[0])

print("RESULT")
print_fitness(s_inds)