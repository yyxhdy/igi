from infra.patch import apply_patch
from infra.util import timeout


def exceed_static_limit(tree, max_depth, max_size):
    if max_depth is not None and tree.height > max_depth:
        return True

    if max_size is not None and len(tree) > max_size:
        return True

    return False


@timeout(0.05)
def run_program(routine, inputs, outputs, sim_func=None):
    results = []
    for in_, out in zip(inputs, outputs):
        out_ = routine(*in_)
        if out_ == out:
            results.append(True)
        else:
            if sim_func is None:
                results.append(False)
            else:
                results.append(sim_func(out_, out))

    return results


def eval_tree(tree, toolbox, inputs, outputs, executor=run_program,
              max_depth=None, max_size=None,
              maximize=True, normalize=False):
    wf = 0 if maximize else len(inputs)
    if normalize:
        wf /= len(inputs)

    if exceed_static_limit(tree, max_depth, max_size):
        tree.fit, tree.code = wf, None
        return wf,

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


def eval_patch(patch, tree, toolbox, inputs, outputs, executor=run_program,
               max_depth=None, max_size=None,
               maximize=True, normalize=False,
               max_ins=5):
    new_tree = apply_patch(patch, tree, max_ins)
    wf = 0 if maximize else len(inputs)
    if normalize:
        wf /= len(inputs)

    if exceed_static_limit(new_tree, max_depth, max_size):
        return (wf, ), None

    routine, code = toolbox.compile(expr=new_tree)
    if code == tree.code:
        return (wf, ), None

    try:
        results = executor(routine, inputs, outputs)

        fit = sum(results)
        if not maximize:
            fit = len(inputs) - fit
        if normalize:
            fit /= len(inputs)
        new_tree.fit, new_tree.code = fit, code

        return (fit, ), new_tree
    except TimeoutError:
        return (wf, ), None



