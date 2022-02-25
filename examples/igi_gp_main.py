import os
import sys
from deap import base

from infra.util import compile_expr, sim_func_slia, sim_func_lisp

from infra.eval import run_program
import dsl.lisp as lisp
import dsl.slia as slia
from functools import partial

from itergi.mutate import uniform_mut
from itergi.crossover import one_point_cx_normal

from itergi.compare import is_better, is_strictly_better
from itergi.select import select_tournament
from itergi.po import gen_random_patches
from itergi.eval import evaluate_patch, evaluate_tree
from itergi.preprocess import pre_processing
from itergi.stop import stop_criterion
from itergi.record import record_best
from itergi.framework import iterative_gen_imp
from itergi.ga import genetic_imp
from itergi.perturb import *
from itergi.acc import acc_criterion
from itergi.init import best_init_tree_depth


data_root = "../dataset"
out_root = "../results/igi_gp"


if __name__ == '__main__':
    prob_type, prob_name = sys.argv[1:3]
    # prob_type, prob_name = "slia", "bikes-long"
    # prob_type, prob_name = "lisp", "L100"

    MAXIMIZE = True
    NORMALIZE = True
    RESOLVE_CONF = True

    TIME_LIMIT = 3600
    MAX_EVAL = 300000000

    STOP_AT_OPT = True
    ONLY_SAVE_OPT = False

    MIN_DEPTH = 2
    MAX_DEPTH = 4

    CX_PROB = 1.0
    MUT_PROB = 1.0

    POP_SIZE = 100
    MAX_GEN = 5
    TN_SIZE = 2
    NUM = 200
    AUTO_IMP = True

    NUM_TREES = POP_SIZE * MAX_GEN

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

    edit_types = ["NodeRepl", "BranchShr", "BranchIns"]
    toolbox = base.Toolbox()

    toolbox.register("init_tree", best_init_tree_depth,
                     min_depth=MIN_DEPTH, max_depth=MAX_DEPTH, pr_set=pr_set,
                     num_trees=NUM_TREES)

    toolbox.register("is_better", is_better, maximize=MAXIMIZE)
    toolbox.register("is_strictly_better", is_strictly_better, maximize=MAXIMIZE)

    toolbox.register("compile", compile_expr, pr_set=pr_set)
    toolbox.register("evaluate_patch", evaluate_patch, toolbox=toolbox, inputs=inputs, outputs=outputs,
                     executor=executor, maximize=MAXIMIZE, normalize=NORMALIZE, resolve_conf=RESOLVE_CONF)
    toolbox.register("evaluate_tree", evaluate_tree, toolbox=toolbox, inputs=inputs, outputs=outputs,
                     executor=executor, maximize=MAXIMIZE, normalize=NORMALIZE)

    toolbox.register("crossover", one_point_cx_normal)
    toolbox.register("mutate", uniform_mut, pr_set=pr_set)

    toolbox.register("rand_patches", gen_random_patches, pr_set=pr_set)

    toolbox.register("select_patches", select_tournament, tn_size=TN_SIZE, maximize=MAXIMIZE)

    toolbox.register("pre_processing", pre_processing)
    toolbox.register("stop_criterion", stop_criterion,
                     opt_fit=OPT_FIT, time_limit=TIME_LIMIT, max_eval=MAX_EVAL, stop_at_opt=STOP_AT_OPT)

    OUT_PATH = os.path.join(out_root, prob_type + "/" + prob_name + ".txt")
    toolbox.register("record_best", record_best, opt_fit=OPT_FIT, only_save_opt=ONLY_SAVE_OPT,
                     out_path=OUT_PATH)

    toolbox.register("perturbation", perturbation_l, pr_set=pr_set, min_size=4, num=NUM)
    toolbox.register("gi_step", genetic_imp, pop_size=POP_SIZE, max_gen=MAX_GEN, cx_prob=CX_PROB, mut_prob=MUT_PROB,
                     first_imp=True, auto_imp=AUTO_IMP)

    toolbox.register("acc_criterion", acc_criterion, maximize=True)

    iterative_gen_imp(toolbox)



