import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
import random
import os
from scripts.dqn import DQN
from scripts.replaybuffer import ReplayBuffer, replaybuffer_from_dict

class DQNAgent:
    def __init__(self, state_dim, action_dim, device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.device = device

        print(f"Using device: {self.device}")

        self.policy_net = DQN(state_dim, action_dim, device=self.device).to(self.device)
        self.target_net = DQN(state_dim, action_dim, device=self.device).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        self.policy_net.eval()

        # Hyperparameters
        self.gamma = 0.99
        self.lr = 0.0005
        self.batch_size = 64
        self.epsilon = 1.0
        self.epsilon_min = 0.02
        self.epsilon_decay = 0.999
        self.target_update = 10

        self.replay_buffer = ReplayBuffer(capacity=25000)
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.lr)

        self.train_step = 0
        self.model_dir = "models"
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, "model.pt")

    def get_action(self, state, training=True):
        if state is None:
            return 0
        if training and random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        else:
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                q_values = self.policy_net(state_tensor)
                return torch.argmax(q_values).item()

    def update(self):
        if len(self.replay_buffer) < self.batch_size:
            return None

        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        q_values = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)

        with torch.no_grad():
            best_actions = self.policy_net(next_states).max(1)[1].unsqueeze(1)
            next_q_values = self.target_net(next_states).gather(1, best_actions).squeeze(1)
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values

        loss = F.smooth_l1_loss(q_values, target_q_values)

        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()

        self.train_step += 1
        if self.train_step % self.target_update == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

        # decay epsilon only during training
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        return loss.item()

    def save_model(self, save_path=None):
        """
        Save a checkpoint containing model state, optimizer, epsilon, train_step,
        and serialized replay buffer (explicit representation).
        """
        if save_path is None:
            save_path = self.model_path
        checkpoint = {
            'model_state_dict': self.policy_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict() if self.optimizer is not None else None,
            'epsilon': self.epsilon,
            'train_step': self.train_step,
            'replay_buffer': self.replay_buffer.to_dict(),
        }
        tmp = save_path + '.tmp'
        torch.save(checkpoint, tmp)
        os.replace(tmp, save_path)
        print(f"Checkpoint saved to {save_path} (epsilon={self.epsilon}, buffer={len(self.replay_buffer)})")

    def load_model(self, filepath=None):
        """
        Load checkpoint (weights, optimizer, epsilon, train_step, replay buffer).
        Uses explicit names and replaybuffer_from_dict to restore buffer.
        """
        if filepath is None:
            filepath = self.model_path
        if not os.path.exists(filepath):
            return False
        checkpoint = torch.load(filepath, map_location=self.device)
        if 'model_state_dict' in checkpoint:
            self.policy_net.load_state_dict(checkpoint['model_state_dict'])
            self.target_net.load_state_dict(self.policy_net.state_dict())
        if 'optimizer_state_dict' in checkpoint and checkpoint['optimizer_state_dict'] is not None and self.optimizer is not None:
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        if 'epsilon' in checkpoint and checkpoint['epsilon'] is not None:
            self.epsilon = checkpoint['epsilon']
        if 'train_step' in checkpoint and checkpoint['train_step'] is not None:
            self.train_step = checkpoint['train_step']
        if 'replay_buffer' in checkpoint and checkpoint['replay_buffer'] is not None:
            # use explicit helper to recreate ReplayBuffer
            self.replay_buffer = replaybuffer_from_dict(checkpoint['replay_buffer'])
        self.policy_net.eval()
        self.target_net.eval()
        print(f"Loaded checkpoint {filepath}: epsilon={self.epsilon}, train_step={self.train_step}, buffer_size={len(self.replay_buffer)}")
        return True

    def set_inference_mode(self):
        self.epsilon = 0.0
        self.policy_net.eval()
        self.target_net.eval()