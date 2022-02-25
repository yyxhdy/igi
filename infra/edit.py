import random
from inspect import isclass
from deap import gp


# data structure for the edit in a patch
class Edit(object):
    def __init__(self, type_, loc, rps):
        self.type = type_   # type of the edit
        self.loc = loc      # the location the edit to be applied
        self.rps = rps      # replacements


def gen_node_repl(tree, loc, pr_set):
    node = tree[loc]

    if node.arity == 0:
        t_list = pr_set.terminals[node.ret]
        p_list = get_rep_primitives(node.ret, pr_set)

        lt, lp = len(t_list), len(p_list)

        index = random.randrange(0, lt + lp)
        if index < lt:
            term = t_list[index]
            if isclass(term):
                term = term()
            rp = [term]
        else:
            prim = p_list[index - lt]
            rp = gen_prim_call(prim, pr_set)
    else:
        prim_list = [p for p in pr_set.primitives[node.ret] if is_arg_compatible(p.args, node.args)]
        rp = [random.choice(prim_list)]

    rps = (loc, loc + 1, rp),
    return Edit("NodeRepl", loc, rps)


# generate a "BranchShr" edit at a specified loc
def gen_branch_shr(tree, loc):
    node = tree[loc]
    if not isinstance(node, gp.Primitive):
        return None

    indexes = []
    k = loc + 1
    for _ in range(node.arity):
        if issubclass(tree[k].ret, node.ret):
            indexes.append(k)

        k = tree.ends[k]

    if len(indexes) == 0:
        return None

    index = random.choice(indexes)

    end = tree.ends[loc]
    if tree.ends[index] != end:
        rps = (loc, index, []), (tree.ends[index], end, [])
    else:
        rps = (loc, index, []),

    return Edit("BranchShr", loc, rps)


# generate a "BranchIns" edit at a specified loc
def gen_branch_ins(tree, loc, pr_set):
    node = tree[loc]
    primitives = pr_set.primitives[node.ret]
    p_dir = {}
    for i in range(len(primitives)):
        p = primitives[i]
        arg_ids = []

        for k in range(len(p.args)):
            type_ = p.args[k]
            if issubclass(node.ret, type_):
                arg_ids.append(k)

        if len(arg_ids) != 0:
            p_dir[i] = arg_ids

    if len(p_dir) == 0:
        return None

    k = random.choice(list(p_dir))
    new_node = primitives[k]
    arg_id = random.choice(p_dir[k])

    pre_rp = [new_node]
    post_rp = []
    for i, arg_type in enumerate(new_node.args):
        if i == arg_id:
            continue

        terminals = pr_set.terminals[arg_type]

        if len(terminals) != 0:
            tn = random.choice(terminals)
            if isclass(tn):
                tn = tn()
            tn = [tn]
        else:
            prim_list = get_rep_primitives(arg_type, pr_set)
            prim = random.choice(prim_list)
            tn = gen_prim_call(prim, pr_set)

        if i < arg_id:
            pre_rp.extend(tn)
        elif i > arg_id:
            post_rp.extend(tn)

    end = tree.ends[loc]

    if len(post_rp) != 0:
        rps = (loc, loc, pre_rp), (end, end, post_rp)
    else:
        rps = (loc, loc, pre_rp),

    return Edit("BranchIns", loc, rps)


# merge branch insertions at the same location
def get_merged_ins(ins1, ins2):
    rp_l = ins2.rps[0][2] + ins1.rps[0][2]

    if len(ins1.rps) == 1 and len(ins2.rps) == 1:
        rps = (ins1.loc, ins1.loc, rp_l),
    elif len(ins1.rps) == 1:
        rps = (ins1.loc, ins1.loc, rp_l), ins2.rps[1]
    elif len(ins2.rps) == 1:
        rps = (ins1.loc, ins1.loc, rp_l), ins1.rps[1]
    else:
        rp_r = ins1.rps[1][2] + ins2.rps[1][2]
        rps = (ins1.loc, ins1.loc, rp_l), (ins1.rps[1][0], ins1.rps[1][1], rp_r)

    return Edit(ins1.type, ins1.loc, rps)


# randomly generate an edit to a program tree
def gen_rnd_edit(tree, pr_set, edit_types, type_weights=None,
                 locations=None, loc_weights=None):
    if locations is None:
        locations = range(len(tree))

    edit = None
    while edit is None:
        loc = random.choices(locations, loc_weights)[0]
        e_type = random.choices(edit_types, type_weights)[0]

        if e_type == "NodeRepl":
            edit = gen_node_repl(tree, loc, pr_set)
        elif e_type == "BranchIns":
            edit = gen_branch_ins(tree, loc, pr_set)
        elif e_type == "BranchShr":
            edit = gen_branch_shr(tree, loc)
        else:
            raise ValueError("Edit type must be one of \"NodeRep\", \"BranchIns\" or \"BranchShr\"")

    return edit


# judge whether two replacements is conflict or not
def is_conflict_rp(rp1, rp2):
    if rp2[0] >= rp1[1] or rp2[1] <= rp1[0]:
        return False
    return True


# judge whether a BranchIns and BranchShr is conflict or not
def is_conflict_edit_is(edit1, edit2):
    cond1 = (edit1.type == "BranchIns" and edit2.type == "BranchShr")
    cond2 = (edit1.type == "BranchShr" and edit2.type == "BranchIns")

    if not cond1 and not cond2:
        return False

    if cond1:
        bi, bs = edit1, edit2
    else:
        bi, bs = edit2, edit1

    if len(bs.rps) < 2:
        return False

    if bi.rps[0][0] != bs.rps[1][0]:
        return False

    return True


# judge whether two edits are conflict or not
def is_conflict_edit(edit1, edit2):
    if is_conflict_edit_is(edit1, edit2):
        return True

    for rp1 in edit1.rps:
        for rp2 in edit2.rps:
            if is_conflict_rp(rp1, rp2):
                return True
    return False


# judge whether the edit is compatible to all existing edits in a patch
def is_edit_compatible(patch, edit):
    for x in patch:
        if is_conflict_edit(x, edit):
            return False

    return True


# apply a NodeRepl edit
def apply_node_repl(edit, tree):
    loc = edit.loc
    rp = edit.rps[0][2]

    new_tree = tree[0:loc] + rp + tree[loc + 1:]
    return gp.PrimitiveTree(new_tree)


# apply a BranchShr edit
def apply_branch_shr(edit, tree):
    l1 = edit.rps[0][0]
    l2 = edit.rps[0][1]

    if len(edit.rps) == 1:
        new_tree = tree[0:l1] + tree[l2:]
    else:
        l3 = edit.rps[1][0]
        l4 = edit.rps[1][1]
        new_tree = tree[0:l1] + tree[l2:l3] + tree[l4:]

    return gp.PrimitiveTree(new_tree)


# apply a BranchIns edit
def apply_branch_ins(edit, tree):
    l1 = edit.rps[0][0]
    rp1 = edit.rps[0][2]

    if len(edit.rps) == 1:
        new_tree = tree[0:l1] + rp1 + tree[l1:]
    else:
        l2 = edit.rps[1][0]
        rp2 = edit.rps[1][2]
        new_tree = tree[0:l1] + rp1 + tree[l1:l2] + rp2 + tree[l2:]

    return gp.PrimitiveTree(new_tree)


# apply an edit to a program tree
def apply_edit(edit, tree):
    if edit.type == "NodeRepl":
        return apply_node_repl(edit, tree)
    elif edit.type == "BranchShr":
        return apply_branch_shr(edit, tree)
    else:
        return apply_branch_ins(edit, tree)


# every argtype in args should be the parent (or the same) type in corr. org_args
def is_arg_compatible(args, org_args):
    if len(args) != len(org_args):
        return False

    for t, org_t in zip(args, org_args):
        if not issubclass(org_t, t):
            return False

    return True


# judge whether there is a terminal with the corr. type for each arg (not include k) in args
def has_terminal(pr_set, args, *ignore_ids):
    for i in range(len(args)):
        if i in ignore_ids:
            continue
        terms = pr_set.terminals[args[i]]
        if len(terms) == 0:
            return False
    return True


def get_rep_primitives(ret, pr_set):
    p_list = []
    for prim in pr_set.primitives[ret]:
        #if not is_insertable(prim) and has_terminal(pr_set, prim.args):
        if has_terminal(pr_set, prim.args):
            p_list.append(prim)
    return p_list


def gen_prim_call(prim, pr_set):
    p_call = [prim]
    for arg_type in prim.args:
        terms = pr_set.terminals[arg_type]
        term = random.choice(terms)
        if isclass(term):
            term = term()
        p_call.append(term)
    return p_call


def is_insertable(prim):
    for type_ in prim.args:
        if issubclass(prim.ret, type_):
            return True

    return False



