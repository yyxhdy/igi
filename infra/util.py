import sys
import random
import time
import math
import errno
import os
import signal
from functools import wraps
import textdistance


# evade the Index Errors
def evade(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args,**kwargs)
            except IndexError:
                pass
    return wrapper


# timeout decorator
def timeout(seconds=0.001, error_message=os.strerror(errno.ETIME)):
    def decorate(function):
        def handler(signum, frame):
            raise TimeoutError(error_message)

        @wraps(function)
        def new_function(*args, **kwargs):
            new_seconds = kwargs.pop('timeout', seconds)
            if new_seconds:
                old = signal.signal(signal.SIGALRM, handler)
                signal.setitimer(signal.ITIMER_REAL, new_seconds)

            if not seconds:
                return function(*args, **kwargs)

            try:
                return function(*args, **kwargs)
            finally:
                if new_seconds:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    signal.signal(signal.SIGALRM, old)
        return new_function

    return decorate


# compile an expression, return the executable function and the code (as string)
def compile_expr(expr, pr_set):
    code = str(expr)
    if len(pr_set.arguments) > 0:
        args = ",".join(arg for arg in pr_set.arguments)
        code = "lambda {args}: {code}".format(args=args, code=code)
    try:
        return eval(code, pr_set.context, {}), code
    except MemoryError:
        _, _, traceback = sys.exc_info()
        raise MemoryError(("DEAP : Error in tree evaluation :"
                            " Python cannot evaluate a tree higher than 90. "
                            "To avoid this problem, you should use bloat control on your "
                            "operators. See the DEAP documentation for more information. "
                            "DEAP will now abort."), traceback)


# negative tournament, used in TinyGP
def neg_tournament(population, tournsize):
    indexes = random.choices(range(len(population)), k=tournsize)

    w_id = indexes[0]
    w_fit = population[w_id].fitness

    for i in range(1, len(indexes)):
        cur_id = indexes[i]
        cur_fit = population[cur_id].fitness
        if cur_fit < w_fit:
            w_fit, w_id = cur_fit, cur_id

    return w_id


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


# the stop criterion of the algorithm
def stop_criterion(best_ind, start_time, n_eval, opt_fit, time_limit, max_eval, stop_at_opt, out_path=None):
    elapsed_time = time.time() - start_time

    cond1 = stop_at_opt and best_ind.fit == opt_fit
    cond2 = time_limit is not None and elapsed_time >= time_limit
    cond3 = max_eval is not None and n_eval >= max_eval

    if cond1 or cond2 or cond3:
        if out_path is not None:
            save_costs_info(elapsed_time, n_eval, out_path)
        return True

    return False


# save the consumed time and evaluations at the end
def save_costs_info(elapsed_time, n_eval, out_path):
    info = "Time: " + str(elapsed_time) + "\t" + "Eval: " + str(n_eval) + "\n"
    with open(out_path, "a+") as out_file:
        out_file.write(info)
        out_file.close()


# save the best or the optimal program to file
def save_best(best_ind, out_path):
    info = str(best_ind.time) + " : " + str(best_ind.eval) + " : " + \
           str(best_ind.fit) + " : " + str(best_ind) + " : " + \
           str(best_ind.height) + " : " + str(len(best_ind)) + "\n"
    with open(out_path, "a+") as out_file:
        out_file.write(info)
        out_file.close()


# record the current best found program and (optional) save it to the file
def record_best(best_ind, start_time, n_eval, opt_fit, only_save_opt=True, out_path=None):
    best_ind.time = time.time() - start_time
    best_ind.eval = n_eval

    if out_path is not None:
        if only_save_opt:
            if best_ind.fit == opt_fit:
                save_best(best_ind, out_path)
        else:
            save_best(best_ind, out_path)


# record the current best found program and (optional) save it to the file, used for MH algorithm
def record_best2(best_ind, start_time, n_eval, opt_fit, normalize, n_examples,
                 only_save_opt=True, out_path=None):
    def save_best2(b_ind, o_path):
        fit = b_ind.fit if normalize else b_ind.fit / n_examples
        info = str(b_ind.time) + " : " + str(b_ind.eval) + " : " + \
               str(fit) + " : " + str(b_ind) + " : " + \
               str(b_ind.height) + " : " + str(len(b_ind)) + "\n"
        with open(o_path, "a+") as o_file:
            o_file.write(info)
            o_file.close()

    best_ind.time = time.time() - start_time
    best_ind.eval = n_eval

    if out_path is not None:
        if only_save_opt:
            if best_ind.fit == opt_fit:
                save_best2(best_ind, out_path)
        else:
            save_best2(best_ind, out_path)


# split an integer to the sum of k integers
def split_integer(n, k):
    res = []
    for i in range(k - 1):
        remain = n - (k - 1 - i)
        s = random.randint(1, remain)
        res.append(s)
        n -= s

    res.append(n)
    return res


# acceptance criterion used in simulated annealing
def acc_criterion_sa(cur_tree, new_tree, cur_temp, maximize=True):
    delta = new_tree.fit - cur_tree.fit
    if not maximize:
        delta = -delta

    if delta > 0 or (delta == 0 and len(new_tree) < len(cur_tree)):
        return True
    elif delta == 0:
        return True
    else:
        prob = math.exp(delta / cur_temp)
        if random.random() < prob:
            return True
        else:
            return False


# acceptance criterion used in iterated hill climbing
def acc_criterion_ihc(cur_tree, new_tree, maximize=True):
    delta = new_tree.fit - cur_tree.fit
    if not maximize:
        delta = -delta

    return delta > 0 or (delta == 0 and len(new_tree) < len(cur_tree))


# acceptance criterion used in metropolis-hasting
def acc_criterion_mh(cur_tree, new_tree, beta, maximize=True):
    delta = new_tree.fit - cur_tree.fit
    if not maximize:
        delta = -delta

    if delta >= 0:
        return True
    else:
        prob = math.exp(beta * delta)
        return random.random() < prob


def sim_func_lisp(out_, out):
    if out != out_:
        return 0
    else:
        return 1


def sim_func_int(out_, out):
    d = abs(out - out_)
    return 1 - d / (d + 1)


def sim_func_slia(out_, out):
    if len(out_) == 0 or len(out) == 0:
        return 0
    d = textdistance.levenshtein.normalized_similarity(out_, out)
    return d


