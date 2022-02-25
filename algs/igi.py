import random
import time
from deap import creator
from deap import tools


def iterated_gen_imp(toolbox, init_tree=None):
    start_time = time.time()

    st_tree = toolbox.rnd_tree() if init_tree is None else init_tree
    toolbox.eval_tree(st_tree)
    n_eval = 1

    toolbox.record_best(st_tree, start_time, n_eval)

    lb_tree, n_eval = gi_search(st_tree, toolbox, n_eval, start_time)
    best_tree = lb_tree
    toolbox.record_best(best_tree, start_time, n_eval)

    while True:
        if toolbox.stop_criterion(best_tree, start_time, n_eval):
            return best_tree

        st_tree_ = toolbox.perturbation(lb_tree)

        toolbox.eval_tree(st_tree_)
        n_eval += 1

        lb_tree_, n_eval = gi_search(st_tree_, toolbox, n_eval, start_time)

        lb_tree = lb_tree_

        if toolbox.is_better(best_tree, lb_tree_):
            best_tree = lb_tree_
            toolbox.record_best(best_tree, start_time, n_eval)


def gi_search(tree, toolbox, n_eval, start_time):
    cur_tree = tree
    while True:
        toolbox.preprocessing(cur_tree)

        toolbox.register("edit", toolbox.rnd_edit, cur_tree)
        toolbox.register("patch", toolbox.rnd_patch, toolbox.edit, cur_tree)
        toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.patch)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        new_tree, ne = toolbox.gi_step(cur_tree, toolbox)
        n_eval += ne

        cur_tree = new_tree

        if toolbox.stop_criterion(cur_tree, start_time, n_eval):
            return cur_tree, n_eval

        return cur_tree, n_eval


def gi_step(tree, toolbox, pop_size, cx_prob, mut_prob):
    pop = toolbox.population(n=pop_size)

    best_tree = None
    ne = 0

    for ind in pop:
        fit, p_tree = toolbox.evaluate(ind, tree)
        ind.fitness.values = fit
        ne += 1

        if toolbox.is_better(best_tree, p_tree)  and p_tree.fit != tree.fit:
            best_tree = p_tree

        if toolbox.is_gi_terminated(tree, best_tree, ne):
            return best_tree, ne

    g = 1
    while True:
        mat_pop = toolbox.select(pop, len(pop))
        offsprings = [toolbox.clone(ind) for ind in mat_pop]

        for i in range(1, len(offsprings), 2):
            if random.random() < cx_prob:
                offsprings[i - 1], offsprings[i] = toolbox.mate(offsprings[i - 1], offsprings[i])
                del offsprings[i - 1].fitness.values, offsprings[i].fitness.values

        for i in range(len(offsprings)):
            if random.random() < mut_prob:
                offsprings[i], = toolbox.mutate(offsprings[i])
                del offsprings[i].fitness.values

        for ind in offsprings:
            fit, p_tree = toolbox.evaluate(ind, tree)

            ind.fitness.values = fit
            ne += 1

            if toolbox.is_better(best_tree, p_tree) and p_tree.fit != tree.fit:
                best_tree = p_tree

            if toolbox.is_gi_terminated(tree, best_tree, ne):
                return best_tree, ne

        pop[:] = offsprings

        g += 1

