import random, json_handle, policy_eval
from policy_op import gen_individual_multi, my_initRepeat, mut_policy_multi, get_prev_policy
from policy_op import gen_individual_directed, mut_policy_directed, gen_individual_ack, mut_policy_ack
from deap import tools, base, creator
from operator import attrgetter
from pathlib import Path
import itertools
import json
import os, shutil
import time
# create class - first: name, second: base, rest params: variable and values
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)      # policy set class

toolbox = base.Toolbox()

# register a function in the toolbox with alias.
# first: alias, second: method, rest params: arguments

# toolbox.register("individual", my_initRepeat, creator.Individual, gen_individual, max_size=10)
toolbox.register("prev_individual", get_prev_policy, creator.Individual)

toolbox.register("individual_ack", my_initRepeat, creator.Individual, gen_individual_ack)
toolbox.register("individual_multi", my_initRepeat, creator.Individual, gen_individual_multi)
toolbox.register("individual_d", my_initRepeat, creator.Individual, gen_individual_directed)

toolbox.register("population_ack", tools.initRepeat, list, toolbox.individual_ack)
toolbox.register("population_multi", tools.initRepeat, list, toolbox.individual_multi)
toolbox.register("population_d", tools.initRepeat, list, toolbox.individual_d)

toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate_ack", mut_policy_multi, m_portion=0.1)
toolbox.register("mutate_multi", mut_policy_multi, m_portion=0.1)
toolbox.register("mutate_d", mut_policy_directed, m_portion=0.1)
toolbox.register("select", tools.selTournament, tournsize=5)
toolbox.register("evaluate", policy_eval.evaluate)


def main(type_SoS):
    # Generate a population of 'policy_set'
    if os.path.exists("./simulation.log"):
        os.remove("./simulation.log")
    folder = './json/candidates'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

    print(">> Framework Start. SoS type: ", type_SoS)
    if type_SoS == "D":
        p_population = toolbox.population_d(n=20)
        prev_policy_file = Path("./json/candidates/prev_policy_D.json")
    elif type_SoS == "A":
        p_population = toolbox.population_ack(n=20)
        prev_policy_file = Path("./json/candidates/prev_policy_A.json")
    else:
        p_population = toolbox.population_multi(n=20)
        prev_policy_file = Path("./json/candidates/prev_policy_multi.json")
    print(">> Initial population is generated. Population size: ", len(p_population))

    if prev_policy_file.is_file():
        print("Previous policy file exists.")
        p_population.append(toolbox.prev_individual(filename=prev_policy_file))
        print("Finish reading a previous policy file. Add the end of the population.")

    CXPB, MUTPB, NGEN = 0.5, 0.2, 30
    # BEST_PORTION = 0.2
    POP = len(p_population)

    # Evaluate the entire population
    print(">> Evaluate the initial population.")
    # fitnesses = map(toolbox.evaluate, p_population)
    fitnesses = map(toolbox.evaluate, p_population, range(0, POP - 1), itertools.repeat(0, POP))
    for ind, fit in zip(p_population, fitnesses):
        ind.fitness.values = fit
    print(">> Finish the evaluation of the initial population.")
    best = []
    for g in range(NGEN):
        print("<<<<Generation: ", g, ">>>>")
        print("Population Length: ", len(p_population))
        # Select the next generation individuals
        # best_cand = sorted(p_population, key=attrgetter("fitness"), reverse=True)[0:int(POP*BEST_PORTION)]

        best_cand = sorted(p_population, key=attrgetter("fitness"), reverse=True)[0:1]
        # update best
        if g == 0:
            best = best_cand
        else:
            cand_fitness = best_cand[0].fitness.values[0]
            current_fitness = best[0].fitness.values[0]
            if cand_fitness > current_fitness:
                best = best_cand

        print("Best length: ", len(best))
        print("Current Best: ", best[0].fitness.values[0])
        print("Pop fits:", end=" ")
        print_fitness(p_population)
        print("Selection...")
        # offspring = toolbox.select(p_population, len(p_population)-int(POP*BEST_PORTION))
        offspring = toolbox.select(p_population, len(p_population))
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
                if type_SoS == "D":
                    toolbox.mutate_d(mutant)
                elif type_SoS == "A":
                    toolbox.mutate_ack(mutant)
                else:
                    toolbox.mutate_multi(mutant)
                del mutant.fitness.values
        print("Re-evaluation...")
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        # fitnesses = map(toolbox.evaluate, invalid_ind)
        fitnesses = map(toolbox.evaluate, invalid_ind, range(0, len(p_population)-1), itertools.repeat(g, len(invalid_ind)))
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        # The population is entirely replaced by the offspring
        p_population[:] = offspring

    p_population[:] = offspring + best
    print()
    print("Total length: ", len(p_population))
    return p_population


def print_fitness(individuals):
    s_individuals = sorted(individuals, key=attrgetter("fitness"), reverse=True)
    for ind in s_individuals:
        print(ind.fitness.values, "%", end=" ")
    print()


def print_individual(individuals):
    for ind in individuals:
        print("*", ind)


if __name__ == '__main__':
    start_time = time.clock()
    type_SoS = ""
    with open('./json/SoSproperties.json') as f:
        for line in f:
            while True:
                try:
                    SoS_properties = json.loads(line)
                    type_SoS = SoS_properties['typeSoS']
                    break
                except ValueError:
                    line += next(f)

    result_pop = main(type_SoS)

    for ind in result_pop:
        print(ind.fitness.values),

    s_inds = sorted(result_pop, key=attrgetter("fitness"), reverse=True)

    end_time = time.clock()
    running_time = end_time - start_time

    json_handle.make_policy_json("output_policy.json", s_inds[0])

    print("RESULT")
    print_fitness(s_inds)
    print("Total running time: ", running_time/100)
