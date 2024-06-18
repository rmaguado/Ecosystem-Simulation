# Game of life with Q-Learning

The environment includes creatures that are each an instance of a RL agent. Each instance occupies a square in a grid and has a score of their energy. An instance can perform the following actions which consume energy: move, consume grass, and reproduce. An instance is removed when it starves. 

dependencies:

- torch
- python3
- pygame (for windowed option)
- numpy
