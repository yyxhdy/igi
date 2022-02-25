import time


def iterative_gen_imp(toolbox):
    start_time = time.time()
    st_tree, n_eval = toolbox.init_tree(toolbox, None, start_time)
    lb_tree, best_tree, n_eval = gi_search(st_tree, toolbox, st_tree, start_time, n_eval)

    while True:
        if toolbox.stop_criterion(best_tree, start_time, n_eval):
            return best_tree

        st_tree_, best_tree, n_eval = toolbox.perturbation(lb_tree, toolbox, best_tree, start_time, n_eval)

        if toolbox.stop_criterion(best_tree, start_time, n_eval):
            return best_tree

        lb_tree_, best_tree, n_eval = gi_search(st_tree_, toolbox, best_tree, start_time, n_eval)

        if toolbox.acc_criterion(lb_tree, lb_tree_):
            lb_tree = lb_tree_


def gi_search(st_tree, toolbox, best_tree, start_time, n_eval):
    cur_tree = st_tree
    while True:
        toolbox.pre_processing(cur_tree)

        next_tree, best_tree, n_eval = toolbox.gi_step(cur_tree, toolbox, best_tree, start_time, n_eval)

        if toolbox.is_better(cur_tree, next_tree):
            cur_tree = next_tree
            if toolbox.stop_criterion(best_tree, start_time, n_eval):
                return cur_tree, best_tree, n_eval
        else:
            return cur_tree, best_tree, n_eval


