import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class DQN(nn.Module):
    def __init__(self, state_dim, action_dim, device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')):
        super(DQN, self).__init__()
        self.device = device
        
        # Deeper network for better feature learning
        self.fc1 = nn.Linear(state_dim, 256)      # First layer
        self.fc2 = nn.Linear(256, 128)            # Second layer  
        self.fc3 = nn.Linear(128, 64)             # Third layer
        self.fc4 = nn.Linear(64, action_dim)      # Output layer
        
        # Batch normalization for stability
        self.bn1 = nn.BatchNorm1d(256)
        self.bn2 = nn.BatchNorm1d(128)
        self.bn3 = nn.BatchNorm1d(64)
        
        self.MSELoss = nn.MSELoss()
        
    def forward(self, x):
        if isinstance(x, np.ndarray):
            x = torch.FloatTensor(x).to(self.device)
        else:
            x = x.to(self.device)

        x = F.leaky_relu(self.fc1(x), negative_slope=0.01)
        x = F.leaky_relu(self.fc2(x), negative_slope=0.01)
        x = F.leaky_relu(self.fc3(x), negative_slope=0.01)
        q_values = self.fc4(x)
        return q_values

    
    def save(self, filepath):
        """
        Save the model weights to a file
        
        Args:
            filepath (str): Path to save the model
        """
        torch.save(self.state_dict(), filepath)
        
    def load(self, filepath):
        """
        Load model weights from a file
        
        Args:
            filepath (str): Path to load the model from
        """
        self.load_state_dict(torch.load(filepath, map_location=self.device))
        
    def __call__(self, x):
        """
        Allow direct calling of model with inputs
        
        Args:
            x: Input state
            
        Returns:
            torch.Tensor: Q-values
        """
        return self.forward(x).to(self.device)