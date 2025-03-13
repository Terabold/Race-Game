import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
import random
import os
from dqn import DQN
from replaybuffer import ReplayBuffer

class DQNAgent:
    """
    DQN Agent that interacts with the racing environment and learns to drive
    """
    def __init__(self, state_dim, action_dim, device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')):
        """
        Initialize the DQN Agent
        
        Args:
            state_dim (int): Dimension of the state space
            action_dim (int): Number of possible actions
            device (torch.device): Device to run the model on (CPU/CUDA)
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.device = device
            
        print(f"Using device: {self.device}")
        
        # DQN Networks
        self.policy_net = DQN(state_dim, action_dim, device=self.device).to(self.device)
        self.target_net = DQN(state_dim, action_dim, device=self.device).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        # Hyperparameters (modified to match DDQN Keras values)
        self.gamma = 0.99  # Discount factor
        self.lr = 0.0005   # Learning rate (matches DDQN)
        self.batch_size = 64  # Batch size (matches DDQN)
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.02  # Minimum exploration (matches DDQN)
        self.epsilon_decay = 0.999  # Slower decay (matches DDQN)
        self.target_update = 10  # Update target network every N steps
        
        # Replay buffer
        self.replay_buffer = ReplayBuffer(capacity=25000)  # Matches DDQN mem_size
        
        # Optimizer
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.lr)
        
        # Training tracking
        self.train_step = 0
        self.model_dir = "models"
        os.makedirs(self.model_dir, exist_ok=True)
        
    def get_action(self, state, training=True):
        """
        Select an action using epsilon-greedy policy
        
        Args:
            state: Current state
            training (bool): Whether we're in training mode (use epsilon-greedy) or not
            
        Returns:
            int: Selected action
        """
        if training and random.random() < self.epsilon:
            # Exploration: random action
            return random.randint(0, self.action_dim - 1)
        else:
            # Exploitation: best known action
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                q_values = self.policy_net(state_tensor)
                return torch.argmax(q_values).item()
    
    def update(self):
        """
        Update the policy network based on experiences in the replay buffer
        
        Returns:
            float: Loss value
        """
        if len(self.replay_buffer) < self.batch_size:
            return None
            
        # Sample batch from replay buffer
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)
        
        # Convert to tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Compute Q values
        q_values = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # DDQN implementation - use policy net to select actions and target net to evaluate them
        with torch.no_grad():
            # Find best actions using policy net
            best_actions = self.policy_net(next_states).max(1)[1].unsqueeze(1)
            # Evaluate those actions using target net (this is the DDQN part)
            next_q_values = self.target_net(next_states).gather(1, best_actions).squeeze(1)
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
            
        # Compute loss (using Huber loss like in Keras example)
        loss = F.smooth_l1_loss(q_values, target_q_values)
        
        # Update policy network
        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping to prevent exploding gradients
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()
        
        # Update target network
        self.train_step += 1
        if self.train_step % self.target_update == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
            
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        return loss.item()
    
    def save_model(self, episode):
        """
        Save the model
        
        Args:
            episode (int): Current episode number
        """
        model_path = os.path.join(self.model_dir, f"dqn_episode_{episode}.pth")
        self.policy_net.save(model_path)
        print(f"Model saved to {model_path}")
        
    def load_model(self, filepath):
        """
        Load a saved model
        
        Args:
            filepath (str): Path to the model file
        """
        self.policy_net.load(filepath)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        print(f"Model loaded from {filepath}")