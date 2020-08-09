"""
Logs Class.
"""
import time
import numpy as np
from params import Params

class Logs():
    """
    Logs Class.
    """
    def __init__(self, environment):
        self.environment = environment
        self.params = Params()
        self.timestart = time.time()
        self.date_time = time.strftime("%Y.%m.%d-%H.%M.%S")
        self.actions = ['left ', 'up   ', 'right', 'down ', 'eat  ', 'repro']

        self.run_fname = f"out/par_run-{self.date_time}.tsv"
        self.logs_fname = f"out/log_out-{self.date_time}.tsv"

        self.batch = 1
        self.loss_fname = f"out/loss_run-{self.date_time}.tsv"

    def log_run(self):
        """
        log run parameters
        """
        header = "Parameters:\t\n\n\t\n"
        with open(self.run_fname, "w") as fname:
            fname.write(header)
        for i in dir(self.params):
            if i[0:1] != "_" and not callable(getattr(self.params, i)):
                line = f'{i:>30}:\t {getattr(self.params, i)}\n'
                with open(self.run_fname, "a") as fname:
                    fname.write(line)

    def log_header(self):
        """
        header for log file
        """
        line = "epoch\tsecs\trandom\tcreatures\tcreature\tstrength\tenergy\tpos_x\tpos_y\taction\treward\tend\tleft\tup\tright\tdown\teat\trepro\n"
        with open(self.logs_fname, "w") as fname:
            fname.write(line)

    def log_iteration(self, epoch, random_policy, creatures, creature, action, reward, end, q_table):
        """
        log iteration
        """
        elapsed = time.time() - self.timestart
        self.timestart = time.time()
        line = f"{epoch:>6}\t{elapsed:8.5f}\t{str(random_policy)[0:1]}\t{len(creatures):>3}\t{creature.creature_id:12.10f}\t{creature.strength:8.5f}\t{creature.energy:6.2f}\t{creature.pos_x:5}\t{creature.pos_y:5}\t{self.actions[action]}\t{reward:>4}\t{end:>5}\t" + np.array2string(q_table, formatter={'float_kind':lambda x: "%#8.1f" % x}, separator="\t", max_line_width=200)[2:-2] + "\n"
        with open(self.logs_fname, "a") as fname:
            fname.write(line)

    def log_loss_header(self):
        """
        log loss
        """
        line = "agent\tbatch\tcreatures\texploration\tloss\n"
        with open(self.loss_fname, "w") as fname:
            fname.write(line)

    def log_loss(self, agent, batch, creatures, exploration, loss):
        """
        log run parameters
        """
        if batch == 1:
            self.log_loss_header()

        line = f"{agent:>8}\t{batch:>6}\t{creatures:>8}\t{exploration:7.5f}\t{loss:12.2f}\n"
        with open(self.loss_fname, "a") as fname:
            fname.write(line)
