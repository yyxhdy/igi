import random


# the comparison between programs
def is_better(ind1, ind2, maximize=True):
    if ind1 is None and ind2 is not None:
        return True
    elif ind1 is not None and ind2 is not None:
        fit1, fit2 = ind1.fit, ind2.fit
        if not maximize:
            fit1, fit2 = -fit1, -fit2
        if fit2 > fit1:
            return True
        elif fit2 == fit1 and len(ind2) < len(ind1):
            return True
    return False


def is_strictly_better(ind1, ind2, maximize=True):
    if ind1 is None and ind2 is not None:
        return True
    elif ind1 is not None and ind2 is not None:
        fit1, fit2 = ind1.fit, ind2.fit
        if not maximize:
            fit1, fit2 = -fit1, -fit2
        if fit2 > fit1:
            return True
        else:
            return False
    return False



