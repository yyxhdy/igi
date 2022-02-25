from deap import gp
import json


class Bool(object):
    pass


def concat(s1, s2):
    return s1 + s2


def str_at(s, i):
    if 0 <= i < len(s):
        return s[i]
    else:
        return ""


def sub_str(s, i, n):
    if n < 0 or i < 0 or i >= len(s):
        return ""
    else:
        return s[i:(i + n)]


def str_rep(s, t1, t2):
    return s.replace(t1, t2, 1)


def str_len(s):
    return len(s)


def index_of(s, t, i):
    if len(s) > i >= 0 and t in s[i:]:
        return s.index(t, i)
    else:
        return -1


def prefix_of(s, t):
    return t.startswith(s)


def suffix_of(s, t):
    return t.endswith(s)


def contains(s, t):
    return t in s


def str_to_int(s):
    if s.isdigit():
        return int(s)
    else:
        return -1


def int_to_str(z):
    if z < 0:
        return ""
    else:
        return str(z)


def addition(z1, z2):
    return z1 + z2


def subtraction(z1, z2):
    return z1 - z2


def equal(z1, z2):
    return z1 == z2


def ite(cond, x, y):
    return x if cond else y


prim_map = {"CAT": (concat, [str, str], str),
            "REP": (str_rep, [str, str, str], str),
            "AT": (str_at, [str, int], str),
            "ITS": (int_to_str, [int], str),
            "SITE": (ite, [Bool, str, str], str),
            "SUBSTR": (sub_str, [str, int, int], str),
            "ADD": (addition, [int, int], int),
            "SUB": (subtraction, [int, int], int),
            "LEN": (str_len, [str], int),
            "STI": (str_to_int, [str], int),
            "IITE": (ite, [Bool, int, int], int),
            "IND": (index_of, [str, str, int], int),
            "EQ": (equal, [int, int], Bool),
            "PRF": (prefix_of, [str, str], Bool),
            "SUF": (suffix_of, [str, str], Bool),
            "CONT": (contains, [str, str], Bool)}


def get_primitive_set(arg_types, ret_type, primitives=None, terminals=None):
    pr_set = gp.PrimitiveSetTyped("main", arg_types, ret_type)
    add = pr_set.addPrimitive

    if primitives is None:
        primitives = prim_map.keys()

    for prim in primitives:
        # print(prim)
        add(prim_map[prim][0], prim_map[prim][1], prim_map[prim][2], prim)

    if terminals is not None:
        i = 0
        for term, type_ in terminals:
            i += 1
            t_name = "T" + str(i)
            if not callable(term):
                pr_set.addTerminal(term, type_, t_name)
            else:
                pr_set.addEphemeralConstant(t_name, term, type_)

    return pr_set


def get_dsl_and_examples(path, n_examples=50):
    inputs = []
    outputs = []

    with open(path) as f:
        data = json.load(f)

    def type_func(t):
        type_ = type(t)
        if type_ == bool:
            return Bool
        else:
            return type_

    ret_type = type_func(data['examples'][0]['output'])
    #print(type(data['examples'][0]['output']))

    arg_types = []
    for x in data['examples'][0]['inputs']:
        arg_types.append(type_func(x))

    n_examples = min(n_examples, len(data['examples']))

    for i in range(n_examples):
        in_data = data['examples'][i]['inputs']
        out_data = data['examples'][i]['output']

        inputs.append(in_data)
        outputs.append(out_data)

    terminals = []
    if data['terminals'] is not None:
        for term in data['terminals']:
            type_ = type_func(term)
            terminals.append((term, type_))

    return get_primitive_set(arg_types, ret_type, data['primitives'], terminals), inputs, outputs



