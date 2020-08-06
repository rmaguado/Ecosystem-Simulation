"""
Network Class.
"""
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
from params import Params

class DeepQNetwork(nn.Module):
    """
    Neural Network Class.
    """
    def __init__(self):
        super(DeepQNetwork, self).__init__()

        self.params = Params()

        self.conv1 = nn.Conv2d(in_channels=self.params.state_features, out_channels=16, padding=1, kernel_size=3, stride=1)
        self.conv2 = nn.Conv2d(in_channels=16, out_channels=4, padding=1, kernel_size=3, stride=1)
        self.conv3 = nn.Conv2d(in_channels=4, out_channels=1, padding=1, kernel_size=3, stride=1)

        fc_input_dims = self.calculate_conv_output_dims(input_dims=(4, 5, 5))

        self.fc1 = nn.Linear(fc_input_dims, 512)
        self.fc2 = nn.Linear(512, self.params.action_size)

        self.optimizer = optim.RMSprop(self.parameters(), lr=self.params.learning_rate)

        self.loss = nn.MSELoss()
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)

    def calculate_conv_output_dims(self, input_dims):
        """
        Returns dimensions of convolutional output.
        """
        state = T.zeros(1, *input_dims)
        dims = self.conv1(state)
        dims = self.conv2(dims)
        dims = self.conv3(dims)
        return int(np.prod(dims.size()))

    def forward(self, state):
        """
        Forward propagation.
        """
        conv1 = F.relu(self.conv1(state))
        conv2 = F.relu(self.conv2(conv1))
        conv3 = F.relu(self.conv3(conv2))
        # conv3 shape is BS x n_filters x H x W
        conv_state = conv3.view(conv3.size()[0], -1)
        # conv_state shape is BS x (n_filters * H * W)
        flat1 = F.relu(self.fc1(conv_state))
        actions = self.fc2(flat1)

        return actions

    def save_checkpoint(self, fname):
        """
        Saves weights.
        """
        print('... saving checkpoint ...')
        T.save(self.state_dict(), fname)

    def load_checkpoint(self, fname):
        """
        Loads the saved weights.
        """
        print('... loading checkpoint ...')
        self.load_state_dict(T.load(fname))
