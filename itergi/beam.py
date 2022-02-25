def beam_imp(tree, toolbox, best_tree, start_time, n_eval,
             beam_width=100, factor=10, max_len=3, first_imp=True, auto_imp=False):
    patches = [(0, [])] * beam_width

    local_best = None
    for k in range(1, max_len + 1):
        next_patches = []
        for i in range(0, beam_width):
            for j in range(0, factor):
                pt = toolbox.extend_patch(patches[i][1], tree)

                fit, new_tree = toolbox.evaluate_patch(pt, tree)
                n_eval += 1

                next_patches.append((fit, pt))

                if toolbox.is_better(local_best, new_tree):
                    local_best = new_tree

                    if toolbox.is_better(best_tree, new_tree):
                        if auto_imp and first_imp:
                            first_imp = False
                        best_tree = new_tree
                        toolbox.record_best(best_tree, start_time, n_eval)

                if first_imp and toolbox.is_strictly_better(tree, local_best):
                    return local_best, best_tree, n_eval

                if toolbox.stop_criterion(best_tree, start_time, n_eval):
                    return local_best, best_tree, n_eval

        patches = toolbox.select_patches(next_patches, beam_width)

    return local_best, best_tree, n_eval



