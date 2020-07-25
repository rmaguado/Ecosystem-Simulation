import numpy as np
import random
from random import randint
from collections import deque

from tensorflow.keras import Model, Sequential
from tensorflow.keras.layers import Conv2D, Dense, Embedding, Reshape, Flatten
from tensorflow.keras.optimizers import Adam

class NeuralNet(object):
    def __init__(self, state_features, action_size, inherit):
        self._state_size = (5, 5, state_features)
        self._action_size = action_size
        self._optimizer = Adam(learning_rate=0.01)
        
        self.experience_replay = deque(maxlen=256)
        
        self.gamma = 0.6 # discount
        self.epsilon = 0.1 # exploration rate
        
        self.q_network = self._build_compile_model()
        
    def store(self, state, action, reward, next_state):
        self.experience_replay.append((state, action, reward, next_state))
    
    def _build_compile_model(self):
        model = Sequential()
        model.add(Conv2D(
                        1, 3, strides=(1, 1), padding='same', input_shape=self._state_size
                        ))
        model.add(Flatten())
        model.add(Dense(64, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(self._action_size, activation='linear'))
        
        model.compile(loss='mse', optimizer=self._optimizer)
        return model
        
    def inherit_network(self, q_network):
        self.q_network.set_weights(q_network.get_weights())
        
    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return randint(0, self._action_size-1)
        
        q_values = self.q_network.predict(state)
        return q_values#np.argmax(q_values[0])
        
    def retrain(self, batch_size):
        minibatch = random.sample(self.experience_replay, batch_size)
        
        for state, action, reward, next_state in minibatch:
            
            target = self.q_network.predict(state)
            t = self.q_network.predict(next_state)
            target[0][np.argmax(action)] = reward + self.gamma * np.amax(t)
            
            self.q_network.fit(state, target, epochs=1, verbose=0)
            
    