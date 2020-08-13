"""
Entities Class
"""
from random import randint, seed
import numpy as np
from params import Params
from creature import Creature
from logs import Logs

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

        self.exploration_rate = self.params.exploration_rate

        for _ in range(self.params.starting_creatures):
            self.spawn_creature()

        if self.params.verbose:
            self.logs = Logs(self.environment)
            self.logs.log_run()
            self.logs.log_header()
            self.batch_counter = self.general_nn.align_counter  # starts 1
            self.logs_random = not self.params.logs_random and self.random_policy

    def write_creature(self, creature):
        """
        Write in creature traits in grid.
        """
        self.entity_grid[creature.pos_x][creature.pos_y][0] = 1
        self.entity_grid[creature.pos_x][creature.pos_y][1] = creature.creature_id
        self.entity_grid[creature.pos_x][creature.pos_y][2] = creature.strength
        self.entity_grid[creature.pos_x][creature.pos_y][3] = creature.energy # 1 / creature.energy

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
        state = np.ndarray((4, self.params.vision_grid, self.params.vision_grid))
        state[0, :, :] = np.pad(self.environment.grass, ((2, 2), (2, 2)), 'constant', constant_values=(1, 1))[var_x:var_x+self.params.vision_grid, var_y:var_y+self.params.vision_grid]
        state[1, :, :] = np.pad(self.entity_grid, ((2, 2), (2, 2), (0, 0)), 'constant', constant_values=(1, 1))[var_x:var_x+self.params.vision_grid, var_y:var_y+self.params.vision_grid, 1]
        state[2, :, :] = np.pad(self.entity_grid, ((2, 2), (2, 2), (0, 0)), 'constant', constant_values=(1, 1))[var_x:var_x+self.params.vision_grid, var_y:var_y+self.params.vision_grid, 2]
        state[3, :, :] = np.pad(self.entity_grid, ((2, 2), (2, 2), (0, 0)), 'constant', constant_values=(1, 1))[var_x:var_x+self.params.vision_grid, var_y:var_y+self.params.vision_grid, 3]
        state = state.reshape((1, 4, self.params.vision_grid, self.params.vision_grid))

        return state

    def check_death(self, creature):
        """
        Determines if a creature's is in direct danger of being eaten.
        """
        state = self.get_state(creature.pos_x, creature.pos_y)
        for var_x, var_y in [[0, 1], [1, 0], [0, -1], [-1, 0]]:
            competitor = self.get_creature(state[0][1][var_x + 2][var_y + 2])
            if competitor:
                if competitor.strength > creature.strength and not creature.check_related(competitor):
                    return True
        return False

    def iterate(self):
        """
        Each creature takes a turn.
        """
        self.general_nn.cum_reward = 0
        terminated = []
        for i in self.creatures:
            if not i in terminated:
                term = self.action(i) # move creature
                if term:
                    terminated.append(term)   # marks for deletion
        for i in terminated:
            self.delete_creature(i)

        # board: each epoch
        self.general_nn.writer.add_scalar('Avg reward', self.general_nn.cum_reward/len(self.creatures), global_step=self.general_nn.align_counter)
        self.general_nn.writer.add_scalar('Creatures', len(self.creatures), global_step=self.general_nn.align_counter)
        self.general_nn.writer.add_scalar('Exploration', self.exploration_rate, global_step=self.general_nn.align_counter)
        if self.general_nn.align_counter > 1:
            self.general_nn.writer.add_histogram('Actions', np.array([self.general_nn.experience_replay[i][1] for i in range(0, -self.params.batch_size, -1)]), global_step=self.general_nn.align_counter)
            pdiff = 0
            for peval, ptarget in zip(self.general_nn.q_eval.parameters(), self.general_nn.q_next.parameters()):
                pdiff += (peval.data-ptarget.data).abs().sum()
            self.general_nn.writer.add_scalar('Param diff', pdiff, global_step=self.general_nn.align_counter)

        # log loss
        if self.params.verbose:
            if self.batch_counter < self.general_nn.align_counter:
                # network updated
                self.logs.log_loss(self.general_nn.agent_hash, self.batch_counter, self.general_nn.run_counter, self.exploration_rate, self.general_nn.loss)
                self.batch_counter = self.general_nn.align_counter


    def action(self, creature):
        """
        Get an action from the Neural Net (or random)
        Perform the action
        Store the rewards and nex_state
        Return if terminated
        """
        # state
        state = self.get_state(creature.pos_x, creature.pos_y)
        # action
        if np.random.rand() < self.exploration_rate or self.random_policy:
            action = randint(0, self.params.action_size-1)
            q_table = np.zeros(self.params.action_size).reshape(1, self.params.action_size) -1
        else:
            action, q_table = creature.neural_net.act(state)

        # decrease exploration rate up to min
        self.exploration_rate -= self.params.exploration_rate_dec
        if self.exploration_rate < self.params.exploration_rate_min:
            self.exploration_rate = self.params.exploration_rate_min



        # init
        reward = None
        terminated = None
        end = False

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
            if not terminated or (terminated and terminated != creature):
                # unhide from grid
                self.write_creature(creature)
        else: # exhausetd energy
            self.erase_creature(creature)
            terminated = creature
            reward = self.params.reward_death
            end = True

        # evasion: reward creature based on moving away from danger
        if self.check_death(creature):
            reward = self.params.reward_evasion
            end = True

        # store in memory_replay and update random_policy
        self.random_policy = creature.store_experience(state, action, reward, self.get_state(creature.pos_x, creature.pos_y), end)

        # logs
        self.logs_random = self.logs_random and self.random_policy
        if (self.params.verbose and
                not self.logs_random and                                 # log initial random
                self.environment.epoch % self.params.logs_thin == 0):    # only creatures of some epochs
            self.logs.log_iteration(self.environment.epoch, self.random_policy, self.creatures, creature, action, reward, end, q_table)

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
                reward = self.params.reward_default
            # is not empty
            else:
                # gets creature object for competing creature
                competitor = self.get_creature(self.entity_grid[creature.pos_x + x_change][creature.pos_y + y_change][1])
                # checks strength, stronger creature survives and consumes other
                if creature.strength > competitor.strength:
                    creature.pos_x += x_change
                    creature.pos_y += y_change
                    creature.energy += competitor.energy * self.params.energy_eat_transfer_rate # ** halved
                    # check if creatures were related (anti-cannibalism rewarding: same as death)
                    if creature.check_related(competitor):
                        reward = self.params.reward_death
                    else:
                        reward = self.params.reward_predation # * competitor.energy
                    self.erase_creature(competitor)
                    terminated = competitor
                # if competitor is stronger
                else:
                    competitor.energy += creature.energy * self.params.energy_eat_transfer_rate
                    self.write_creature(competitor)
                    reward = self.params.reward_death
                    terminated = creature
        # creature tries to move outside grid
        else:
            reward = self.params.reward_default

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
        reward = self.params.reward_default

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
            if creature.inherit(parent, entity_grid=self.entity_grid, general_nn=self.general_nn):
                self.creatures.append(creature)
                self.write_creature(creature)
            # reward though creature not spawned
            reward = self.params.reward_repro
        else:
            reward = self.params.reward_default

        return reward, terminated

    def delete_creature(self, creature):
        """
        Deletes a creature from the grid and creature list.
        """
        self.erase_creature(creature)
        self.creatures.remove(creature)
