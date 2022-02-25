import time
import random


def tiny_gp(toolbox, pop_size, crossover_prob):
    start_time = time.time()

    pop = toolbox.population(n=pop_size)
    n_eval = 0

    best_ind = None

    for ind in pop:
        fit = toolbox.evaluate(ind)
        ind.fitness.values = fit
        n_eval += 1

        if toolbox.is_better(best_ind, ind):
            best_ind = ind
            toolbox.record_best(best_ind, start_time, n_eval)

        if toolbox.stop_criterion(best_ind, start_time, n_eval):
            return best_ind

    while True:
        for i in range(pop_size):
            parents = toolbox.tournament(pop)
            if random.random() < crossover_prob:
                parent1 = toolbox.clone(parents[0])
                parent2 = toolbox.clone(parents[1])
                offspring, _ = toolbox.mate(parent1, parent2)
            else:
                parent = toolbox.clone(parents[0])
                offspring, = toolbox.mutate(parent)

            del offspring.fitness.values
            fit = toolbox.evaluate(offspring)
            n_eval += 1

            offspring.fitness.values = fit

            index = toolbox.neg_tournament(pop)
            pop[index] = offspring

            if toolbox.is_better(best_ind, offspring):
                best_ind = offspring
                toolbox.record_best(best_ind, start_time, n_eval)

            if toolbox.stop_criterion(best_ind, start_time, n_eval):
                return best_ind
