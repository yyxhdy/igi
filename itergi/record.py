import time


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