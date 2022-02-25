import sys

import os
from deap import base
from deap import creator
from deap import tools
from deap import gp
import operator
from algs.tgp import tiny_gp
from infra.util import neg_tournament, is_better, stop_criterion, record_best, compile_expr, sim_func_slia, sim_func_lisp
from infra.operator import point_mut
from infra.tree import gen_rnd_depth_tree
from infra.eval import eval_tree, run_program
import dsl.lisp as lisp
import dsl.slia as slia
from functools import partial

data_root = "../dataset"
out_root = "../results/sa"

if __name__ == '__main__':
    prob_type, prob_name = sys.argv[1:3]

    # prob_type, prob_name = "slia", "bikes-long"
    # prob_type, prob_name = "lisp", "L100"

    MAXIMIZE = True
    NORMALIZE = True

    WEIGHT = 1.0 if MAXIMIZE else -1.0

    MIN_DEPTH = 2
    MAX_DEPTH = 4

    TIME_LIMIT = 3600
    MAX_EVAL = 300000000

    STOP_AT_OPT = True
    ONLY_SAVE_OPT = False

    POP_SIZE = 20000
    CROSSOVER_PROB = 0.9
    MUT_PER_NODE = 0.1
    TN_SIZE = 2

    PROB_PATH = os.path.join(data_root, prob_type + "/" + prob_name + ".json")
    if prob_type == "lisp":
        NUM_EXAMPLES = 100
        pr_set, inputs, outputs = lisp.get_dsl_and_examples(PROB_PATH, NUM_EXAMPLES)
        executor = partial(run_program, sim_func=sim_func_lisp)
    else:
        NUM_EXAMPLES = 1000
        pr_set, inputs, outputs = slia.get_dsl_and_examples(PROB_PATH, NUM_EXAMPLES)
        executor = partial(run_program, sim_func=sim_func_slia)

    OPT_FIT = len(inputs) if MAXIMIZE else 0
    if NORMALIZE:
        OPT_FIT /= len(inputs)

    creator.create("FitnessMax", base.Fitness, weights=(WEIGHT,))
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("expr", gen_rnd_depth_tree, MIN_DEPTH, MAX_DEPTH, pr_set)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", compile_expr, pr_set=pr_set)

    toolbox.register("evaluate", eval_tree, toolbox=toolbox, inputs=inputs, outputs=outputs,
                     executor=executor,
                     normalize=NORMALIZE, maximize=MAXIMIZE)

    toolbox.register("mate", gp.cxOnePoint)
    toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=30))

    toolbox.register("mutate", point_mut, prob=MUT_PER_NODE, pr_set=pr_set)

    toolbox.register("tournament", tools.selTournament, k=2, tournsize=TN_SIZE)
    toolbox.register("neg_tournament", neg_tournament, tournsize=TN_SIZE)

    toolbox.register("is_better", is_better, maximize=MAXIMIZE)

    toolbox.register("stop_criterion", stop_criterion,
                     opt_fit=OPT_FIT, time_limit=TIME_LIMIT, max_eval=MAX_EVAL, stop_at_opt=STOP_AT_OPT)

    OUT_PATH = os.path.join(out_root, prob_type + "/" + prob_name + ".txt")

    toolbox.register("record_best", record_best, opt_fit=OPT_FIT, only_save_opt=ONLY_SAVE_OPT,
                     out_path=OUT_PATH)

    best_tree = tiny_gp(toolbox, POP_SIZE, CROSSOVER_PROB)
    print(best_tree, best_tree.fitness.values)