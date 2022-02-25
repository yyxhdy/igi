import sys
import os
from deap import base

from deap import gp
import operator

from infra.util import is_better, stop_criterion, acc_criterion_sa, record_best, compile_expr, sim_func_lisp, sim_func_slia

from infra.eval import eval_tree, run_program
import dsl.lisp as lisp

import dsl.slia as slia
from functools import partial
from infra.tree import gen_rnd_depth_tree, subtree_localization

from infra.edit import gen_rnd_edit
from infra.operator import hvl_mut

from algs.sa import simulated_annealing

data_root = "../dataset"
out_root = "../results/sa"

if __name__ == '__main__':
    #prob_type, prob_name = sys.argv[1:3]

    # prob_type, prob_name = "slia", "bikes-long"
    prob_type, prob_name = "lisp", "L100"

    MAXIMIZE = True
    NORMALIZE = True

    WEIGHT = 1.0 if MAXIMIZE else -1.0

    MIN_DEPTH = 2
    MAX_DEPTH = 4

    TIME_LIMIT = 3600
    MAX_EVAL = 300000000

    STOP_AT_OPT = True
    ONLY_SAVE_OPT = False

    T_START = 1.5
    T_END = 0.001
    STEP_SIZE = 500

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

    toolbox.register("rnd_tree", gen_rnd_depth_tree, MIN_DEPTH, MAX_DEPTH, pr_set)

    toolbox.register("eval_tree", eval_tree, toolbox=toolbox, inputs=inputs, outputs=outputs, executor=executor,
                     normalize=NORMALIZE, maximize=MAXIMIZE)

    toolbox.register("gen_rnd_edit", gen_rnd_edit, pr_set=pr_set, edit_types=edit_types)

    toolbox.register("mutate", hvl_mut, rand_edit=toolbox.gen_rnd_edit)
    toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=30))

    toolbox.register("compile", compile_expr, pr_set=pr_set)
    toolbox.register("is_better", is_better, maximize=MAXIMIZE)

    toolbox.register("preprocessing", subtree_localization)

    toolbox.register("stop_criterion", stop_criterion,
                     opt_fit=OPT_FIT, time_limit=TIME_LIMIT, max_eval=MAX_EVAL, stop_at_opt=STOP_AT_OPT)
    toolbox.register("acc_criterion", acc_criterion_sa, maximize=MAXIMIZE)

    OUT_PATH = os.path.join(out_root, prob_type + "/" + prob_name + ".txt")
    toolbox.register("record_best", record_best, opt_fit=OPT_FIT, only_save_opt=ONLY_SAVE_OPT,
                     out_path=OUT_PATH)

    best_tree = simulated_annealing(toolbox, T_START, T_END, STEP_SIZE, init_tree=None)
    print(best_tree, best_tree.fit)
