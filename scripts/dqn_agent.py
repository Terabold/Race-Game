import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
import random
import os
from scripts.dqn import DQN
from scripts.replaybuffer import ReplayBuffer, replaybuffer_from_dict


class DQNAgent:
    """
    DQN Agent with improved hyperparameters for consistency
    """

    def __init__(self, state_dim, action_dim, device=None):
        """
        Initialize the DQN Agent
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.device = device if device else torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        print(f"Using device: {self.device}")

        # Networks
        self.policy_net = DQN(state_dim, action_dim, device=self.device).to(self.device)
        self.target_net = DQN(state_dim, action_dim, device=self.device).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        # IMPROVED HYPERPARAMETERS
        self.gamma = 0.995
        self.lr = 0.0001  # Lower learning rate for more stable learning
        self.batch_size = 64  # Smaller batches for more frequent updates
        
        # IMPROVED EPSILON SCHEDULE
        self.epsilon = 1.0
        self.epsilon_min = 0.05  # HIGHER minimum - maintains exploration
        self.epsilon_decay = 0.99985  # SLOWER decay
        
        # Target network update
        self.target_update = 100  # Even more stable
        
        # Episode tracking
        self.episode_count = 0

        # Replay buffer
        self.replay_buffer = ReplayBuffer(capacity=100000)
        
        # Optimizer with gradient clipping
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.lr)
        
        # Learning rate scheduler - more aggressive reduction on plateau
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, 
            mode='max',  # Monitor rewards (maximize)
            factor=0.5,  # Reduce LR by half
            patience=500,  # Wait 500 episodes before reducing
            verbose=True
        )

        # Tracking
        self.train_step = 0
        self.model_dir = "models"
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, "model.pt")
        
        # Performance tracking
        self.best_reward = -float('inf')
        self.best_checkpoints = 0
        self.episodes_without_improvement = 0
        self.recent_rewards = []
        self.recent_checkpoints = []

    def get_action(self, state, training=True):
        """
        Select an action using epsilon-greedy policy
        """
        if state is None:
            return 0
        
        if training and random.random() < self.epsilon:
            # Exploration
            return random.randint(0, self.action_dim - 1)
        else:
            # Exploitation
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                q_values = self.policy_net(state_tensor)
                return torch.argmax(q_values).item()

    def update(self):
        """
        Update the policy network using a batch from replay buffer
        """
        if len(self.replay_buffer) < self.batch_size * 4:  # Wait for enough samples
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

        # Double DQN target
        with torch.no_grad():
            # Select best actions using policy network
            best_actions = self.policy_net(next_states).max(1)[1].unsqueeze(1)
            # Evaluate using target network
            next_q_values = self.target_net(next_states).gather(1, best_actions).squeeze(1)
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values

        # Huber loss (more robust than MSE)
        loss = F.smooth_l1_loss(q_values, target_q_values)

        # Optimize with gradient clipping
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

    def end_episode(self, episode_reward=0, checkpoints_reached=0):
        """
        Called when an episode ends
        """
        self.episode_count += 1
        
        # Track recent performance
        self.recent_rewards.append(episode_reward)
        self.recent_checkpoints.append(checkpoints_reached)
        
        if len(self.recent_rewards) > 100:
            self.recent_rewards.pop(0)
            self.recent_checkpoints.pop(0)
        
        # Update learning rate based on performance
        if len(self.recent_rewards) >= 100:
            avg_reward = np.mean(self.recent_rewards)
            avg_checkpoints = np.mean(self.recent_checkpoints)
            
            self.scheduler.step(avg_reward)
        
        return self.epsilon

    def save_model(self, save_path=None):
        """
        Save model, optimizer, and replay buffer
        """
        if save_path is None:
            save_path = self.model_path
        checkpoint = {
            'model_state_dict': self.policy_net.state_dict(),
            'target_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'epsilon': self.epsilon,
            'train_step': self.train_step,
            'episode_count': self.episode_count,
            'best_reward': self.best_reward,
            'best_checkpoints': self.best_checkpoints,
            'recent_rewards': self.recent_rewards,
            'recent_checkpoints': self.recent_checkpoints,
            'replay_buffer': self.replay_buffer.to_dict(),
        }
        tmp = save_path + '.tmp'
        torch.save(checkpoint, tmp)
        os.replace(tmp, save_path)

    def load_model(self, filepath=None):
        """
        Load model and training state
        """
        if filepath is None:
            filepath = self.model_path
        if not os.path.exists(filepath):
            print("No model file found.")
            return False

        checkpoint = torch.load(filepath, map_location=self.device, weights_only=False)

        self.policy_net.load_state_dict(checkpoint['model_state_dict'])
        
        if 'target_state_dict' in checkpoint:
            self.target_net.load_state_dict(checkpoint['target_state_dict'])
        else:
            self.target_net.load_state_dict(self.policy_net.state_dict())

        if 'optimizer_state_dict' in checkpoint:
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        if 'scheduler_state_dict' in checkpoint:
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])

        if 'epsilon' in checkpoint:
            loaded_epsilon = checkpoint['epsilon']
            # Don't reset epsilon if it's reasonable
            if loaded_epsilon < 0.05:
                print(f"WARNING: Loaded epsilon {loaded_epsilon:.4f} is very low!")
                print(f"Resetting to {self.epsilon_min:.4f}")
                self.epsilon = self.epsilon_min
            else:
                self.epsilon = loaded_epsilon

        if 'train_step' in checkpoint:
            self.train_step = checkpoint['train_step']
            
        if 'episode_count' in checkpoint:
            self.episode_count = checkpoint['episode_count']
        
        if 'best_reward' in checkpoint:
            self.best_reward = checkpoint['best_reward']
        
        if 'best_checkpoints' in checkpoint:
            self.best_checkpoints = checkpoint['best_checkpoints']
        
        if 'recent_rewards' in checkpoint:
            self.recent_rewards = checkpoint['recent_rewards']
            
        if 'recent_checkpoints' in checkpoint:
            self.recent_checkpoints = checkpoint['recent_checkpoints']

        if 'replay_buffer' in checkpoint and checkpoint['replay_buffer']:
            self.replay_buffer = replaybuffer_from_dict(checkpoint['replay_buffer'])

        print(f"Loaded: ε={self.epsilon:.4f}, step={self.train_step}, ep={self.episode_count}, buffer={len(self.replay_buffer)}")
        print(f"Best checkpoints: {self.best_checkpoints:.1f}/46")
        if self.recent_rewards:
            print(f"Recent avg reward: {np.mean(self.recent_rewards):.1f}")
        if self.recent_checkpoints:
            print(f"Recent avg checkpoints: {np.mean(self.recent_checkpoints):.1f}/46")
        return True