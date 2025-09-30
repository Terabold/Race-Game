import numpy as np
import random
from collections import deque

class ReplayBuffer:
    """
    Replay Buffer for storing and sampling experiences for DQN training
    """
    def __init__(self, capacity=10000):
        """
        Initialize a ReplayBuffer with fixed capacity
        
        Args:
            capacity (int): Maximum number of experiences to store
        """
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity
        
    def add(self, state, action, reward, next_state, done):
        """
        Add an experience to the buffer
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state after taking action
            done: Whether the episode is done
        """
        experience = (state, action, reward, next_state, done)
        self.buffer.append(experience)
        
    def sample(self, batch_size):
        if len(self.buffer) < batch_size:
            indices = range(len(self.buffer))
        else:
            indices = random.sample(range(len(self.buffer)), batch_size)
            
        # More efficient batch construction
        batch = [self.buffer[i] for i in indices]
        
        # Create arrays once rather than concatenating
        states = np.vstack([exp[0] for exp in batch])
        actions = np.array([exp[1] for exp in batch], dtype=np.int64)
        rewards = np.array([exp[2] for exp in batch], dtype=np.float32)
        next_states = np.vstack([exp[3] for exp in batch])
        dones = np.array([exp[4] for exp in batch], dtype=np.float32)
        
        return states, actions, rewards, next_states, dones
    
    def __len__(self):
        """
        Return the current size of the buffer
        """
        return len(self.buffer)