import time


def simulated_annealing(toolbox, t_start, t_end, step_size, init_tree=None):
    start_time = time.time()

    cur_tree = toolbox.rnd_tree() if init_tree is None else init_tree
    toolbox.eval_tree(cur_tree)
    n_eval = 1

    toolbox.preprocessing(cur_tree)

    best_tree = cur_tree
    cur_temp = t_start

    toolbox.record_best(best_tree, start_time, n_eval)

    cool_rate = pow(t_end / t_start, 1.0 / step_size)

    while True:
        if toolbox.stop_criterion(best_tree, start_time, n_eval):
            return best_tree

        new_tree, = toolbox.mutate(cur_tree)

        toolbox.eval_tree(new_tree)
        n_eval += 1

        if toolbox.acc_criterion(cur_tree, new_tree, cur_temp):
            cur_tree = new_tree
            toolbox.preprocessing(cur_tree)

            if toolbox.is_better(best_tree, cur_tree):
                best_tree = cur_tree
                toolbox.record_best(best_tree, start_time, n_eval)

        if n_eval % step_size == 0:
            cur_temp *= cool_rate
            if cur_temp < t_end:
                cur_temp = t_end
