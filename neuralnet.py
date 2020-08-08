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

        self.device = T.device(self.params.cuda if T.cuda.is_available() else 'cpu')
        
        
        # network model
        if self.params.convolutional:
            
            self.conv1 = nn.Conv2d(in_channels=self.params.state_features, out_channels=16, padding=1, kernel_size=3, stride=1)
            self.conv2 = nn.Conv2d(in_channels=16, out_channels=4, padding=1, kernel_size=3, stride=1)
            self.conv3 = nn.Conv2d(in_channels=4, out_channels=1, padding=1, kernel_size=3, stride=1)
            fc_input_dims = self.calculate_conv_output_dims(input_dims=(self.params.state_features, self.params.vision_grid, self.params.vision_grid))
            self.fc1 = nn.Linear(fc_input_dims, 512)
            self.fc2 = nn.Linear(512, self.params.action_size)
        else:
            
            fc_input_dims = self.params.state_features * self.params.vision_grid * self.params.vision_grid # 100
            self.fc1 = nn.Linear(fc_input_dims, 400)
            self.fc2 = nn.Linear(400, 300)
            self.fc3 = nn.Linear(300, self.params.action_size)

        self.optimizer = optim.Adam(self.parameters(), lr=self.params.learning_rate)
        # RMSprop

        self.loss = nn.MSELoss()
        
        self.to(self.device)

    def forward(self, state):
        """
        Forward propagation.
        """
        if self.params.convolutional:
            
            o = F.relu(self.conv1(state)) # conv1
            o = F.relu(self.conv2(o))     # conv2
            o = F.relu(self.conv3(o))     # conv3      shape is BS x n_filters x H x W
            o = o.view(o.size()[0], -1)   # conv_flat  shape is BS x (n_filters * H * W)
            o = F.relu(self.fc1(o))       # relu1      -> 512
            actions = self.fc2(o)         # sum    512 -> 6
            
        else:
            
            state = T.flatten(state, 1)  # flatten starting 1: leaving the batch
            
            o = F.relu(self.fc1(state))  # relu1      -> 400
            o = F.relu(self.fc2(o))      # relu2  400 -> 300
            actions = self.fc3(o)        # sum    300 -> 6

        return actions
    
    def calculate_conv_output_dims(self, input_dims):
        """
        Returns dimensions of convolutional output.
        """
        state = T.zeros(1, *input_dims)
        dims = self.conv1(state)
        dims = self.conv2(dims)
        dims = self.conv3(dims)
        return int(np.prod(dims.size()))

