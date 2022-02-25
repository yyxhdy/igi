import random
import time


def metropolis_hastings(toolbox, switch_prob=0.01, beta=0.5, max_size=100):
    def move(size):
        if size == 1:
            return size + 1
        elif size == max_size:
            return size - 1
        else:
            return random.choice([size - 1, size + 1])

    start_time = time.time()

    n_eval = 0
    best_tree = None

    cur_list = {}
    forbid_sizes = []

    n = 1
    while True:
        if n not in cur_list and n not in forbid_sizes:
            new_tree = toolbox.rnd_tree(n)
            if new_tree is None:
                forbid_sizes.append(n)
                continue

            toolbox.eval_tree(new_tree)
            cur_list[n] = new_tree
            n_eval += 1

            if toolbox.is_better(best_tree, cur_list[n]):
                best_tree = new_tree
                toolbox.record_best(best_tree, start_time, n_eval)
        elif n in cur_list:
            new_tree, = toolbox.mutate(cur_list[n])
            toolbox.eval_tree(new_tree)
            n_eval += 1

            if toolbox.acc_criterion(cur_list[n], new_tree, beta):
                cur_list[n] = new_tree
                if toolbox.is_better(best_tree, cur_list[n]):
                    best_tree = cur_list[n]
                    toolbox.record_best(best_tree, start_time, n_eval)
        else:
            n = move(n)
            continue

        if random.random() <= switch_prob:
            n = move(n)

        if toolbox.stop_criterion(best_tree, start_time, n_eval):
            return best_tree
