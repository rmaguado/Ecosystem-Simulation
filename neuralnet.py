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

        if self.params.convolutional:
            self.conv1 = nn.Conv2d(in_channels=self.params.state_features, out_channels=16, padding=1, kernel_size=3, stride=1)
            self.conv2 = nn.Conv2d(in_channels=16, out_channels=4, padding=1, kernel_size=3, stride=1)
            self.conv3 = nn.Conv2d(in_channels=4, out_channels=1, padding=1, kernel_size=3, stride=1)
            fc_input_dims = self.calculate_conv_output_dims(input_dims=(self.params.state_features, self.params.vision_grid, self.params.vision_grid))
            self.fc1 = nn.Linear(fc_input_dims, 512)
        else:
            fc_input_dims = self.params.state_features * self.params.vision_grid * self.params.vision_grid
            self.fc1 = nn.Linear(fc_input_dims, 512)
            self.fc2 = nn.Linear(512, 256)
            self.fc3 = nn.Linear(256, self.params.action_size)

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
        if self.params.convolutional:
            conv1 = F.relu(self.conv1(state))
            conv2 = F.relu(self.conv2(conv1))
            conv3 = F.relu(self.conv3(conv2))            # conv3      shape is BS x n_filters x H x W
            conv_state = conv3.view(conv3.size()[0], -1) # conv_state shape is BS x (n_filters * H * W)
            flat1 = F.relu(self.fc1(conv_state))
            actions = self.fc2(flat1)
        else:
            state = T.flatten(state,1)  # flatten starting 1: leaving the batch
            flat1 = F.relu(self.fc1(state))
            flat2 = F.relu(self.fc2(flat1))
            actions = self.fc3(flat2)

        return actions

