# dqn_agent.py - SIMPLIFIED VERSION
import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
import random
import os
from scripts.dqn import DQN
from scripts.replaybuffer import ReplayBuffer


class DQNAgent:
    """Simple DQN Agent for Racing"""
    
    # Action space: 6 actions (no backward)
    ACTION_MAP = [0, 1, 3, 4, 5, 6]  # coast, forward, left, right, forward+left, forward+right
    
    def __init__(self, state_dim, action_dim=6, device=None):
        if action_dim != 6:
            raise ValueError("Only 6-action mode supported")
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.device = device if device else torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        print(f"DQN Agent initialized - {action_dim} actions on {self.device}")
        
        # Networks
        self.policy_net = DQN(state_dim, action_dim, device=self.device).to(self.device)
        self.target_net = DQN(state_dim, action_dim, device=self.device).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        # Hyperparameters
        self.gamma = 0.99
        self.lr = 0.0003
        self.batch_size = 128
        
        # Epsilon (exploration)
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9995
        
        # Target network update frequency
        self.target_update = 100
        
        # Tracking
        self.episode_count = 0
        self.train_step = 0
        self.best_reward = -float('inf')
        self.best_finish_time = 0.0
        self.best_finish_episode = 0
        
        # Replay buffer
        self.replay_buffer = ReplayBuffer(capacity=100000)
        
        # Optimizer
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.lr)
        
        # Model paths
        self.model_dir = "models/actions_6"
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, "model.pt")
        self.best_model_path = os.path.join(self.model_dir, "best_model.pt")
    
    def get_action(self, state, training=True):
        """Select action using epsilon-greedy"""
        if state is None:
            return self.ACTION_MAP[0]  # coast
        
        # Random exploration
        if training and random.random() < self.epsilon:
            agent_action = random.randint(0, self.action_dim - 1)
        else:
            # Greedy action from network
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                q_values = self.policy_net(state_tensor)
                agent_action = torch.argmax(q_values).item()
        
        # Map to environment action
        return self.ACTION_MAP[agent_action]
    
    def store_experience(self, state, env_action, reward, next_state, done):
        """Store experience in replay buffer"""
        # Convert environment action to agent action index
        try:
            agent_action = self.ACTION_MAP.index(env_action)
        except ValueError:
            agent_action = 0  # default to coast
        
        self.replay_buffer.add(state, agent_action, reward, next_state, done)
    
    def update(self):
        """Update policy network"""
        if len(self.replay_buffer) < self.batch_size * 2:
            return None
        
        # Sample batch
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)
        
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Current Q-values
        q_values = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Target Q-values (Double DQN)
        with torch.no_grad():
            best_actions = self.policy_net(next_states).max(1)[1].unsqueeze(1)
            next_q_values = self.target_net(next_states).gather(1, best_actions).squeeze(1)
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        # Loss
        loss = F.smooth_l1_loss(q_values, target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()
        
        # Update target network
        self.train_step += 1
        if self.train_step % self.target_update == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        return loss.item()
    
    def end_episode(self, episode_reward, checkpoints_reached, time_remaining, finished):
        """Called at end of episode"""
        self.episode_count += 1
        
        if episode_reward > self.best_reward:
            self.best_reward = episode_reward
        
        if finished and time_remaining > self.best_finish_time:
            self.best_finish_time = time_remaining
            self.best_finish_episode = self.episode_count
            self.save_model(self.best_model_path)
    
    def save_model(self, save_path=None):
        """Save checkpoint"""
        if save_path is None:
            save_path = self.model_path
        
        checkpoint = {
            'model_state_dict': self.policy_net.state_dict(),
            'target_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'train_step': self.train_step,
            'episode_count': self.episode_count,
            'best_reward': self.best_reward,
            'best_finish_time': self.best_finish_time,
            'best_finish_episode': self.best_finish_episode,
            'action_dim': self.action_dim,
            'replay_buffer': self.replay_buffer.to_dict(),
        }
        
        tmp = save_path + '.tmp'
        torch.save(checkpoint, tmp)
        os.replace(tmp, save_path)
    
    def load_model(self, filepath=None):
        """Load checkpoint"""
        if filepath is None:
            filepath = self.model_path
        
        if not os.path.exists(filepath):
            print(f"No model found at {filepath}")
            return False
        
        checkpoint = torch.load(filepath, map_location=self.device, weights_only=False)
        
        # Verify action dim
        saved_action_dim = checkpoint.get('action_dim', self.action_dim)
        if saved_action_dim != self.action_dim:
            print(f"Warning: Model has {saved_action_dim} actions, expected {self.action_dim}")
            return False
        
        # Load network states
        self.policy_net.load_state_dict(checkpoint['model_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        # Load tracking
        self.epsilon = checkpoint.get('epsilon', self.epsilon)
        self.train_step = checkpoint.get('train_step', 0)
        self.episode_count = checkpoint.get('episode_count', 0)
        self.best_reward = checkpoint.get('best_reward', -float('inf'))
        self.best_finish_time = checkpoint.get('best_finish_time', 0.0)
        self.best_finish_episode = checkpoint.get('best_finish_episode', 0)
        
        # Load replay buffer
        if 'replay_buffer' in checkpoint and checkpoint['replay_buffer']:
            from scripts.replaybuffer import replaybuffer_from_dict
            self.replay_buffer = replaybuffer_from_dict(checkpoint['replay_buffer'])
        
        return True