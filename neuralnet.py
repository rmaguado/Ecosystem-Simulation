"""
Neural Net Class
"""

from params import Params
from random import sample
from collections import deque
import numpy as np
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Conv2D, Dense, Flatten
from tensorflow.keras.optimizers import Adam

class Neuralnet():
    """
    Neural Net Class
    """
    def __init__(self):
        self.params = Params()
        self.state_size = (5, 5, self.params.state_features)
        self.optimizer = Adam(learning_rate=self.params.learning_rate)

        self.experience_replay = deque(maxlen=4096)

        self.update_counter = 1
        self.align_counter = 1
        self.q_network = self.compile_model()
        self.target_network = self.compile_model()
        self.align_target()

    def store(self, state, action, reward, next_state):
        """
        Store rewards and states for experience replay.
        """
        self.experience_replay.append((state, action, reward, next_state))

    def compile_model(self):
        """
        Compiles the model.
        """
        model = Sequential()
        model.add(Conv2D(filters=16, kernel_size=3, strides=(1, 1), padding='same', input_shape=self.state_size))
        model.add(Conv2D(filters=4, kernel_size=3, strides=(1, 1), padding='valid'))
        model.add(Conv2D(filters=1, kernel_size=3, strides=(1, 1), padding='same'))
        model.add(Flatten())
        model.add(Dense(32, activation='relu'))
        model.add(Dense(32, activation='relu'))
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
        """
        q_values = self.q_network.predict(state)
        return q_values

    def retrain(self):
        """
        Train the neural net from a sample of the experience replay items.
        """
        if self.align_counter % 64 == 0:
            self.align_target()
        if len(self.experience_replay) >= self.params.batch_size:
            batch = sample(self.experience_replay, self.params.batch_size)
            for state, action, reward, next_state in batch:
                target = self.q_network.predict(state)
                target[0][np.argmax(action)] = reward + self.params.discount * np.amax(self.target_network.predict(next_state))
                self.q_network.fit(state, target, epochs=1, verbose=0)

        self.align_counter += 1
