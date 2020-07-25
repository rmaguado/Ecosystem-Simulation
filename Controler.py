#!/usr/bin/python3

from Environment import Environment
from Window import Window
from Entities import Entities
import time
import os, sys, select, termios

class Controler(object):
    def __init__(self, grid_size, starting_creatures):
        self.grid_size = grid_size
        self.environment = Environment(grid_size)
        self.entities = Entities(grid_size, starting_creatures, self.environment)
        self.window = Window(grid_size)
        self.epoch = 0
        self.to_iterate = 0
        self.logs = []
        self.running = True
        
        self.clear()
        self.render()
        self.idle()
        
    def clear(self):
        print("\033c")
        
    def render(self):
        self.window.render(self.environment.grass, self.entities.creatures)
        
    def refresh(self):
        if self.window.handle_event():
            self.render()
            
    def next_epoch(self):
        self.environment.growth_cycle()
        self.logs.append(self.entities.iterate())
        self.epoch += 1
        self.render()
        
    def console(self):
        self.clear()
        print(f'Epoch: {self.epoch}')
        print(f'Creatures: {len(self.entities.creatures)}')
        print("Type 'help' for a list of commands.")
        
    def help(self):
        self.clear()
        print('iter -i [indefinately] -c [counter] -s [stop]')
        print('logs -g [get logs for one epoch | default last] -a [all logs]')
        print('exit')
        print('')
        print('Type enter to return to idle.')
    
    def get_logs(self, args):
        self.clear()
        if len(args) > 1:
            if args[1] == '-a':
                for i in range(len(self.logs)):
                    print(f'Epoch: {i}')
                    for j in self.logs[i]:
                        print(j)
                    print('')
            elif args[1] == '-g':
                if len(args) == 2:
                    epoch = self.epoch -1
                else:
                    epoch = int(args[2])
                for i in self.logs[epoch]:
                    print(i)
        else:
            pass
        print('')
        print('Type enter to return to idle.')
        
    def iterate(self, args):
        if len(args) == 1:
            self.clear()
            print('Please enter appropriate parameters')
        if args[1] == '-i':
            self.to_iterate = -1
        elif args[1] == '-c':
            if len(args) == 3:
                self.to_iterate = int(args[2])
                print(f'Added {args[2]} iteratios to queue. ')
                self.console()
        elif args[1] == '-s':
            self.to_iterate = 0
            self.console()
            
    def idle(self):
        self.console()
        
        while self.running:
            self.refresh()
            time.sleep(0.01)
            
            if select.select([sys.stdin,],[],[],0.0)[0]:
                a = input()
                args = a.split()
                if len(args) == 0:
                    self.console()
                else:    
                    if args[0] == 'help':
                        self.help()
                    elif args[0] == 'iter':
                        self.iterate(args)
                    elif args[0] == 'logs':
                        self.get_logs(args)
                    elif args[0] == 'exit':
                        self.clear()
                        self.running = False
                    else:
                        self.clear()
                        print('Command not understood.')
                    
                termios.tcflush(sys.stdin, termios.TCIOFLUSH)
            
            if self.to_iterate == -1:
                self.next_epoch()
            elif self.to_iterate > 0:
                self.next_epoch()
                self.to_iterate -= 1
            
            if self.window.quit_command:
                self.running = False
        

os.chdir(os.path.dirname(sys.argv[0]))
controler = Controler(grid_size=10, starting_creatures=5)



"""
* add a probability that hunting fails
* add a reward mechanism that discourages attacking same species 

* add a reward mechanism that discourages attacking stronger and encourages attacking weaker
* add a method for training once having been terminated for the general neural net

* click on creatures to get stats
* pre-train a neural network to inherit

"""
