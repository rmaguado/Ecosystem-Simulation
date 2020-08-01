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
        self.simulate = False
        self.verbose = True
        self.window_show = True

        self.general_nn = True
        self.inherit_nn = "weights-2020.07.31-12.41.36.model"
        self.batch_size = 128
        self.exploration_rate = 0.01
        self.learning_rate = 0.05
        self.log_interval = 256
        self.action_size = 6
        self.state_features = 4
        self.discount = 0.9
