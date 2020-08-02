"""
Neural Net Class
"""
from random import sample
from collections import deque
import numpy as np
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Conv2D, Dense, Flatten
from tensorflow.keras.optimizers import Adam
from params import Params

class Neuralnet():
    """
    Neural Net Class
    """
    def __init__(self):
        self.params = Params()
        self.state_size = (5, 5, self.params.state_features)
        self.optimizer = Adam(learning_rate=self.params.learning_rate)

        self.experience_replay = deque(maxlen=2**14)

        self.batch_counter = 1
        self.align_counter = 1
        self.q_network = self.compile_model()
        self.target_network = self.compile_model()
        self.align_target()

    def store(self, state, action, reward, next_state):
        """
        Store rewards and states for experience replay.
        """
        self.experience_replay.append((state, action, reward, next_state))
        self.batch_counter += 1
        if self.batch_counter % self.params.batch_size == 0:
            self.retrain()
        if len(self.experience_replay) == 4 * self.params.batch_size:
            return True
        return False

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
        if self.align_counter % 3 == 0:
            self.align_target()

        if len(self.experience_replay) >= self.params.batch_size:
            batch = sample(self.experience_replay, self.params.batch_size)
            states = np.ndarray((self.params.batch_size, 5, 5, self.params.state_features))
            for i in range(self.params.batch_size):
                states[i] = batch[i][0]
            target = self.q_network.predict(states[:]) # makes prediction for all states in batch
            for i in range(batch):
                target[i][batch[i][1]] = batch[i][2] + self.params.discount * np.amax(self.target_network.predict(batch[i][3]))
            self.q_network.fit(states, target, epochs=1, verbose=0)

        self.align_counter += 1
