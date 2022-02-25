
def acc_criterion(cur_tree, new_tree, maximize=True):
    delta = new_tree.fit - cur_tree.fit
    if not maximize:
        delta = -delta

    return delta >= 0

