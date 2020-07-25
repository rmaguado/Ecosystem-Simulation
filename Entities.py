import numpy as np
from random import randint
from Creature import Creature
import numpy as np

class Entities(object):
    def __init__(self, grid_size, starting_greatures, environment):
        self.grid_size = grid_size
        self.creatures = []
        self.entity_grid = np.zeros((self.grid_size,self.grid_size,4)) # 4 is for has_entity, id, strength, energy
        self.environment = environment
        
        for i in range(starting_greatures):
            self.spawn_creature()
            
    def write_creature(self, creature):
        self.entity_grid[creature.pos_x][creature.pos_y][0] = 1
        self.entity_grid[creature.pos_x][creature.pos_y][1] = creature.creature_id
        self.entity_grid[creature.pos_x][creature.pos_y][2] = 1 / creature.strength
        self.entity_grid[creature.pos_x][creature.pos_y][3] = 1 / creature.energy
        
    def erase_creature(self, creature):
        self.entity_grid[creature.pos_x][creature.pos_y][:] = 0
        
    def spawn_creature(self):
        creature = Creature(True, self.grid_size, self.entity_grid)
        self.write_creature(creature)
        self.creatures.append(creature)
        
    def get_creature(self, creature_id):
        creature = None
        for i in self.creatures:
            if i.creature_id == creature_id:
                creature = i
                break
        return creature
        
    def get_state(self, x ,y):
        state = np.ndarray((5,5,4))
        state[:, :, 0] = np.pad(self.environment.grass, ((2, 2), (2, 2)), 'constant', constant_values=(1, 1))[x:x+5, y:y+5]
        state[:, :, 1:] = np.pad(self.entity_grid, ((2, 2), (2, 2), (0, 0)), 'constant', constant_values=(1, 1))[x:x+5, y:y+5, 1:]
        state = state.reshape(1,5,5,4)
        return state
        
    def iterate(self):
        logs = []
        terminated = []
        for i in self.creatures:
            log, term = self.action(i)
            logs.append(log)
            if term:
                terminated.append(i)
        for i in terminated:
            self.delete_creature(i)
            
        return logs
        
    def action(self, creature):
        state = self.get_state(creature.pos_x, creature.pos_y)
        action = creature.get_action(state)
        reward = None
        log = None
        terminated = None
        i = np.argmax(action)
        if i == 0:
            reward, log, terminated = self.move_creature(creature, -1 , 0)
        elif i == 1:
            reward, log, terminated = self.move_creature(creature, 0 , 1)
        elif i == 2:
            reward, log, terminated = self.move_creature(creature, 1 , 0)
        elif i == 3:
            reward, log, terminated = self.move_creature(creature, 0 , -1)
        elif i == 4:
            reward, log, terminated = self.eat_grass(creature)
        elif i == 5:
            reward, log, terminated = self.reproduce_creature(creature)
        creature.get_rewards(state, action, reward, self.get_state(creature.pos_x, creature.pos_y))
        
        if creature.life_time % 16 == 0:
            creature.neural_net.retrain(16)
        
        return log, terminated
        
    def move_creature(self, creature, x_change , y_change):
        reward = None
        log = None
        terminated = False
        if creature.pos_x + x_change >= 0 and creature.pos_x + x_change < self.grid_size and creature.pos_y + y_change >= 0 and creature.pos_y + y_change < self.grid_size and creature.energy > 1:
            if self.entity_grid[creature.pos_x + x_change][creature.pos_y + y_change][0] == 0:
                self.erase_creature(creature)
                creature.pos_x += x_change
                creature.pos_y += y_change
                creature.energy -= 2
                if creature.check_living():
                    self.write_creature(creature)
                    reward = -1
                    log = f"{creature.creature_id} moved to {creature.pos_x}, {creature.pos_y}"
                else:
                    terminated = True
                    reward = -1
                    log = f"{creature.creature_id} starved to death"
                
            else:
                competitor = self.get_creature(self.entity_grid[creature.pos_x + x_change][creature.pos_y + y_change][1])
                if creature.strength > competitor.strength:
                    self.erase_creature(creature)
                    creature.energy -= 2
                    creature.energy += int(competitor.energy / 2)
                    creature.pos_x += x_change
                    creature.pos_y += y_change
                    if creature.check_living():
                        self.write_creature(creature)
                        if creature.check_related(competitor):
                            reward = -50
                        else:
                            reward = 50
                        log = f"{creature.creature_id} moved to {creature.pos_x}, {creature.pos_y} and consumed {competitor.creature_id}"
                    else:
                        terminated = True
                        reward = -1
                        log = f"{creature.creature_id} moved to {creature.pos_x}, {creature.pos_y} and consumed {competitor.creature_id} but still starved to death"
                    self.delete_creature(competitor)
                else:
                    competitor.energy += int(creature.energy / 2)
                    self.erase_creature(creature)
                    log = f"{creature.creature_id} was consumed by {competitor.creature_id}"
                    reward = -1
                    terminated = True
        else:
            creature.energy -= 1
            if creature.check_living():
                self.write_creature(creature)
                reward = -1
                log = f"{creature.creature_id} failed to move"
            else:
                self.erase_creature(creature)
                terminated = True
                reward = -1
                log = f"{creature.creature_id} starved to death"
                
        return reward, log, terminated
            
    def eat_grass(self, creature):
        terminated = False
        if self.environment.grass[creature.pos_x][creature.pos_y] == 1:
            self.environment.grass[creature.pos_x][creature.pos_y] -= 1
            creature.energy += 5
            self.write_creature(creature)
            reward = 1
            log = f"{creature.creature_id} consumed grass at {creature.pos_x}, {creature.pos_y}"
        else:
            creature.energy -= 1
            if creature.check_living():
                self.write_creature(creature)
                reward = -1
                log = f"{creature.creature_id} failed to consume grass"
            else:
                self.erase_creature(creature)
                terminated = True
                reward = -1
                log = f"{creature.creature_id} starved to death"
        return reward, log, terminated
        
    def reproduce_creature(self, parent):
        terminated = False
        creature = Creature(False, self.grid_size, self.entity_grid)
        success = creature.inherit(parent, self.entity_grid) and parent.energy > parent.get_reproductive_cost()
        if success:
            self.creatures.append(creature)
            self.write_creature(creature)
            parent.energy -= parent.get_reproductive_cost()
            self.write_creature(parent)
            reward = 150
            log = f"{parent.creature_id} reproduced at {parent.pos_x}, {parent.pos_y}"
        else:
            parent.energy -= 1
            if parent.check_living():
                self.write_creature(parent)
                reward = -5
                log = f"{parent.creature_id} failed to reproduce"
            else:
                self.erase_creature(parent)
                terminated = True
                reward = -5
                log = f"{parent.creature_id} starved to death"
        return reward, log, terminated
        
    def delete_creature(self, creature):
        self.entity_grid[creature.pos_x][creature.pos_y][:] = 0
        self.creatures.remove(creature)
    