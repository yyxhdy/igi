import random


def select_best(patches, k, maximize):
    patches = sorted(patches, key=lambda x: -x[0] if maximize else x[0])
    return patches[0:k]


def select_tournament(patches, k, tn_size, maximize):
    chosen = []
    for i in range(k):
        aspirants = [random.choice(patches) for _ in range(tn_size)]
        func = max if maximize else min
        chosen.append(func(aspirants, key=lambda x: x[0]))
    return chosen
