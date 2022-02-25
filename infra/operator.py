import random
from inspect import isclass
from deap import gp
from infra.edit import apply_edit, is_arg_compatible
from infra.tree import gen_fixed_size_tree


def uniform_cx(ind1, ind2):
    ind1_ = [x for x in (ind1 + ind2) if random.random() < 0.5]
    ind2_ = [x for x in (ind2 + ind1) if random.random() < 0.5]

    ind_type = type(ind1)

    if len(ind1_) != 0:
        ind1 = ind_type(ind1_)
    if len(ind2_) != 0:
        ind2 = ind_type(ind2_)

    return ind1, ind2


def one_point_cx_ratio(ind1, ind2):
    alpha = random.random()
    cp1 = int(alpha * len(ind1))
    cp2 = int(alpha * len(ind2))

    ind1[cp1:], ind2[cp2:] = ind2[cp2:], ind1[cp1:]
    return ind1, ind2


def one_point_cx_normal(ind1, ind2):
    cp1 = random.randrange(0, len(ind1))
    cp2 = random.randrange(0, len(ind2))
    ind1[cp1:], ind2[cp2:] = ind2[cp2:], ind1[cp1:]

    return ind1, ind2


def one_point_cx(ind1, ind2, mode='ratio'):
    if mode not in ["ratio", "normal"]:
        raise ValueError("Mode must be one of \"ratio\" or \"normal\"")

    if mode == 'ratio':
        return one_point_cx_ratio(ind1, ind2)
    else:
        return one_point_cx_normal(ind1, ind2)


def uniform_mut(ind, toolbox):
    size = len(ind)
    ind_ = type(ind)()

    for edit in ind:
        if random.random() < 1.0 / size:
            k = random.randrange(0, 3)
            if k > 0:
                edit_ = toolbox.edit()
                if k == 1:
                    ind_.append(edit_)
                elif k == 2:
                    ind_.extend([edit, edit_])
        else:
            ind_.append(edit)

    if len(ind_) != 0:
        return ind_,
    else:
        return ind,


def point_mut(individual, prob, pr_set):
    for index in range(len(individual)):
        if random.random() >= prob:
            continue

        node = individual[index]

        if node.arity == 0:  # Terminal
            term = random.choice(pr_set.terminals[node.ret])
            if isclass(term):
                term = term()
            individual[index] = term
        else:  # Primitive
            prim_list = [p for p in pr_set.primitives[node.ret] if is_arg_compatible(p.args, node.args)]
            individual[index] = random.choice(prim_list)

    return individual,


# generate an random edit, and apply it to the tree
def hvl_mut(tree, rand_edit):
    while True:
        edit = rand_edit(tree)
        new_tree = apply_edit(edit, tree)
        if edit.type != "NodeRepl" or new_tree[edit.loc] != tree[edit.loc]:
            break

    return new_tree,


def mh_mut(tree, pr_set):
    index = random.randrange(len(tree))

    sl = tree.searchSubtree(index)
    start, stop = sl.start, sl.stop
    size = stop - start

    rp_tree = gen_fixed_size_tree(size, pr_set, tree[index].ret)
    if rp_tree is None:
        return tree,

    new_tree = tree[0:start] + rp_tree + tree[stop:]
    return gp.PrimitiveTree(new_tree),

