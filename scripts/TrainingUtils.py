# TrainingUtils.py - OPTIMIZED & FIXED
import numpy as np
import pygame
import math
from scripts.Constants import *

# ============================================================================
# REWARD CALCULATION - FIXED & OPTIMIZED
# ============================================================================

def calculate_reward(environment, action, step_info, prev_state=None, checkpoint_idx=None):
    """
    Optimized reward calculation with fixed speed reward bug
    """
    reward = 0.0
    reward_breakdown = {}

    # 1. SPEED REWARDS - FIXED BUG (removed speed_ratio = 0 line)
    speed_ratio = abs(environment.car.velocity) / environment.car.max_velocity
    
    if speed_ratio >= 0.95:  # Almost max speed
        speed_reward = 2.0
    elif speed_ratio >= 0.80:  # High speed
        speed_reward = 1.5
    elif speed_ratio >= 0.65:  # Good speed
        speed_reward = 1.0
    elif speed_ratio >= 0.45:  # Acceptable
        speed_reward = 0.4
    elif speed_ratio >= 0.30:  # Slow
        speed_reward = 0.0
    else:  # Too slow
        speed_reward = -0.8
        
    reward += speed_reward
    reward_breakdown["speed"] = speed_reward

    # 2. EDGE PENALTY - Optimized (get min ray once)
    car = environment.car
    if car.ray_distances:
        min_ray_normalized = min(car.ray_distances) / car.ray_length
        
        if min_ray_normalized < 0.08:  # Very close to wall
            edge_penalty = -2.0
        elif min_ray_normalized < 0.15:  # Too close
            edge_penalty = -0.5
        elif min_ray_normalized < 0.25:  # Close
            edge_penalty = -0.1
        else:  # Safe distance
            edge_penalty = 0.05
    else:
        edge_penalty = 0.0
    
    reward += edge_penalty
    reward_breakdown["edge"] = edge_penalty

    # 3. CHECKPOINT CROSSING - Major progress reward
    if step_info.get("checkpoint_crossed", False):
        checkpoint_reward = 15.0  # Increased from 10.0
        reward += checkpoint_reward
        reward_breakdown["checkpoint"] = checkpoint_reward

    # 4. BACKWARD CROSSING - Heavy penalty
    if step_info.get("backward_crossed", False):
        backward_penalty = -30.0  # Increased penalty
        reward += backward_penalty
        reward_breakdown["backward"] = backward_penalty

    # 5. OBSTACLE HIT - Moderate penalty
    if step_info.get("hit_obstacle", False):
        obstacle_penalty = -5.0
        reward += obstacle_penalty
        reward_breakdown["obstacle"] = obstacle_penalty

    # 6. TERMINAL STATES
    if step_info.get("finished", False):
        finish_reward = 300.0  # Increased base reward
        reward += finish_reward
        reward_breakdown["finish"] = finish_reward
        
        # Time bonus for fast completion
        time_ratio = environment.time_remaining / environment.max_time
        if time_ratio > 0.6:  # Very fast
            time_bonus = 100.0
        elif time_ratio > 0.4:  # Fast
            time_bonus = 60.0
        elif time_ratio > 0.2:  # Decent
            time_bonus = 30.0
        else:
            time_bonus = 10.0
            
        reward += time_bonus
        reward_breakdown["fast_finish"] = time_bonus
    
    if step_info.get("collision", False):
        collision_penalty = -150.0
        reward += collision_penalty
        reward_breakdown["collision"] = collision_penalty
    
    if step_info.get("timeout", False):
        timeout_penalty = -300.0
        reward += timeout_penalty
        reward_breakdown["timeout"] = timeout_penalty

    # Ensure all values are floats (no complex numbers)
    reward = float(reward)
    reward_breakdown["total"] = reward
    
    return reward, reward_breakdown


# ============================================================================
# TRAINING STATISTICS - OPTIMIZED
# ============================================================================

def save_training_stats(episode, avg_reward, losses, epsilon, 
                       win_count=0, avg_checkpoints=0, 
                       total_checkpoints=16, filename="training_stats.csv"):
    """Optimized stats saving with better formatting"""
    import csv
    import os
    
    win_rate = (win_count / 100.0) * 100
    checkpoint_pct = (avg_checkpoints / total_checkpoints * 100) if total_checkpoints > 0 else 0
    
    # Only write header if file doesn't exist
    write_header = not os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                'Episode', 
                'Avg_Reward_100', 
                'Avg_Loss', 
                'Epsilon', 
                'WinRate_%', 
                'Avg_Checkpoints_%'
            ])
        
        avg_loss = float(np.mean(losses)) if losses else 0.0
        
        writer.writerow([
            episode,
            f"{avg_reward:.2f}",
            f"{avg_loss:.4f}",
            f"{epsilon:.4f}",
            f"{win_rate:.1f}",
            f"{checkpoint_pct:.1f}"
        ])


# ============================================================================
# DRAWING FUNCTIONS - OPTIMIZED
# ============================================================================

def draw_reward_overlay(surface, episode_reward_breakdown, current_episode=0):
    """Optimized reward overlay with pre-computed surfaces"""
    if not episode_reward_breakdown:
        return
    
    # Panel setup
    panel_width = 300
    panel_height = 320
    panel_x = surface.get_width() - panel_width - 10
    panel_y = 100
    
    # Create panel surface once
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((30, 30, 40, 220))
    pygame.draw.rect(panel, (100, 100, 120), (0, 0, panel_width, panel_height), 2)
    
    # Fonts
    title_font = pygame.font.SysFont('Arial', 18, bold=True)
    item_font = pygame.font.SysFont('Arial', 16)
    
    # Title
    title = title_font.render("Reward Breakdown", True, (255, 255, 255))
    panel.blit(title, (10, 10))
    pygame.draw.line(panel, (100, 100, 120), (10, 35), (panel_width - 10, 35), 1)
    
    y_offset = 45
    line_height = 20
    
    # Reward items (only show non-zero)
    items = [
        ('Checkpoint', 'checkpoint', (100, 255, 100)),
        ('Speed', 'speed', (100, 200, 100)),
        ('Edge', 'edge', (200, 200, 100)),
        ('Obstacle', 'obstacle', (255, 150, 50)),
        ('Backward', 'backward', (255, 80, 80)),
        ('Finish', 'finish', (100, 255, 100)),
        ('Fast Finish', 'fast_finish', (255, 215, 0)),
        ('Collision', 'collision', (255, 50, 50)),
        ('Timeout', 'timeout', (255, 100, 50)),
    ]
    
    for label, key, color in items:
        value = episode_reward_breakdown.get(key, 0.0)
        value = float(value)  # Ensure float
        
        if abs(value) < 0.01:  # Skip near-zero values
            continue
        
        # Label
        label_text = item_font.render(f"{label}:", True, (200, 200, 200))
        panel.blit(label_text, (15, y_offset))
        
        # Value (right-aligned)
        value_text = item_font.render(f"{value:+.1f}", True, color)
        value_rect = value_text.get_rect(right=panel_width - 15, y=y_offset)
        panel.blit(value_text, value_rect)
        
        y_offset += line_height
    
    # Separator
    pygame.draw.line(panel, (100, 100, 120), (10, y_offset), (panel_width - 10, y_offset), 1)
    y_offset += 8
    
    # Total
    total_value = float(episode_reward_breakdown.get('total', 0.0))
    
    total_label = title_font.render("Total:", True, (255, 255, 255))
    panel.blit(total_label, (15, y_offset))
    
    total_color = (100, 255, 100) if total_value > 0 else (255, 100, 100) if total_value < 0 else (200, 200, 200)
    total_text = title_font.render(f"{total_value:+.1f}", True, total_color)
    total_rect = total_text.get_rect(right=panel_width - 15, y=y_offset)
    panel.blit(total_text, total_rect)
    
    surface.blit(panel, (panel_x, panel_y))


def draw_training_info(surface, episode, steps, reward, epsilon, loss):
    """Lightweight training info display"""
    font = pygame.font.SysFont('Arial', 18)
    
    info_texts = [
        f"Ep: {episode}",
        f"Steps: {steps}",
        f"R: {reward:.1f}",
        f"ε: {epsilon:.3f}",
        f"Loss: {loss:.4f}" if loss else "Loss: N/A"
    ]
    
    x_pos = surface.get_width() - 180
    y_pos = 10
    
    for text in info_texts:
        text_surf = font.render(text, True, (255, 255, 255))
        # Simple shadow
        surface.blit(font.render(text, True, (0, 0, 0)), (x_pos + 1, y_pos + 1))
        surface.blit(text_surf, (x_pos, y_pos))
        y_pos += 22