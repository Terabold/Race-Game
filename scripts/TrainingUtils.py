# TrainingUtils.py - UPDATED with simplified UI
import numpy as np
import pygame
import math
from scripts.Constants import *

# ============================================================================
# REWARD CALCULATION - FIXED
# ============================================================================

def calculate_reward(environment, action, step_info, prev_state=None, checkpoint_idx=None):
    """
    Optimized reward calculation
    
    Returns:
        reward (float): Total reward
        breakdown (dict): Reward components
    """
    reward = 0.0
    breakdown = {}

    # 1. SPEED REWARDS
    speed_ratio = abs(environment.car.velocity) / environment.car.max_velocity
    
    if speed_ratio >= 0.95:
        speed_reward = 2.0
    elif speed_ratio >= 0.80:
        speed_reward = 1.5
    elif speed_ratio >= 0.65:
        speed_reward = 1.0
    elif speed_ratio >= 0.45:
        speed_reward = 0.4
    elif speed_ratio >= 0.30:
        speed_reward = 0.0
    else:
        speed_reward = -0.8
        
    reward += speed_reward
    breakdown["speed"] = speed_reward

    # 2. EDGE PENALTY
    car = environment.car
    if car.ray_distances:
        min_ray_normalized = min(car.ray_distances) / car.ray_length
        
        if min_ray_normalized < 0.08:
            edge_penalty = -2.0
        elif min_ray_normalized < 0.15:
            edge_penalty = -0.5
        elif min_ray_normalized < 0.25:
            edge_penalty = -0.1
        else:
            edge_penalty = 0.05
    else:
        edge_penalty = 0.0
    
    edge_penalty *= 0.2  # Scale penalty
    reward += edge_penalty
    breakdown["edge"] = edge_penalty

    # 3. CHECKPOINT CROSSING
    if step_info.get("checkpoint_crossed", False):
        checkpoint_reward = 15.0
        reward += checkpoint_reward
        breakdown["checkpoint"] = checkpoint_reward

    # 4. BACKWARD CROSSING
    if step_info.get("backward_crossed", False):
        backward_penalty = -30.0
        reward += backward_penalty
        breakdown["backward"] = backward_penalty

    # 5. OBSTACLE HIT
    if step_info.get("hit_obstacle", False):
        obstacle_penalty = -50.0
        reward += obstacle_penalty
        breakdown["obstacle"] = obstacle_penalty

    # 6. TERMINAL STATES
    if step_info.get("finished", False):
        finish_reward = 300.0
        reward += finish_reward
        breakdown["finish"] = finish_reward
        
        # Time bonus
        time_ratio = environment.time_remaining / environment.max_time
        if time_ratio > 0.6:
            time_bonus = 100.0
        elif time_ratio > 0.4:
            time_bonus = 60.0
        elif time_ratio > 0.2:
            time_bonus = 30.0
        else:
            time_bonus = 10.0
        time_bonus*=2.0
        reward += time_bonus
        breakdown["fast_finish"] = time_bonus
    
    if step_info.get("collision", False):
        collision_penalty = -750.0
        reward += collision_penalty
        breakdown["collision"] = collision_penalty
    
    if step_info.get("timeout", False):
        timeout_penalty = -300.0
        reward += timeout_penalty
        breakdown["timeout"] = timeout_penalty

    reward = float(reward)
    breakdown["total"] = reward
    
    return reward, breakdown


# ============================================================================
# STATISTICS
# ============================================================================

def save_training_stats(episode, avg_reward, losses, epsilon, 
                       win_count=0, avg_checkpoints=0, 
                       total_checkpoints=16,
                       best_finish_time=0.0,
                       best_finish_episode=0,
                       filename="training_stats.csv"):
    """Save training statistics to CSV"""
    import csv
    import os
    
    win_rate = (win_count / 100.0) * 100
    checkpoint_pct = (avg_checkpoints / total_checkpoints * 100) if total_checkpoints > 0 else 0
    best_completion_time = max(0.0, 25.0 - best_finish_time)
    
    write_header = not os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                'Episode', 'Avg_Reward_100', 'Avg_Loss', 'Epsilon', 
                'WinRate_%', 'Avg_Checkpoints_%',
                'Best_Finish_Time_Remaining', 'Best_Completion_Time', 'Best_Finish_Episode'
            ])
        
        avg_loss = float(np.mean(losses)) if losses else 0.0
        
        writer.writerow([
            episode,
            f"{avg_reward:.2f}",
            f"{avg_loss:.4f}",
            f"{epsilon:.4f}",
            f"{win_rate:.1f}",
            f"{checkpoint_pct:.1f}",
            f"{best_finish_time:.2f}",
            f"{best_completion_time:.2f}",
            best_finish_episode,
        ])


# ============================================================================
# TRAINING UI
# ============================================================================

def draw_training_ui(surface, episode, reward_breakdown, best_finish_time, best_finish_episode):
    """Draw simplified training overlay"""
    if not reward_breakdown:
        return
    
    # Panel setup
    panel_w, panel_h = 280, 280
    panel_x = surface.get_width() - panel_w - 10
    panel_y = 10
    
    # Create panel
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((20, 20, 30, 230))
    pygame.draw.rect(panel, (80, 80, 100), (0, 0, panel_w, panel_h), 2)
    
    # Fonts
    title_font = pygame.font.SysFont('Arial', 18, bold=True)
    item_font = pygame.font.SysFont('Arial', 15)
    
    # Title
    title = title_font.render(f"Episode {episode}", True, (255, 255, 255))
    panel.blit(title, (10, 10))
    pygame.draw.line(panel, (80, 80, 100), (10, 35), (panel_w - 10, 35), 1)
    
    y = 45
    line_h = 20
    
    # Reward breakdown (only non-zero)
    items = [
        ('Checkpoint', 'checkpoint', (100, 255, 100)),
        ('Speed', 'speed', (100, 200, 100)),
        ('Edge', 'edge', (200, 200, 100)),
        ('Obstacle', 'obstacle', (255, 150, 50)),
        ('Backward', 'backward', (255, 80, 80)),
        ('Finish', 'finish', (100, 255, 100)),
        ('Collision', 'collision', (255, 50, 50)),
    ]
    
    for label, key, color in items:
        value = reward_breakdown.get(key, 0.0)
        if abs(value) < 0.01:
            continue
        
        # Label
        label_text = item_font.render(f"{label}:", True, (200, 200, 200))
        panel.blit(label_text, (15, y))
        
        # Value
        value_text = item_font.render(f"{value:+.1f}", True, color)
        value_rect = value_text.get_rect(right=panel_w - 15, y=y)
        panel.blit(value_text, value_rect)
        
        y += line_h
    
    # Total
    y += 5
    pygame.draw.line(panel, (80, 80, 100), (10, y), (panel_w - 10, y), 1)
    y += 8
    
    total = float(reward_breakdown.get('total', 0.0))
    total_label = title_font.render("Total:", True, (255, 255, 255))
    panel.blit(total_label, (15, y))
    
    total_color = (100, 255, 100) if total > 0 else (255, 100, 100) if total < 0 else (200, 200, 200)
    total_text = title_font.render(f"{total:+.1f}", True, total_color)
    total_rect = total_text.get_rect(right=panel_w - 15, y=y)
    panel.blit(total_text, total_rect)
    
    # Best finish
    if best_finish_time > 0:
        y += 30
        pygame.draw.line(panel, (80, 80, 100), (10, y), (panel_w - 10, y), 1)
        y += 10
        
        best_label = item_font.render("Best Finish:", True, (200, 200, 200))
        panel.blit(best_label, (15, y))
        
        y += line_h
        best_time_text = item_font.render(f"{25.0 - best_finish_time:.2f}s", True, (255, 215, 0))
        panel.blit(best_time_text, (15, y))
        
        best_ep_text = item_font.render(f"(Ep {best_finish_episode})", True, (150, 150, 150))
        best_ep_rect = best_ep_text.get_rect(right=panel_w - 15, y=y)
        panel.blit(best_ep_text, best_ep_rect)
    
    surface.blit(panel, (panel_x, panel_y))


def draw_reward_overlay(surface, episode_reward_breakdown, current_episode=0):
    """Legacy function - redirects to draw_training_ui"""
    draw_training_ui(surface, current_episode, episode_reward_breakdown, 0, 0)