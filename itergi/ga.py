import random
import time


def genetic_imp(tree, toolbox, best_tree, start_time, n_eval,
                pop_size, max_gen, cx_prob, mut_prob, first_imp=True, auto_imp=False):
    patches = toolbox.rand_patches(pop_size, tree)

    local_best = None
    gen = 0
    while gen < max_gen:
        t1 = time.time()
        pop = []

        for pt in patches:
            fit, p_tree = toolbox.evaluate_patch(pt, tree)
            pop.append((fit, pt))
            n_eval += 1

            if toolbox.is_better(local_best, p_tree):
                local_best = p_tree
                if toolbox.is_better(best_tree, p_tree):
                    if auto_imp and first_imp:
                        first_imp = False
                    best_tree = p_tree
                    toolbox.record_best(best_tree, start_time, n_eval)

            if first_imp and toolbox.is_strictly_better(tree, local_best):
                return local_best, best_tree, n_eval

            if toolbox.stop_criterion(best_tree, start_time, n_eval):
                return local_best, best_tree, n_eval

        offsprings = [toolbox.clone(ind[1]) for ind in toolbox.select_patches(pop, pop_size)]

        for i in range(1, pop_size, 2):
            if random.random() < cx_prob:
                offsprings[i - 1], offsprings[i] = toolbox.crossover(offsprings[i - 1], offsprings[i])

        for i in range(pop_size):
            if random.random() < mut_prob:
                offsprings[i] = toolbox.mutate(offsprings[i], tree)

        patches[:] = offsprings

        gen += 1

    return local_best, best_tree, n_eval

