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
        self.window_show = False
        self.verbose = True
        self.simulate = False
        self.seed = None # 131

        # environment
        self.grid_size = 20
        self.starting_creatures = 20
        self.min_n_creatures = 10

        self.action_size = 6    # left up down right eat reproduce
        self.state_features = 4 # has_entity, id, strength, energy
        self.vision_grid = 5    # 5x5

        self.grass_grow_rate = 0.2
        self.relatedness = 0.01
        self.relatedness_rate = 0.1

        self.energy_cost = 2
        self.energy_eat = 6
        self.energy_eat_transfer_rate = 0.5
        self.energy_reprod_transfer_rate = 0.5

        # Q & NN
        self.discount = 0.9
        self.general_nn = True
        self.inherit_nn = None # "weights-2020.07.31-12.41.36.model"
        self.batch_size = 512
        self.memory_size = 2**16 # 65536 experience replay
 
        self.memory_load = None # "stack-2020.08.04-17.47.27.memory"
        self.training_size = 1024
 
        self.exploration_rate = 0.2
        self.learning_rate = 0.05
        self.retrain_delay = 3 # to update target NN
        self.convolutional = False
        self.max_epochs = 500

        self.reward_DEATH = -10
        self.reward_EVASION = -10
        self.reward_SKIP = 0
        self.reward_COMPETITOR = 0
        self.reward_REPRODUCE = 20

    def reproductive_cost(self, strength):
        return strength * 100 + 5
