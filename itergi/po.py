import random
from infra.edit import gen_node_repl, gen_branch_ins, gen_branch_shr, is_edit_compatible
import numpy as np


def gen_random_patches(num, tree, pr_set):
    patches = []
    for _ in range(num):
        length = 1 + np.random.poisson(1)
        #length = 1
        patch = [gen_random_edit(tree, pr_set) for _ in range(length)]
        patches.append(patch)
    return patches


def gen_patch(length, tree, pr_set):
    patch = [gen_random_edit(tree, pr_set) for _ in range(length)]
    return patch


def gen_random_edit(tree, pr_set):
    locations = range(len(tree))

    edit_types = ['NodeRepl', 'BranchIns', 'BranchShr']
    edit = None

    while edit is None:
        loc = random.choice(locations)
        e_type = random.choice(edit_types)

        if e_type == "NodeRepl":
            edit = gen_node_repl(tree, loc, pr_set)
        elif e_type == "BranchIns":
            edit = gen_branch_ins(tree, loc, pr_set)
        elif e_type == "BranchShr":
            edit = gen_branch_shr(tree, loc)
        else:
            raise ValueError("Edit type must be one of \"NodeRep\", \"BranchIns\" or \"BranchShr\"")

    return edit


def extend_patch(patch, tree, pr_set):
    while True:
        edit = gen_random_edit(tree, pr_set)
        if is_edit_compatible(patch, edit):
            new_patch = patch + [edit]
            return new_patch

