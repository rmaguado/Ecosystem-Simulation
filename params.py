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

        self.grid_size = 20
        self.starting_creatures = 20
        self.min_n_creatures = 10
        self.simulate = False
        self.verbose = True
        self.window_show = False

        self.general_nn = True
        self.inherit_nn = None # "weights-2020.07.31-12.41.36.model"
        self.batch_size = 128
        self.exploration_rate = 0.2
        self.learning_rate = 0.05
        self.log_interval = 256
        self.action_size = 6
        self.state_features = 4
        self.discount = 0.9
        self.relatedness = 0.01
        self.relatedness_rate = 0.1
        self.training_size = 2**10

        self.interactive = False
        self.max_epochs = 1000

        self.energy_cost = 2
        self.energy_eat = 5
        self.reward_DEATH = -100
        self.reward_SKIP = 0
        self.reward_COMPETITOR = 0
        self.reward_REPRODUCE = 100

        self.seed = None # 131
