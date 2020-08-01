#!/usr/local/bin/python3
"""
Ecosystem Simulator
"""

import time
import os
import sys
import select
import termios

from pickle import load, dump
from collections import deque
import numpy
from params import Params
from environment import Environment
from window import Window
from entities import Entities
from neuralnet import Neuralnet

class Controler():
    """
    Controler class
    """
    def __init__(self):
        self.date_time = time.strftime("%Y.%m.%d-%H.%M.%S")
        self.timestart = time.time()

        self.params = Params()
        self.environment = Environment()

        if self.params.verbose:
            line = "epoch   creatures   time    elapsed\n"
            with open(f"out/log_epocs-{self.date_time}.txt", "w") as fname:
                fname.write(line)

        if self.params.inherit_nn:
            self.inherit_nn = Neuralnet()
            self.inherit_nn.inherit_network(self.load_weights(self.params.inherit_nn))
        else:
            self.inherit_nn = None

        if self.params.general_nn:
            if self.params.inherit_nn:
                self.general_nn = self.inherit_nn
            else:
                self.general_nn = Neuralnet()
            self.entities = Entities(environment=self.environment, general_nn=self.general_nn)
        else:
            self.general_nn = None
            self.entities = Entities(environment=self.environment, inherit_nn=self.inherit_nn)

        self.epoch = 1
        self.to_iterate = 0
        self.logs = deque(maxlen=64)

        self.running = True
        self.clear()

        if self.params.simulate:
            self.load_scenario()

        if self.params.window_show:
            self.window = Window()
            self.render()

        self.idle()

        # save neural network
        if self.params.general_nn:
            self.save_weights(neural_net=self.general_nn, fname=f"out/weights-{self.date_time}.model")

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

    def save_weights(self, neural_net, fname):
        """
        Pickles the weights of a nn.
        """
        f_save = open(fname, "wb")
        weights = neural_net.q_network.get_weights()
        dump(weights, f_save)
        f_save.close()

    def load_weights(self, fname):
        """
        Opens file with saved model to retreive weights
        """
        f_name = open(fname, "rb")
        weights = load(f_name)
        f_name.close()

        return weights

    def clear(self):
        """
        The clear code for terminal
        """
        print("\033c")

    def render(self):
        """
        Render
        """
        self.window.render(self.environment.grass, self.entities.creatures)

    def refresh(self):
        """
        Update screen
        """
        if self.window.handle_event():
            self.render()

    def next_epoch(self):
        """
        Next Iteration
        """
        self.environment.growth_cycle(reset=self.params.simulate)
        if self.params.simulate:
            self.load_scenario()

        self.logs.append(self.entities.iterate())
        if self.params.verbose:
            now = time.strftime("%Y.%m.%d-%H.%M.%S")
            elapsed = time.time() - self.timestart
            self.timestart = time.time()
            line = f"{self.epoch}\t{len(self.entities.creatures)}\t{now}\t{elapsed}\n"
            with open(f"out/log_epocs-{self.date_time}.txt", "a") as fname:
                fname.write(line)

        self.epoch += 1
        if len(self.entities.creatures) < 20:
            self.entities.spawn_creature()
        if self.general_nn:
            self.general_nn.retrain() # retrain every self.batch_size new states
        if self.params.window_show:
            self.render()

        self.params.learning_rate -= 0.0005
        if self.params.learning_rate <= 0:
            self.params.learning_rate = 0.05
            self.entities.clear()
            for _ in range(self.params.starting_creatures):
                self.entities.spawn_creature()

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
        print('logs -g [get logs for one epoch | default last] -a [all logs]')
        print('exit')
        print('')
        print('Type enter to return to idle.')

    def get_logs(self, args):
        """
        –
        """
        self.clear()
        if len(args) > 1:
            if args[1] == '-a':
                for i in range(len(self.logs)):
                    print(f'Epoch: {i+1}')
                    for j in self.logs[i]:
                        print(j)
            elif args[1] == '-g':
                print(f'Epoch: {self.epoch -1}')
                for i in self.logs[-1]:
                    print(i)
        else:
            pass
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
            if self.params.window_show:
                self.refresh()
            time.sleep(0.01)

            if select.select([sys.stdin,], [], [], 0.0)[0]:
                args = input().split()
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

            if self.params.window_show:
                if self.window.quit_command:
                    self.to_iterate = 0
                    self.running = False
                    self.window.close_window()

try:
    os.chdir(os.path.dirname(sys.argv[0]))
except FileNotFoundError:
    pass

controler = Controler()
