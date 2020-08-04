"""
Entities Class
"""
import time
from random import randint, seed
import numpy as np
from params import Params
from creature import Creature

class Entities():
    """
    Entities Class
    """
    def __init__(self, environment, general_nn=None, inherit_nn=None):
        self.params = Params()
        if self.params.seed:
            seed(self.params.seed)
        self.creatures = []
        self.entity_grid = np.zeros((self.params.grid_size, self.params.grid_size, 4)) # 4 is for has_entity, id, strength, energy
        self.environment = environment
        if self.params.general_nn: # T
            self.random_policy = True
        else:
            self.random_policy = False

        self.general_nn = general_nn
        self.inherit_nn = inherit_nn

        for _ in range(self.params.starting_creatures):
            self.spawn_creature()

        if self.params.verbose:
            self.date_time = time.strftime("%Y.%m.%d-%H.%M.%S")
            self.timestart = time.time()
            self.actions = ['left ', 'up   ', 'right', 'down ', 'eat  ', 'repro']
            # logs header
            line = "epoch\tsecs\trandom\tcreatures\tcreature\tstrength\tenergy\tpos_x\tpos_y\taction\treward\tleft\tup\tright\tdown\teat\trepro\n"
            with open(f"out/log_out-{self.date_time}.tsv", "w") as fname:
                fname.write(line)

    def write_creature(self, creature):
        """
        Write in creature traits in grid.
        """
        self.entity_grid[creature.pos_x][creature.pos_y][0] = 1
        self.entity_grid[creature.pos_x][creature.pos_y][1] = creature.creature_id
        self.entity_grid[creature.pos_x][creature.pos_y][2] = creature.strength
        self.entity_grid[creature.pos_x][creature.pos_y][3] = 1 / creature.energy

    def erase_creature(self, creature):
        """
        Clear the location of a creature in the grid.
        """
        self.entity_grid[creature.pos_x][creature.pos_y][:] = 0

    def spawn_creature(self, pos_x=None, pos_y=None, strength=None, creature_id=None, energy=None):
        """
        Create creature objects.
        ** arguments pos_x ... are needed only for simulations
        """
        if self.general_nn: # T
            creature = Creature(autogenerated=True, entity_grid=self.entity_grid, pos_x=pos_x, pos_y=pos_y, strength=strength, energy=energy, creature_id=creature_id, general_nn=self.general_nn)
        elif self.inherit_nn:
            creature = Creature(autogenerated=True, entity_grid=self.entity_grid, pos_x=pos_x, pos_y=pos_y, strength=strength, energy=energy, creature_id=creature_id, inherit_nn=self.general_nn)
        else:
            creature = Creature(autogenerated=True, entity_grid=self.entity_grid, pos_x=pos_x, pos_y=pos_y, strength=strength, energy=energy, creature_id=creature_id)
        self.write_creature(creature)
        self.creatures.append(creature)

    def get_creature(self, creature_id):
        """
        Obtain creature object from id.
        """
        creature = None
        for i in self.creatures:
            if i.creature_id == creature_id:
                creature = i
                break
        return creature

    def clear(self):
        """
        Empty creature objects from queue.
        """
        for creature in self.creatures:
            self.entity_grid[creature.pos_x][creature.pos_y][:] = 0
        self.creatures = []

    def get_state(self, var_x, var_y):
        """
        Returns input grid for a vision_grid of 5 x 5.
        """
        state = np.ndarray((self.params.vision_grid, self.params.vision_grid, 4))
        state[:, :, 0] = np.pad(self.environment.grass, ((2, 2), (2, 2)), 'constant', constant_values=(1, 1))[var_x:var_x+self.params.vision_grid, var_y:var_y+self.params.vision_grid]
        state[:, :, 1:] = np.pad(self.entity_grid, ((2, 2), (2, 2), (0, 0)), 'constant', constant_values=(1, 1))[var_x:var_x+self.params.vision_grid, var_y:var_y+self.params.vision_grid, 1:]
        state = state.reshape((1, self.params.vision_grid, self.params.vision_grid, 4))

        return state

    def check_death(self, creature):
        """
        Determines if a creature's is in direct danger of being eaten.
        """
        state = self.get_state(creature.pos_x, creature.pos_y)
        for var_x, var_y in [[0, 1], [1, 0], [0, -1], [-1, 0]]:
            competitor = self.get_creature(state[0][var_x + 2][var_y + 2][1])
            if competitor:
                if competitor.strength > creature.strength and not creature.check_related(competitor):
                    return True
        return False

    def iterate(self):
        """
        Each creature takes a turn.
        """
        terminated = []
        for i in self.creatures:
            if not i in terminated:
                term = self.action(i) # move creature
                if term:
                    terminated.append(term)   # marks for deletion
        for i in terminated:
            self.delete_creature(i)

    def action(self, creature):
        """
        Get an action from the Neural Net,
        Call the function,
        Store the rewards and states.
        """
        # state
        state = self.get_state(creature.pos_x, creature.pos_y)
        # action
        if np.random.rand() < self.params.exploration_rate or self.random_policy:
            q_table = np.zeros(self.params.action_size).reshape(1, self.params.action_size)
            action = randint(0, self.params.action_size-1)
        else:
            q_table = creature.neural_net.q_network.predict(state) 
            action = np.argmax(q_table)
        #reward
        reward = None
        terminated = None
        # hide from grid
        self.erase_creature(creature)
        # energy cost
        creature.energy -= self.params.energy_cost

        if action == 0:     # left
            reward, terminated = self.move_creature(creature, -1, 0)
        elif action == 1:   # up
            reward, terminated = self.move_creature(creature, 0, 1)
        elif action == 2:   # right
            reward, terminated = self.move_creature(creature, 1, 0)
        elif action == 3:   # down
            reward, terminated = self.move_creature(creature, 0, -1)
        elif action == 4:   # eat
            reward, terminated = self.eat_grass(creature)
        elif action == 5:   # reproduce
            reward, terminated = self.reproduce_creature(creature)

        # if creature has run out of energy it dies
        if creature.check_living(): # energy > 0
            if not terminated or (terminated and terminated != creature): # terminated.creature_id != creature.creature_id):
                # unhide from grid
                self.write_creature(creature)
        else: # exhausetd energy
            self.erase_creature(creature)
            terminated = creature
            reward = self.params.reward_DEATH

        # reward creature based on moving away from danger 
        if self.check_death(creature):
            reward = self.params.reward_EVASION

        # store in memory_replay and update random_policy
        self.random_policy = creature.store_experience(state, action, reward, future_state=self.get_state(creature.pos_x, creature.pos_y))

        # logs
        if self.params.verbose:
            elapsed = time.time() - self.timestart
            self.timestart = time.time()
            line = f"{self.environment.epoch:>6}\t{elapsed:8.5f}\t{str(self.random_policy)[0:1]}\t{len(self.creatures):>3}\t{creature.creature_id:12.10f}\t{creature.strength:8.5f}\t{creature.energy:6.2f}\t{creature.pos_x:5}\t{creature.pos_y:5}\t{self.actions[action]}\t{reward:>4}\t" + np.array2string(q_table, formatter={'float_kind':lambda x: "%#8.4f" % x}, separator="\t")[2:-2] + "\n"
            with open(f"out/log_out-{self.date_time}.tsv", "a") as fname:
                fname.write(line)

        return terminated

    def move_creature(self, creature, x_change, y_change):
        """
        Calls to move the creature in a direction.
        If the creature does not have enough energy or cannot move: the creature will not move.
        If the creature moves into an empty space, the old location is wiped and is written in the new location.
        If the creature moves into another creature, the one with a greater strength will consume the other and take a portion of its energy.
        """
        reward = None
        terminated = None

        # Check that the creature will not move outside the grid bounds and has enough energy to move.
        if creature.pos_x + x_change >= 0 and creature.pos_x + x_change < self.params.grid_size and creature.pos_y + y_change >= 0 and creature.pos_y + y_change < self.params.grid_size and creature.energy > 0:
            # check if the new location is empty
            if self.entity_grid[creature.pos_x + x_change][creature.pos_y + y_change][0] == 0:
                creature.pos_x += x_change
                creature.pos_y += y_change
                reward = self.params.reward_SKIP
            # is not empty
            else:
                # gets creature object for competing creature
                competitor = self.get_creature(self.entity_grid[creature.pos_x + x_change][creature.pos_y + y_change][1])
                # checks strength, stronger creature survives and consumes other
                if creature.strength > competitor.strength:
                    creature.pos_x += x_change
                    creature.pos_y += y_change
                    creature.energy += competitor.energy * self.params.energy_eat_transfer_rate # ** halved
                    # check if creatures were related (anti-cannibalism rewarding)
                    if creature.check_related(competitor):
                        reward = self.params.reward_DEATH
                    else:
                        reward = self.params.reward_COMPETITOR # * competitor.energy 
                    self.erase_creature(competitor)
                    terminated = competitor
                # if competitor is stronger
                else:
                    competitor.energy += creature.energy * self.params.energy_eat_transfer_rate
                    self.write_creature(competitor)
                    reward = self.params.reward_DEATH
                    terminated = creature
        # creature tries to move outside grid
        else:
            reward = self.params.reward_SKIP

        return reward, terminated

    def eat_grass(self, creature):
        """
        Function for creature to consume grass.
        """
        terminated = None
        # eat only if grass is green (1)
        if self.environment.grass[creature.pos_x][creature.pos_y] == 1: # if green
            self.environment.grass[creature.pos_x][creature.pos_y] = 0  # eat all
            creature.energy += self.params.energy_eat
        reward = self.params.reward_SKIP

        return reward, terminated

    def reproduce_creature(self, parent):
        """
        Attempts to create a new creature given space and energy requirements are met.
        """
        terminated = None
        # reproduction success based on space and energy
        reproductive_cost = parent.get_reproductive_cost() * self.params.energy_reprod_transfer_rate
        if parent.energy > reproductive_cost:
            parent.energy -= reproductive_cost
            creature = Creature(autogenerated=False, entity_grid=self.entity_grid, general_nn=self.general_nn)
            creature.inherit(parent, entity_grid=self.entity_grid, general_nn=self.general_nn)
            self.creatures.append(creature)
            self.write_creature(creature)
            reward = self.params.reward_REPRODUCE
        else:
            reward = self.params.reward_SKIP

        return reward, terminated

    def delete_creature(self, creature):
        """
        Deletes a creature from the grid and creature list.
        """
        self.erase_creature(creature)
        self.creatures.remove(creature)
