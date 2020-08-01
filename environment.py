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

    def growth_cycle(self, reset=False):
        """
        Grow grass in all squares by one cycle.
        """
        if reset:
            self.grass = np.ones((self.params.grid_size, self.params.grid_size))
        else:
            self.grass += 0.1
            self.grass = np.where(self.grass <= 1, self.grass, 1)
