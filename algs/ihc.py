import time


def iterated_hill_climb(toolbox, max_mut, init_tree=None):
    start_time = time.time()

    cur_tree = toolbox.rnd_tree() if init_tree is None else init_tree
    toolbox.eval_tree(cur_tree)
    n_eval = 1

    best_tree = cur_tree
    toolbox.record_best(best_tree, start_time, n_eval)

    while True:
        if toolbox.stop_criterion(best_tree, start_time, n_eval):
            return best_tree

        toolbox.preprocessing(cur_tree)
        k = 0
        while k < max_mut:
            new_tree, = toolbox.mutate(cur_tree)
            toolbox.eval_tree(new_tree)
            n_eval += 1

            if toolbox.acc_criterion(cur_tree, new_tree):
                cur_tree = new_tree
                break
            k += 1

        if k == max_mut:
            cur_tree = toolbox.rnd_tree()
            toolbox.eval_tree(cur_tree)
            n_eval += 1

        if toolbox.is_better(best_tree, cur_tree):
            best_tree = cur_tree
            toolbox.record_best(best_tree, start_time, n_eval)


