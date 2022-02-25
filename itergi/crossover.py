import random


def concat_cx(pt1, pt2):
    return pt1 + pt2, None


def one_point_cx_ratio(pt1, pt2):
    alpha = random.random()
    cp1 = int(alpha * len(pt1))
    cp2 = int(alpha * len(pt2))

    pt1[cp1:], pt2[cp2:] = pt2[cp2:], pt1[cp1:]
    return pt1, pt2


def one_point_cx_normal(pt1, pt2):
    cp1 = random.randrange(0, len(pt1))
    cp2 = random.randrange(0, len(pt2))
    pt1[cp1:], pt2[cp2:] = pt2[cp2:], pt1[cp1:]

    return pt1, pt2


def one_point_cx(pt1, pt2, mode='ratio'):
    if mode not in ["ratio", "normal"]:
        raise ValueError("Mode must be one of \"ratio\" or \"normal\"")

    if mode == 'ratio':
        return one_point_cx_ratio(pt1, pt2)
    else:
        return one_point_cx_normal(pt1, pt2)


