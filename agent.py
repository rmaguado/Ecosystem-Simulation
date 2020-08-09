"""
Agent Class.
"""
from random import sample, randint, seed
from collections import deque
from pickle import load, dump
import gzip
import numpy as np
import torch as T
from neuralnet import DeepQNetwork
from params import Params

class Agent():
    """
    Agent Class.
    """
    def __init__(self):
        self.params = Params()

        if self.params.seed:
            seed(self.params.seed)

        self.action_space = [i for i in range(self.params.action_size)]
        self.state_size = (self.params.vision_grid, self.params.vision_grid, self.params.state_features)

        self.experience_replay = deque(maxlen=self.params.memory_size)

        self.run_counter = 1
        self.align_counter = 1
        self.q_eval = DeepQNetwork()
        self.q_next = DeepQNetwork()

        self.align_target()
        self.random_action = True
        self.loss = 0
        self.agent_hash = randint(1, 10000000)

    def store(self, state, action, reward, next_state, end):
        """
        Store rewards and states for experience replay.
        """
        self.experience_replay.append((state, action, reward, next_state, end))
        if self.run_counter % self.params.batch_size == 0:
            self.loss = self.retrain()
        self.run_counter += 1

        # end of random
        if self.run_counter >= self.params.training_random:
            if self.random_action:
                print(f"End of {self.params.training_random} initial random experiences")
            self.random_action = False

        return self.random_action

    def sample_memory(self):
        """
        Returns random sample of experience replay.
        """
        batch = sample(self.experience_replay, self.params.batch_size)

        states = np.zeros((self.params.batch_size, self.params.state_features, self.params.vision_grid, self.params.vision_grid), dtype=np.float32)
        actions = np.zeros(self.params.batch_size, dtype=np.int8)
        rewards = np.zeros(self.params.batch_size, dtype=np.int8)  # {-128 to 127}
        future_states = np.zeros((self.params.batch_size, self.params.state_features, self.params.vision_grid, self.params.vision_grid), dtype=np.float32)
        ends = np.ndarray(self.params.batch_size, dtype=bool)

        for i in range(self.params.batch_size):
            states[i] = batch[i][0]
            actions[i] = batch[i][1]
            rewards[i] = batch[i][2]
            future_states[i] = batch[i][3]
            ends[i] = batch[i][4]

        states = T.tensor(states, dtype=T.float32).to(self.q_eval.device)
        actions = T.tensor(actions, dtype=T.int64).to(self.q_eval.device)
        rewards = T.tensor(rewards, dtype=T.float32).to(self.q_eval.device)
        future_states = T.tensor(future_states, dtype=T.float32).to(self.q_eval.device)
        ends = T.tensor(ends, dtype=T.bool).to(self.q_eval.device)

        return states, actions, rewards, future_states, ends

    def act(self, state):
        """
        Generates the q table and the derived action
        """
        state = T.tensor(state, dtype=T.float32).to(self.q_eval.device)
        q_table = self.q_eval.forward(state)

        action = T.argmax(q_table).item()        # .item() removes tensor()
        q_table = q_table.detach().cpu().numpy() # tensor > numpy : need to move to cpu and detach
        return action, q_table

    def retrain(self):
        """
        Train the neural net from a sample of the experience replay items.
        """
        if self.align_counter % self.params.retrain_delay == 0:
            self.align_target()

        if len(self.experience_replay) >= self.params.batch_size:

            states, actions, rewards, future_states, ends = self.sample_memory()
            indices = np.arange(self.params.batch_size)

            q_pred = self.q_eval.forward(states)[indices, actions]
            q_next = self.q_next.forward(future_states).max(dim=1)[0]

            q_next[ends] = 0.0
            q_target = rewards + self.params.discount * q_next

            loss = self.q_eval.loss(q_target, q_pred).to(self.q_eval.device)

            self.q_eval.optimizer.zero_grad()
            loss.backward()
            self.q_eval.optimizer.step()

        self.align_counter += 1

        return loss.item()

    # netwok

    def get_weights(self):
        """
        Gets the weights from network
        """
        return self.q_eval.state_dict()

    def inherit_network(self, weights):
        """
        Copies the weights from another network
        """
        self.q_eval.load_state_dict(weights)
        self.align_target()

    def align_target(self):
        """
        Copies the weights from another network
        """
        self.q_next.load_state_dict(self.q_eval.state_dict())

    def save_network(self, fname):
        """
        Saves weights.
        """
        print('... saving checkpoint ...')
        T.save(self.q_eval.state_dict(), fname)

    def load_network(self, fname):
        """
        Loads the saved weights.
        """
        print('... loading checkpoint ...')
        self.q_eval.load_state_dict(T.load(fname))

    # memory: experience replay

    def save_memory(self, fname):
        """
        Dumps the experience_replay.
        """
        f_save = gzip.open(fname, "wb")
        dump(self.experience_replay, f_save)
        f_save.close()

    def load_memory(self, fname):
        """
        Retrieves saved experience_replay
        """
        f_name = gzip.open(fname, "rb")
        self.experience_replay = load(f_name)
        f_name.close()
