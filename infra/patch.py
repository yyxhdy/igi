import random
from deap import gp
from infra.edit import gen_rnd_edit, get_merged_ins, is_edit_compatible


# randomly generate a patch to a program tree
def gen_rnd_patch(tree, min_length, max_length, pr_set,
                  edit_types, type_weights=None,
                  locations=None, loc_weights=None):
    if locations is None:
        locations = range(len(tree))

    length = random.randint(min_length, max_length)
    patch = []

    for _ in range(length):
        edit = gen_rnd_edit(tree, pr_set, edit_types, type_weights, locations, loc_weights)
        patch.append(edit)

    return patch


# merge branch insertions at the same location in a patch
# max_ins is the maximum allowed number of insertions at a location
def merge_insertions(patch, max_ins):
    new_patch = []
    ins_dir = {}

    for edit in patch:
        if edit.type != "BranchIns":
            new_patch.append(edit)
            continue

        loc = edit.loc
        if loc in ins_dir:
            index = ins_dir[loc][0]
            count = ins_dir[loc][1]
            if count < max_ins:
                mg_ins = get_merged_ins(new_patch[index], edit)
                new_patch[index] = mg_ins
                ins_dir[loc][1] += 1
        else:
            ins_dir[loc] = [len(new_patch), 1]
            new_patch.append(edit)

    return new_patch


# resolve the conflicts between edits
def resolve_conflicts(patch):
    new_patch = []
    for edit in patch:
        if is_edit_compatible(new_patch, edit):
            new_patch.append(edit)

    return new_patch


# extract all replacements from a patch
def extract_all_rps(patch):
    all_rps = []
    ins_dir = {}

    for edit in patch:
        if edit.type != "BranchIns":
            all_rps.extend(edit.rps)
            continue

        if edit.loc in ins_dir:
            ins_dir[edit.loc].append((-1, edit.rps[0][2]))
        else:
            ins_dir[edit.loc] = [(-1, edit.rps[0][2])]

        if len(edit.rps) == 2:
            loc = edit.rps[1][0]
            if loc in ins_dir:
                ins_dir[loc].append((edit.loc, edit.rps[1][2]))
            else:
                ins_dir[loc] = [(edit.loc, edit.rps[1][2])]

    for loc in ins_dir:
        ins_dir[loc].sort(reverse=True)
        rps = []
        for _, rp in ins_dir[loc]:
            rps.extend(rp)

        all_rps.append((loc, loc, rps))

    all_rps.sort()
    return all_rps


# execute all replacements extracted from a patch
def execute_rps(all_rps, tree):
    new_tree = []
    j, k = 0, 0
    while k < len(all_rps):
        cur_id = all_rps[k][0]
        if j < cur_id:
            new_tree.append(tree[j])
            j += 1
        elif j == cur_id:
            new_tree.extend(all_rps[k][2])
            j = all_rps[k][1]
            k += 1

    if j < len(tree):
        new_tree.extend(tree[j:])

    return new_tree


# apply a patch to the program tree
def apply_patch(patch, tree, max_ins):
    if len(patch) == 0:
        return tree

    patch = merge_insertions(patch, max_ins)
    patch = resolve_conflicts(patch)

    all_rps = extract_all_rps(patch)
    new_tree = execute_rps(all_rps, tree)

    return gp.PrimitiveTree(new_tree)
