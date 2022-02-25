from infra.tree import gen_rnd_depth_tree


def best_init_tree_depth(toolbox, best_tree,
                         start_time, min_depth, max_depth, pr_set, num_trees):
    n_eval = 0
    cur_best_tree = None

    for _ in range(num_trees):
        tree = gen_rnd_depth_tree(min_depth, max_depth, pr_set, None, "Half")
        toolbox.evaluate_tree(tree)
        n_eval += 1

        if toolbox.is_better(cur_best_tree, tree):
            cur_best_tree = tree

        if toolbox.is_better(best_tree, tree):
            best_tree = tree
            toolbox.record_best(best_tree, start_time, n_eval)

        if toolbox.stop_criterion(best_tree, start_time, n_eval):
            break

    return cur_best_tree, n_eval






