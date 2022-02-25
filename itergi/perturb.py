import random
from infra.tree import gen_rnd_size_trees
from deap import gp


def perturbation_l(tree, toolbox, best_tree, start_time, n_eval, pr_set, min_size=3, num=200):
    node_ids = []
    for i in range(len(tree)):
        sl = tree.searchSubtree(i)
        start, stop = sl.start, sl.stop
        k = stop - start
        if k >= min_size:
            node_ids.append((i, start, stop))

    if len(node_ids) != 0:
        sid, start, stop = random.choice(node_ids)
    if len(node_ids) == 0 or sid == 0:
        st_tree, other_eval = toolbox.init_tree(toolbox, best_tree, start_time)
        n_eval += other_eval

        if toolbox.is_better(best_tree, st_tree):
            best_tree = st_tree

        return st_tree, best_tree, n_eval
    else:
        size = stop - start
        low, up = 1, size
        st_tree = None
        rp_tree_list = gen_rnd_size_trees(low, up, num, pr_set, tree[sid].ret)

        for rp_tree in rp_tree_list:
            new_tree = tree[0:start] + rp_tree + tree[stop:]
            new_tree = gp.PrimitiveTree(new_tree)
            toolbox.evaluate_tree(new_tree)
            n_eval += 1

            if toolbox.is_better(best_tree, new_tree):
                best_tree = new_tree
                toolbox.record_best(best_tree, start_time, n_eval)

            if new_tree.code != tree.code and toolbox.is_better(st_tree, new_tree):
                st_tree = new_tree

            if toolbox.stop_criterion(best_tree, start_time, n_eval):
                break

        return st_tree, best_tree, n_eval




