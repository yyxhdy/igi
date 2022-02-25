import random
import sys
from inspect import isclass
from infra.util import evade
from deap import gp
from infra.util import timeout, split_integer


def gen_rnd_depth_tree(min_depth, max_depth, pr_set, type_=None, mode="Half"):
    d_list = list(range(min_depth, max_depth + 1))

    while True:
        if len(d_list) == 0:
            raise ValueError(f"No valid trees with depth in [{min_depth}, {max_depth}]")

        depth = random.choice(d_list)
        tree = gen_fixed_depth_tree(depth, pr_set, type_, mode, min_=min_depth)
        if tree is not None:
            return tree
        else:
            d_list.remove(depth)


def gen_fixed_depth_tree(depth, pr_set, type_=None, mode="Half", min_=2):
    try:
        return gen_fixed_depth_tree_e(depth, pr_set, type_, mode, min_)
    except TimeoutError:
        return None


@timeout(1)
def gen_fixed_depth_tree_e(depth, pr_set, type_=None, mode="Half", min_=2):
    return evade(gen_fixed_depth_tree_b)(depth, pr_set, type_, mode, min_)


def gen_fixed_depth_tree_b(depth, pr_set, type_=None, mode="Half", min_=2):
    if type_ is None:
        type_ = pr_set.ret

    if mode not in ["Full", "Grow", "Half"]:
        raise ValueError("Mode must be one of \"Half\", \"Grow\", or \"Full\"")

    if mode == "Half":
        mode = random.choice(["Full", "Grow"])

    expr = []
    stack = [(0, type_)]
    while len(stack) != 0:
        dep, type_ = stack.pop()
        l1, l2 = len(pr_set.primitives[type_]), len(pr_set.terminals[type_])

        if dep == depth or (mode == "Grow" and dep >= min_ and random.random() < l2 / (l1 + l2)):
            try:
                term = random.choice(pr_set.terminals[type_])
            except IndexError:
                _, _, traceback = sys.exc_info()
                raise IndexError("The gp.generate function tried to add " \
                                 "a terminal of type '%s', but there is " \
                                 "none available." % (type_,)).with_traceback(traceback)
            if isclass(term):
                term = term()
            expr.append(term)
        else:
            try:
                prim = random.choice(pr_set.primitives[type_])
            except IndexError:
                _, _, traceback = sys.exc_info()
                raise IndexError("The gp.generate function tried to add " \
                                 "a primitive of type '%s', but there is " \
                                 "none available." % (type_,)).with_traceback(traceback)
            expr.append(prim)
            for arg in reversed(prim.args):
                stack.append((dep + 1, arg))

    return gp.PrimitiveTree(expr)


def gen_rnd_size_trees(min_size, max_size, num_trees, pr_set, type_=None):
    s_list = list(range(min_size, max_size + 1))
    tree_list = []

    while len(tree_list) < num_trees:
        if len(s_list) == 0:
            raise ValueError(f"No valid trees with size in [{min_size}, {max_size}]")

        size = random.choice(s_list)
        tree = gen_fixed_size_tree(size, pr_set, type_)
        if tree is not None:
            tree_list.append(tree)
        else:
            s_list.remove(size)
    return tree_list


def gen_rnd_size_tree(min_size, max_size, pr_set, type_=None):
    s_list = list(range(min_size, max_size + 1))

    while True:
        if len(s_list) == 0:
            raise ValueError(f"No valid trees with size in [{min_size}, {max_size}]")

        size = random.choice(s_list)
        tree = gen_fixed_size_tree(size, pr_set, type_)
        if tree is not None:
            return tree
        else:
            s_list.remove(size)


def gen_fixed_size_tree(size, pr_set, type_=None):
    try:
        return gen_fixed_size_tree_e(size, pr_set, type_)
    except TimeoutError:
        return None


@timeout(0.05)
def gen_fixed_size_tree_e(size, pr_set, type_=None):
    return evade(gen_fixed_size_tree_b)(size, pr_set, type_)


def gen_fixed_size_tree_b(size, pr_set, type_=None):
    if type_ is None:
        type_ = pr_set.ret

    expr = []
    stack = [(size, type_)]

    while len(stack) != 0:
        size, type_ = stack.pop()

        if size == 1:
            try:
                term = random.choice(pr_set.terminals[type_])
            except IndexError:
                _, _, traceback = sys.exc_info()
                raise IndexError("The gp.generate function tried to add " 
                                 "a terminal of type '%s', but there is " 
                                 "none available." % (type_,)).with_traceback(traceback)
            if isclass(term):
                term = term()
            expr.append(term)
        else:
            try:
                pr_list = pr_set.primitives[type_]
                pr_list = [pr for pr in pr_list if size > pr.arity]
                prim = random.choice(pr_list)
            except IndexError:
                _, _, traceback = sys.exc_info()
                raise IndexError("The gp.generate function tried to add "
                                 "a primitive of type '%s', but there "
                                 "is none available." % (type_,)).with_traceback(traceback)
            expr.append(prim)

            len_list = split_integer(size - 1, prim.arity)

            for s, arg in zip(len_list, reversed(prim.args)):
                stack.append((s, arg))

    return gp.PrimitiveTree(expr)


# localize subtrees in a tree
def subtree_localization(tree):
    n = len(tree)
    if n == 0:
        return

    ends = [-1] * n
    stack = [[0, tree[0].arity]]

    cp = 1
    while len(stack) != 0:
        if stack[-1][1] == 0:
            x = stack.pop()
            start = x[0]
            ends[start] = cp
            if len(stack) != 0:
                stack[-1][1] -= 1
        else:
            stack.append([cp, tree[cp].arity])
            cp += 1

    tree.ends = ends
