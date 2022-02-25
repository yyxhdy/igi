from deap import gp
import json


def head(xs):
    return xs[0] if len(xs) > 0 else None


def last(xs):
    return xs[-1] if len(xs) > 0 else None


def take(n, xs):
    return xs[:n]


def drop(n, xs):
    return xs[n:]


def access(n, xs):
    return xs[n] if n is not None and len(xs) > n >= 0 else None


def maximum(xs):
    return max(xs) if len(xs) > 0 else None


def minimum(xs):
    return min(xs) if len(xs) > 0 else None


def reverse(xs):
    return list(reversed(xs))


def sort(xs):
    return sorted(xs)


def sum_(xs):
    return sum(xs)


def map_(f, xs):
    return [f(x) for x in xs]


def filter_(f, xs):
    return [x for x in xs if f(x)]


def count(f, xs):
    return len([x for x in xs if f(x)])


def zipwith(f, xs, ys):
    return [f(x, y) for (x, y) in zip(xs, ys)]


def scanl1(f, xs):
    if len(xs) == 0:
        return xs
    n = len(xs)
    ys = [0] * n
    ys[0] = xs[0]
    for i in range(1, n):
        ys[i] = f(ys[i - 1], xs[i])

    return ys


def map_a1(xs):
    return map_(lambda x: x + 1, xs)


def map_m1(xs):
    return map_(lambda x: x - 1, xs)


def map_t2(xs):
    return map_(lambda x: x * 2, xs)


def map_t3(xs):
    return map_(lambda x: x * 3, xs)


def map_t4(xs):
    return map_(lambda x: x * 4, xs)


def map_d2(xs):
    return map_(lambda x: x // 2, xs)


def map_d3(xs):
    return map_(lambda x: x // 3, xs)


def map_d4(xs):
    return map_(lambda x: x // 4, xs)


def map_v1(xs):
    return map_(lambda x: -x, xs)


def map_p2(xs):
    return map_(lambda x: x ** 2, xs)


def filter_g0(xs):
    return filter_(lambda x: x > 0, xs)


def filter_l0(xs):
    return filter_(lambda x: x < 0, xs)


def filter_even(xs):
    return filter_(lambda x: x % 2 == 0, xs)


def filter_odd(xs):
    return filter_(lambda x: x % 2 == 1, xs)


def count_g0(xs):
    return count(lambda x: x > 0, xs)


def count_l0(xs):
    return count(lambda x: x < 0, xs)


def count_even(xs):
    return count(lambda x: x % 2 == 0, xs)


def count_odd(xs):
    return count(lambda x: x % 2 == 1, xs)


def zipwith_sum(xs, ys):
    return zipwith(lambda x, y: x + y, xs, ys)


def zipwith_diff(xs, ys):
    return zipwith(lambda x, y: x - y, xs, ys)


def zipwith_mul(xs, ys):
    return zipwith(lambda x, y: x * y, xs, ys)


def zipwith_max(xs, ys):
    return zipwith(lambda x, y: max(x, y), xs, ys)


def zipwith_min(xs, ys):
    return zipwith(lambda x, y: min(x, y), xs, ys)


def scanl1_sum(xs):
    return scanl1(lambda x, y: x + y, xs)


def scanl1_diff(xs):
    return scanl1(lambda x, y: x - y, xs)


def scanl1_mul(xs):
    return scanl1(lambda x, y: x * y, xs)


def scanl1_max(xs):
    return scanl1(lambda x, y: max(x, y), xs)


def scanl1_min(xs):
    return scanl1(lambda x, y: min(x, y), xs)


def get_primitive_set(arg_types, ret_type):
    pr_set = gp.PrimitiveSetTyped("main", arg_types, ret_type)

    pr_set.addPrimitive(head, [list], int, name="HEAD")
    pr_set.addPrimitive(last, [list], int, name="LAST")
    pr_set.addPrimitive(take, [int, list], list, name="TAKE")
    pr_set.addPrimitive(drop, [int, list], list, name="DROP")
    pr_set.addPrimitive(access, [int, list], int, name="ACCESS")
    pr_set.addPrimitive(minimum, [list], int, name="MINIMUM")
    pr_set.addPrimitive(maximum, [list], int, name="MAXIMUM")
    pr_set.addPrimitive(reverse, [list], list, name="REVERSE")
    pr_set.addPrimitive(sort, [list], list, name="SORT")
    pr_set.addPrimitive(sum, [list], int, name="SUM")

    pr_set.addPrimitive(map_a1, [list], list, name="MAPA1")
    pr_set.addPrimitive(map_m1, [list], list, name="MAPM1")
    pr_set.addPrimitive(map_t2, [list], list, name="MAPT2")
    pr_set.addPrimitive(map_t3, [list], list, name="MAPT3")
    pr_set.addPrimitive(map_t4, [list], list, name="MAPT4")
    pr_set.addPrimitive(map_d2, [list], list, name="MAPD2")
    pr_set.addPrimitive(map_d3, [list], list, name="MAPD3")
    pr_set.addPrimitive(map_d4, [list], list, name="MAPD4")
    pr_set.addPrimitive(map_v1, [list], list, name="MAPV1")
    pr_set.addPrimitive(map_p2, [list], list, name="MAPP2")

    pr_set.addPrimitive(filter_g0, [list], list, name="FILG0")
    pr_set.addPrimitive(filter_l0, [list], list, name="FILL0")
    pr_set.addPrimitive(filter_even, [list], list, name="FILEV")
    pr_set.addPrimitive(filter_odd, [list], list, name="FILOD")

    pr_set.addPrimitive(count_g0, [list], int, name="COUG0")
    pr_set.addPrimitive(count_l0, [list], int, name="COUL0")
    pr_set.addPrimitive(count_even, [list], int, name="COUEV")
    pr_set.addPrimitive(count_odd, [list], int, name="COUOD")

    pr_set.addPrimitive(zipwith_sum, [list, list], list, name="ZIPSUM")
    pr_set.addPrimitive(zipwith_diff, [list, list], list, name="ZIPDIF")
    pr_set.addPrimitive(zipwith_mul, [list, list], list, name="ZIPMUL")
    pr_set.addPrimitive(zipwith_max, [list, list], list, name="ZIPMAX")
    pr_set.addPrimitive(zipwith_min, [list, list], list, name="ZIPMIN")

    pr_set.addPrimitive(scanl1_sum, [list], list, name="SCANSUM")
    pr_set.addPrimitive(scanl1_diff, [list], list, name="SCANDIF")
    pr_set.addPrimitive(scanl1_mul, [list], list, name="SCANMUL")
    pr_set.addPrimitive(scanl1_max, [list], list, name="SCANMAX")
    pr_set.addPrimitive(scanl1_min, [list], list, name="SCANMIN")

    return pr_set


def get_dsl_and_examples(path, n_examples=50):
    inputs = []
    outputs = []

    with open(path) as f:
        data = json.load(f)

    if data['examples'][0]['output'] is not None:
        ret_type = type(data['examples'][0]['output'])
    else:
        ret_type = int

    arg_types = []
    for x in data['examples'][0]['inputs']:
        if x is not None:
            arg_types.append(type(x))
        else:
            arg_types.append(int)

    n_examples = min(n_examples, len(data['examples']))

    for i in range(n_examples):
        in_data = data['examples'][i]['inputs']
        out_data = data['examples'][i]['output']

        inputs.append(in_data)
        outputs.append(out_data)

    return get_primitive_set(arg_types, ret_type), inputs, outputs



