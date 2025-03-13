import numpy as np
import pygame
import math

def calculate_reward(environment, prev_state=None, done=False, collision=False):
    """
    Calculate a simplified reward that prioritizes speed and track completion
    
    Args:
        environment: Racing environment
        prev_state: Previous state if available
        done: Whether the episode is done
        collision: Whether the car collided with a border or obstacle
    
    Returns:
        float: Calculated reward
    """
    car = environment.car1
    
    # Terminal rewards/penalties
    if environment.car1_finished:
        return 100.0  # Large reward for finishing the race
    
    if collision or car.failed:
        return -50.0  # Significant penalty for collision
        
    if done and not environment.car1_finished:
        return -20.0  # Penalty for timeout without finishing
    
    # Calculate base reward primarily from speed
    speed_ratio = car.velocity / car.max_velocity
    
    # Primary speed reward - focus on maintaining optimal speed
    if speed_ratio > 0.9:
        speed_reward = 0.9  # Very good but not maximum (prevents excessive speed)
    elif speed_ratio > 0.7:
        speed_reward = 1.0  # Maximum reward for optimal speed range
    elif speed_ratio > 0.4:
        speed_reward = 0.7  # Decent speed but could be better
    elif speed_ratio > 0.1:
        speed_reward = 0.3  # Too slow
    else:
        speed_reward = -0.2  # Penalty for nearly stopping
    
    # Simple track position awareness - only penalize if very close to edges
    ray_data = car.ray_distances_border
    min_ray = min(ray_data) if ray_data else 0
    
    # Only apply edge penalty when very close to borders (but not crashing)
    edge_penalty = -0.5 if min_ray < 0.15 else 0.0
    
    # Small time penalty to encourage finishing
    time_penalty = -0.01
    
    # Final reward calculation
    total_reward = speed_reward + edge_penalty + time_penalty
    
    return total_reward

def process_state(environment):
    """
    Process the environment state for the DQN input
    
    Args:
        environment: Racing environment
        
    Returns:
        numpy.ndarray: Processed state vector
    """
    return np.array(environment.state())

def map_action_to_game_action(action_idx):
    """
    Map DQN action index to game action
    
    The game action codes are:
    0: Do nothing
    1: Accelerate
    2: Brake
    3: Turn left
    4: Turn right
    5: Accelerate + Turn left
    6: Accelerate + Turn right
    7: Brake + Turn left
    8: Brake + Turn right
    
    Args:
        action_idx (int): DQN action index (0-8)
        
    Returns:
        int: Game action code
    """
    # Direct mapping for simplicity
    return action_idx

def save_training_stats(episode, rewards, losses, epsilon, filename="training_stats.csv"):
    """
    Save training statistics to a CSV file
    
    Args:
        episode (int): Current episode
        rewards (list): Episode rewards
        losses (list): Training losses
        epsilon (float): Current epsilon value
        filename (str): CSV filename
    """
    import csv
    import os
    
    # Create header if file doesn't exist
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Episode', 'Reward', 'Avg_Loss', 'Epsilon'])
        
        avg_loss = np.mean(losses) if losses else 0
        writer.writerow([episode, rewards, avg_loss, epsilon])

def draw_training_info(surface, episode, steps, reward, epsilon, loss):
    """
    Draw training information on the game surface
    
    Args:
        surface: Pygame surface
        episode (int): Current episode
        steps (int): Steps in current episode
        reward (float): Current episode reward
        epsilon (float): Current exploration rate
        loss (float): Current loss value
    """
    font = pygame.font.SysFont('Arial', 20)
    
    # Training info background
    info_surface = pygame.Surface((300, 140))
    info_surface.set_alpha(200)
    info_surface.fill((50, 50, 50))
    surface.blit(info_surface, (surface.get_width() - 310, 10))
    
    # Training info text
    text_color = (255, 255, 255)
    episode_text = font.render(f"Episode: {episode}", True, text_color)
    steps_text = font.render(f"Steps: {steps}", True, text_color)
    reward_text = font.render(f"Reward: {reward:.2f}", True, text_color)
    epsilon_text = font.render(f"Epsilon: {epsilon:.2f}", True, text_color)
    loss_text = font.render(f"Loss: {loss:.4f}" if loss is not None else "Loss: N/A", True, text_color)
    
    surface.blit(episode_text, (surface.get_width() - 300, 20))
    surface.blit(steps_text, (surface.get_width() - 300, 45))
    surface.blit(reward_text, (surface.get_width() - 300, 70))
    surface.blit(epsilon_text, (surface.get_width() - 300, 95))
    surface.blit(loss_text, (surface.get_width() - 300, 120))