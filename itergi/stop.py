import time


# save the consumed time and evaluations at the end
def save_costs_info(elapsed_time, n_eval, out_path):
    info = "Time: " + str(elapsed_time) + "\t" + "Eval: " + str(n_eval) + "\n"
    with open(out_path, "a+") as out_file:
        out_file.write(info)
        out_file.close()


# the stop criterion of the algorithm
def stop_criterion(best_ind, start_time, n_eval, opt_fit,
                   time_limit, max_eval, stop_at_opt, out_path=None):
    elapsed_time = time.time() - start_time

    cond1 = stop_at_opt and best_ind.fit == opt_fit
    cond2 = time_limit is not None and elapsed_time >= time_limit
    cond3 = max_eval is not None and n_eval >= max_eval

    if cond1 or cond2 or cond3:
        if out_path is not None:
            save_costs_info(elapsed_time, n_eval, out_path)
        return True

    return False
