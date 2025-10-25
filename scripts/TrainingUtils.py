import numpy as np
import pygame
import math

def calculate_reward(environment, prev_state=None, done=False, collision=False):
    """
    Simplified, small-magnitude reward function.
    - finish: +1.0
    - collision: -1.0
    - timeout (done without finishing): -0.5
    - small per-step penalty: -0.001
    - small speed/progress bonus: ~[-0.01 .. +0.01]
    This keeps episode totals small (no thousands).
    """
    car = environment.car1

    # Terminal rewards
    if environment.car1_finished:
        return 1.0

    if collision or car.failed:
        return -1.0

    if done and not environment.car1_finished:
        return -0.5

    # Small reward from speed (normalized)
    speed_ratio = 0.0
    try:
        speed_ratio = car.velocity / car.max_velocity
    except Exception:
        speed_ratio = 0.0

    # Map speed_ratio (~-1..1) to small reward
    speed_reward = (speed_ratio - 0.5) * 0.02  # about -0.01 .. +0.01

    # Edge penalty if very close to border (normalized distances available from rays)
    ray_data = getattr(car, "ray_distances_border", None)
    if ray_data:
        min_ray_norm = min([d / car.ray_length for d in ray_data]) if ray_data else 1.0
    else:
        min_ray_norm = 1.0

    edge_penalty = -0.02 if min_ray_norm < 0.1 else 0.0

    # Small time penalty to encourage finishing faster
    time_penalty = -0.001

    total_reward = speed_reward + edge_penalty + time_penalty

    # Clamp reward to a sensible small range
    total_reward = max(-1.0, min(1.0, total_reward))

    return total_reward

def process_state(environment):
    """
    Process the environment state for the DQN input
    """
    state = environment.state()
    if state is None:
        return np.zeros(1, dtype=np.float32)
    return np.array(state, dtype=np.float32)

def map_action_to_game_action(action_idx):
    """
    For this simplified setup we use a direct mapping.
    """
    return int(action_idx)

def save_training_stats(episode, rewards, losses, epsilon, filename="training_stats.csv"):
    import csv
    import os
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Episode', 'Reward', 'Avg_Loss', 'Epsilon'])
        avg_loss = np.mean(losses) if losses else 0
        writer.writerow([episode, rewards, avg_loss, epsilon])

def draw_training_info(surface, episode, steps, reward, epsilon, loss):
    font = pygame.font.SysFont('Arial', 20)
    info_surface = pygame.Surface((300, 140))
    info_surface.set_alpha(200)
    info_surface.fill((50, 50, 50))
    surface.blit(info_surface, (surface.get_width() - 310, 10))
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