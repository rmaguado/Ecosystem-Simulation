"""
Environment Class
"""
import numpy as np
from params import Params

class Environment():
    """
    Environment Class
    """

    def __init__(self):
        self.params = Params()
        self.grass = np.ones((self.params.grid_size, self.params.grid_size))

        # counters for logs
        self.epoch = None

    def grow_grass(self, reset=False):
        """
        Grow grass in all squares by one cycle.
        """
        if reset:
            self.grass = np.ones((self.params.grid_size, self.params.grid_size))    # 1
        else:                                                                       # grow max 1
            self.grass += self.params.grass_grow_rate
            self.grass = np.where(self.grass >= 1, self.grass, 1)
