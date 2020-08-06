# Ecosystem-Simulation
how it works:

there are agents that interact with one another: 

- the environment aka the grass
- a q-learning style neural network class
- instances of a creature class that inherit the neural network class
- a grid for creatures to move in / eat others / reproduce

i tried to make a launcher with a chmod shell script but had problems with different systems installing pygame in different locations (smh my head pygame)

dependencies:

- torch
- python3
- pygame (for windowed option)
- numpy
