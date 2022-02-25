import random
from itergi.po import gen_random_edit


def uniform_mut2(pt, tree, pr_set):
    size = len(pt)
    pt_ = []

    for edit in pt:
        if random.random() < 1.0 / size:
            k = random.randrange(0, 2)
            if k == 1:
                edit_ = gen_random_edit(tree, pr_set)
                pt_.extend([edit, edit_])
        else:
            pt_.append(edit)

    if len(pt_) != 0:
        return pt_
    else:
        return pt


def uniform_mut(pt, tree, pr_set):
    size = len(pt)
    pt_ = []

    for edit in pt:
        if random.random() < 1.0 / size:
            k = random.randrange(0, 3)
            if k > 0:
                edit_ = gen_random_edit(tree, pr_set)
                if k == 1:
                    pt_.append(edit_)
                elif k == 2:
                    pt_.extend([edit, edit_])
        else:
            pt_.append(edit)

    if len(pt_) != 0:
        return pt_
    else:
        return pt

