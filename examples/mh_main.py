import sys

import os
from deap import base
from deap import gp
import operator

from infra.util import is_better, stop_criterion, acc_criterion_mh, record_best2, compile_expr, sim_func_slia, sim_func_lisp

from infra.eval import eval_tree, run_program
import dsl.lisp as lisp
import dsl.slia as slia
from functools import partial
from infra.tree import gen_fixed_size_tree
from infra.operator import mh_mut

from algs.mh import metropolis_hastings

data_root = "../dataset"
out_root = "../results/mh"


if __name__ == '__main__':
    prob_type, prob_name = sys.argv[1:3]

    # prob_type, prob_name = "slia", "bikes-long"
    # prob_type, prob_name = "lisp", "L100"

    MAXIMIZE = True
    NORMALIZE = False

    WEIGHT = 1.0 if MAXIMIZE else -1.0

    TIME_LIMIT = 3600
    MAX_EVAL = 300000000

    SWITCH_PROB, BETA = 0.006, 0.7

    STOP_AT_OPT = True
    ONLY_SAVE_OPT = False

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

    toolbox = base.Toolbox()

    toolbox.register("rnd_tree", gen_fixed_size_tree, pr_set=pr_set)
    toolbox.register("eval_tree", eval_tree, toolbox=toolbox, inputs=inputs, outputs=outputs, executor=executor,
                     normalize=NORMALIZE, maximize=MAXIMIZE)

    toolbox.register("mutate", mh_mut, pr_set=pr_set)
    toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=30))

    toolbox.register("compile", compile_expr, pr_set=pr_set)
    toolbox.register("is_better", is_better, maximize=MAXIMIZE)

    OUT_PATH = os.path.join(out_root, prob_type + "/" + prob_name + ".txt")

    toolbox.register("record_best", record_best2, opt_fit=OPT_FIT, normalize=NORMALIZE, n_examples=len(inputs),
                     only_save_opt=ONLY_SAVE_OPT,
                     out_path=OUT_PATH)

    toolbox.register("stop_criterion", stop_criterion,
                     opt_fit=OPT_FIT, time_limit=TIME_LIMIT, max_eval=MAX_EVAL, stop_at_opt=STOP_AT_OPT)

    toolbox.register("acc_criterion", acc_criterion_mh, maximize=MAXIMIZE)
    metropolis_hastings(toolbox, switch_prob=SWITCH_PROB, beta=BETA)




