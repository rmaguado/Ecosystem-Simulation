"""
Neural Net Class
"""
from random import sample, seed
from collections import deque
import numpy as np
from tensorflow.keras import Sequential, Input
from tensorflow.keras.layers import Conv2D, Dense, Flatten
from tensorflow.keras.optimizers import Adam
from params import Params


class Neuralnet():
    """
    Neural Net Class
    """
    def __init__(self):
        self.params = Params()

        if self.params.seed:
            seed(self.params.seed)

        self.state_size = (self.params.vision_grid, self.params.vision_grid, self.params.state_features)
        self.optimizer = Adam(learning_rate=self.params.learning_rate)

        self.experience_replay = deque(maxlen=self.params.memory_size)

        self.batch_counter = 1
        self.align_counter = 1
        self.q_network = self.compile_model()
        self.target_network = self.compile_model()
        self.align_target()
        self.random_action = True

    def store(self, state, action, reward, next_state):
        """
        Store rewards and states for experience replay.
        """
        self.experience_replay.append((state, action, reward, next_state))
        if self.batch_counter % self.params.batch_size == 0:
            self.retrain()
        self.batch_counter += 1

        # end of random
        if self.batch_counter >= self.params.training_size:
            if self.random_action:
                print("End of random experiences")
            self.random_action = False

        return self.random_action

    def compile_model(self):
        """
        Compiles the model.
        """
        model = Sequential()

        if self.params.convolutional:
            model.add(Conv2D(filters=1, kernel_size=3, strides=(1, 1), padding='same', input_shape=self.state_size))
            model.add(Flatten())
            model.add(Dense(64, activation='relu'))
            model.add(Dense(32, activation='relu'))
            model.add(Dense(16, activation='relu'))
        else:
            model.add(Input(shape=self.state_size))
            model.add(Flatten())
            model.add(Dense(256, activation='relu'))
            model.add(Dense(128, activation='relu'))

        model.add(Dense(self.params.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=self.optimizer)
        return model

    def inherit_network(self, weights):
        """
        Copies the weights from another network
        """
        self.q_network.set_weights(weights)
        self.align_target()

    def align_target(self):
        """
        Copies the weights from another network
        """
        self.target_network.set_weights(self.q_network.get_weights())

    def act(self, state):
        """
        Produces a q table
        #not used
        """
        q_values = self.q_network.predict(state)
        return q_values

    def retrain(self):
        """
        Train the neural net from a sample of the experience replay items.
        """
        if self.align_counter % self.params.retrain_delay == 0:
            self.align_target()

        if len(self.experience_replay) >= self.params.batch_size:
            batch = sample(self.experience_replay, self.params.batch_size)
            states = np.ndarray((self.params.batch_size, self.params.vision_grid, self.params.vision_grid, self.params.state_features))
            for i in range(self.params.batch_size):
                states[i] = batch[i][0]
            target = self.target_network.predict(states) # makes Q prediction for each action for all states in batch
            for i in range(self.params.batch_size):
                action_b = batch[i][1]
                reward_b = batch[i][2]
                nextstate_b = batch[i][3]
                target[i][action_b] = reward_b + self.params.discount * np.amax(self.target_network.predict(nextstate_b))
            self.q_network.fit(states, target, epochs=1, verbose=0)

        self.align_counter += 1
