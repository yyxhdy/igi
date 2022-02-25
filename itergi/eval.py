from infra.edit import get_merged_ins
from infra.patch import extract_all_rps, execute_rps, resolve_conflicts
from deap import gp


def merge_branch_ins(patch):
    new_patch = []
    ins_dir = {}

    for edit in patch:
        if edit.type != "BranchIns":
            new_patch.append(edit)
            continue

        loc = edit.loc
        if loc in ins_dir:
            index = ins_dir[loc][0]
            mg_ins = get_merged_ins(new_patch[index], edit)
            new_patch[index] = mg_ins
            ins_dir[loc][1] += 1
        else:
            ins_dir[loc] = [len(new_patch), 1]
            new_patch.append(edit)

    return new_patch


def execute_patch(patch, tree, resolve_conf=False):
    if len(patch) == 0:
        return tree

    patch = merge_branch_ins(patch)

    if resolve_conf:
        patch = resolve_conflicts(patch)

    all_rps = extract_all_rps(patch)
    new_tree = execute_rps(all_rps, tree)

    return gp.PrimitiveTree(new_tree)


def evaluate_tree(tree, toolbox, inputs, outputs, executor, maximize, normalize):
    wf = 0 if maximize else len(inputs)
    if normalize:
        wf /= len(inputs)

    routine, code = toolbox.compile(expr=tree)
    try:
        results = executor(routine, inputs, outputs)
        fit = sum(results)

        if not maximize:
            fit = len(inputs) - fit
        if normalize:
            fit /= len(inputs)
        tree.fit, tree.code = fit, code

        return fit,
    except TimeoutError:
        tree.fit, tree.code = wf, None
        return wf,


def evaluate_patch(patch, tree, toolbox, inputs, outputs, executor, maximize, normalize, resolve_conf=False):
    new_tree = execute_patch(patch, tree, resolve_conf)
    wf = 0 if maximize else len(inputs)
    if normalize:
        wf /= len(inputs)

    routine, code = toolbox.compile(expr=new_tree)
    if code == tree.code:
        return wf, None

    try:
        results = executor(routine, inputs, outputs)
        fit = sum(results)

        if not maximize:
            fit = len(inputs) - fit
        if normalize:
            fit /= len(inputs)
        new_tree.fit, new_tree.code = fit, code

        return fit, new_tree
    except TimeoutError:
        return wf, None


