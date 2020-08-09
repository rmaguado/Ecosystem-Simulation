#!/usr/bin/env python3
"""
Ecosystem Simulator
"""
import time
import os
import sys
import select
import termios
import numpy
from params import Params
from environment import Environment
from window import Window
from entities import Entities
from agent import Agent



class Controler():
    """
    Controler class
    """
    def __init__(self):
        self.date_time = time.strftime("%Y.%m.%d-%H.%M.%S")

        self.params = Params()
        self.environment = Environment()

        if self.params.inherit_nn: # F
            self.inherit_nn = Agent()
            self.inherit_nn.load_network(fname=self.params.inherit_nn)
        else:
            self.inherit_nn = None # T

        if self.params.general_nn:  # T
            if self.params.inherit_nn:  # F
                self.general_nn = self.inherit_nn
            else: # T
                self.general_nn = Agent()   # first network

            self.entities = Entities(environment=self.environment, general_nn=self.general_nn) # new NN
        else: # F
            self.general_nn = None
            self.entities = Entities(environment=self.environment, inherit_nn=self.inherit_nn)

        if self.params.memory_load:
            self.general_nn.load_memory(fname="out/"+self.params.memory_load)
            print("memory replay loaded")

        self.epoch = 1

        if self.params.simulate:
            self.load_scenario()

        if self.params.window_show:
            self.window = Window()
            self.render()

        if self.params.interactive:
            self.to_iterate = 0
            self.running = True
            self.clear()
            self.idle()
        else:
            self.loop()

        # save neural network & experience_replay
        if self.params.general_nn:
            self.general_nn.save_network(fname=f"out/weights-{self.date_time}.model")
            self.general_nn.save_memory(fname=f"out/stack-{self.date_time}.memory")


    def load_scenario(self):
        """
        Simulate a scenario
        """
        self.entities.clear()

        # 3 creatures fixed positions in random order creation

        rnd = numpy.random.permutation(3)
        pos_x = numpy.array([3, 2, 3])
        pos_y = numpy.array([3, 3, 2])
        strength = numpy.array([0.9, 0.5, 0.1])

        for i in rnd.argsort():
            self.entities.spawn_creature(pos_x=pos_x[i], pos_y=pos_y[i], strength=strength[i])

    def clear(self):
        """
        The clear code for terminal
        """
        print("\033c")

    def render(self):
        """
        Render
        """
        self.window.render(self.environment.grass, self.entities.creatures, self.epoch)

    def refresh(self, sleep=0):
        """
        Update screen
        """
        if self.window.handle_event():
            self.render()
        time.sleep(sleep)


    def next_epoch(self):
        """
        Next Iteration
        """
        if self.params.simulate:
            self.load_scenario()

        self.environment.grow_grass(reset=self.params.simulate)
        self.environment.epoch = self.epoch

        # move creatures
        self.entities.iterate()

        while len(self.entities.creatures) < self.params.min_n_creatures:
            self.entities.spawn_creature()  ## verify that general_nn is acting

        if self.params.window_show:
            self.render()

        self.epoch += 1

    def console(self):
        """
        –
        """
        self.clear()
        print(f'Epoch: {self.epoch}')
        print(f'Creatures: {len(self.entities.creatures)}')
        print("Type 'help' for a list of commands.")

    def help(self):
        """
        –
        """
        self.clear()
        print('iter -i [indefinately] -c [counter] -s [stop]')
        print('exit')
        print('')
        print('Type enter to return to idle.')

    def iterate(self, args):
        """
        –
        """
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
        """
        Updates window for input while not iterating
        """
        self.console()

        while self.running:
            if self.params.window_show and not self.entities.random_policy:
                self.refresh(sleep=0.1)  # wait until initial random end

            if select.select([sys.stdin,], [], [], 0.0)[0]:
                args = input().split()
                if len(args) == 0:
                    self.console()
                else:
                    if args[0] == 'help':
                        self.help()
                    elif args[0] == 'iter':
                        self.iterate(args)
                    elif args[0] == 'exit':
                        self.clear()
                        self.running = False
                    else:
                        self.clear()
                        print('Command not understood.')

                termios.tcflush(sys.stdin, termios.TCIOFLUSH)

            if self.to_iterate == -1:
                self.next_epoch()
                if self.params.verbose:
                    print(f"epoch: {self.epoch}")
            elif self.to_iterate > 0:
                self.next_epoch()
                self.to_iterate -= 1

            if self.params.window_show:
                if self.window.quit_command:
                    self.to_iterate = 0
                    self.running = False
                    self.window.close_window()

    def loop(self):
        """
        Loops epochs.
        """
        if self.params.verbose:
            print(f"Running for {self.params.max_epochs} epochs")
        for _ in range(self.params.max_epochs):
            if self.params.window_show:
                self.refresh(sleep=.1)
                if self.window.quit_command:
                    self.window.close_window()
                    break

            self.next_epoch()
            if self.params.verbose and self.epoch % 1000 == 0:
                print(f"Epoch: {self.epoch}")


try:
    os.chdir(os.path.dirname(sys.argv[0]))
except FileNotFoundError:
    pass

controler = Controler()
