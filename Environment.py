import numpy as np

class Environment(object):
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.grass = np.ones((self.grid_size,self.grid_size))
        
    def trim(self, x, y):
        self.grass[x][y] -= 0.1
        
    def growth_cycle(self):
        self.grass += 0.1
        self.grass = np.where(self.grass <= 1, self.grass, 1)