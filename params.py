"""
Parameter Class
"""
import os

# no startup info
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

class Params():
    """
    Parameter Class
    """
    def __init__(self):

        # run
        self.interactive = False
        self.window_show = True
        self.verbose = True
        self.simulate = False
        self.seed = None # 131

        self.logs_thin = 100 # log each n epochs
        self.logs_random = False # log initial random actions

        self.cuda = "cuda:1"

        # environment
        self.grid_size = 20
        self.starting_creatures = 20
        self.min_n_creatures = 2

        self.relatedness = 0.02

        self.grass_grow_rate = 0.05

        self.energy_cost = .2
        self.energy_eat = 5
        self.energy_eat_transfer_rate = 0.5
        self.energy_reprod_transfer_rate = 0.5

        self.action_size = 6    # left up down right eat reproduce
        self.state_features = 4 # has_entity, id, strength, energy
        self.vision_grid = 5    # 5x5

        # Q & NN

        self.convolutional = True

        self.max_epochs = 10000

        self.discount = 0.95

        self.general_nn = True
        self.inherit_nn = None # "weights-2020.   .model"

        self.batch_size = 256

        self.memory_size = self.batch_size * 100 # 2**16 # 65536 experience replay
        self.memory_load = None # "stack-2020.   .memory"

        self.training_random = self.batch_size * 20
        self.exploration_rate = 0.25
        self.exploration_rate_min = 0.05
        self.exploration_rate_dec = (self.exploration_rate - self.exploration_rate_min) / (self.max_epochs * self.min_n_creatures) / 0.75 # last 25% at min

        self.learning_rate = 0.001
        self.retrain_delay = 10

        self.reward_death = -0.8
        self.reward_evasion = -0.4
        self.reward_default = 0
        self.reward_predation = 0
        self.reward_repro = 0.5

    def reproductive_cost(self, strength):
        """
        Calculate reproductive cost proportional to creature strength.
        """
        return strength * 20 + 5
