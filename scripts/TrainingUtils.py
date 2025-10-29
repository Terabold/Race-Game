import numpy as np
import pygame
import math
import csv
import os
from scripts.Constants import *

# ============================================================================
# REWARD CALCULATION - CHECKPOINT ZONE SYSTEM
# ============================================================================

def calculate_reward(environment, collision=False, just_finished=False, action=None, 
                    hit_obstacle=False, timeout=False, episode=0, 
                    checkpoint_crossed=False, backward_crossed=False,
                    track_progress=0.0, prev_checkpoint_distance=None, **kwargs):
    """
    Enhanced reward structure focused on consistency, speed, and high win rate
    """
    breakdown = {
        'speed': 0.0,
        'edge': 0.0,
        'time': 0.0,
        'checkpoint': 0.0,
        'progress': 0.0,
        'finish': 0.0,
        'collision': 0.0,
        'timeout': 0.0,
        'obstacle': 0.0,
        'backward': 0.0,
        'total': 0.0
    }

    # ========== TERMINAL REWARDS ==========
    if just_finished:
        # Massive finish reward + time bonus to encourage speed
        time_bonus = environment.time_remaining * 200  # Doubled time bonus
        breakdown['finish'] = 15000.0 + time_bonus  # Increased base finish reward
        breakdown['total'] = breakdown['finish']
        return breakdown, None
    
    if collision:
        # Harsher collision penalty to enforce precision
        breakdown['collision'] = -2000.0  # Doubled penalty
        breakdown['total'] = -2000.0
        return breakdown, None
    
    if timeout:
        # Even harsher timeout penalty to discourage slow driving
        breakdown['timeout'] = -3000.0  # 50% increase
        breakdown['total'] = -3000.0
        return breakdown, None
    
    # ========== STEP REWARDS ==========
    car = environment.car
    
    # 1. CHECKPOINT REWARDS
    if checkpoint_crossed:
        # Increased checkpoint reward for consistent progression
        checkpoint_bonus = 300.0  # 50% increase
        # Additional bonus for maintaining speed through checkpoint
        speed_at_checkpoint = abs(car.velocity) / car.max_velocity
        if speed_at_checkpoint > 0.7:
            checkpoint_bonus += 100.0  # Speed bonus at checkpoints
        
        breakdown['checkpoint'] = checkpoint_bonus
        print(f"🏁 Checkpoint {environment.checkpoint_manager.checkpoints_crossed}/"
              f"{environment.checkpoint_manager.total_checkpoints} crossed!")
    
    # 2. BACKWARD CROSSING PENALTY
    if backward_crossed:
        # Much harsher backward penalty
        breakdown['backward'] = -500.0  # Doubled penalty
        breakdown['checkpoint'] = 0.0
        print("⛔ Backward checkpoint crossed! Severe penalty applied.")
    
    current_distance = environment.checkpoint_manager.get_distance_to_checkpoint(
        (car.position.x, car.position.y)
    )
    
    # 3. EDGE AWARENESS - More granular wall distance rewards
    min_ray = min(car.ray_distances) if car.ray_distances else 200
    min_ray_normalized = min_ray / car.ray_length
    
    if min_ray_normalized < 0.10:
        breakdown['edge'] = -4.0  # Doubled wall proximity penalty
    elif min_ray_normalized < 0.20:
        breakdown['edge'] = -1.0  # Increased medium proximity penalty
    elif min_ray_normalized < 0.30:
        breakdown['edge'] = -0.2  # Small penalty for being somewhat close
    elif min_ray_normalized > 0.50:
        breakdown['edge'] = 0.5   # Better reward for maintaining safe distance
    else:
        breakdown['edge'] = 0.2   # Small positive for acceptable distance
    
    # 4. SPEED REWARDS - More granular and rewarding for consistent speed
    speed_ratio = abs(car.velocity) / car.max_velocity
    
    if speed_ratio > 0.85:
        breakdown['speed'] = 2.0  # Doubled high speed reward
    elif speed_ratio > 0.70:
        breakdown['speed'] = 1.0  # Good speed reward
    elif speed_ratio > 0.50:
        breakdown['speed'] = 0.5  # Acceptable speed
    elif speed_ratio < 0.30:
        breakdown['speed'] = -0.5  # Increased penalty for low speed
    
    # 5. OBSTACLE PENALTIES
    if hit_obstacle:
        breakdown['obstacle'] = -20.0  # Doubled obstacle penalty
    
    # 6. TIME MANAGEMENT
    # Progressive time penalty that increases as time passes
    time_used_ratio = 1 - (environment.time_remaining / environment.max_time)
    breakdown['time'] = -0.2 * (1 + time_used_ratio)  # Progressive time pressure
    
    # Calculate progress reward based on checkpoint approach
    if current_distance is not None and prev_checkpoint_distance is not None:
        distance_improvement = prev_checkpoint_distance - current_distance
        if distance_improvement > 0:
            breakdown['progress'] = distance_improvement * 0.1  # Reward for approaching checkpoint
        else:
            breakdown['progress'] = distance_improvement * 0.2  # Doubled penalty for moving away
    
    # Calculate total
    breakdown['total'] = sum(breakdown.values())
    
    return breakdown, current_distance


# ============================================================================
# TRAINING STATISTICS
# ============================================================================

def save_training_stats(episode, rewards, losses, epsilon, filename="training_stats.csv"):
    """Save training statistics to CSV"""
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Episode', 'Reward', 'Avg_Loss', 'Epsilon'])
        avg_loss = np.mean(losses) if losses else 0
        writer.writerow([episode, rewards, avg_loss, epsilon])


def log_winrate(episode, winrate, filename="winrate_log.csv"):
    """Log win-rate over last 100 episodes"""
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Episode', 'WinRate_100'])
        writer.writerow([episode, f"{winrate:.4f}"])


# ============================================================================
# DRAWING UTILITIES
# ============================================================================

def font_scale(size, Font=FONT):
    """Helper to create scaled fonts"""
    return pygame.font.Font(Font, size)


def create_shadowed_text(text, font, color, shadow_color=BLACK, offset=4):
    """Create text with shadow effect"""
    shadow = font.render(text, True, shadow_color)
    main_text = font.render(text, True, color)
    
    combined = pygame.Surface(
        (shadow.get_width() + offset, shadow.get_height() + offset), 
        pygame.SRCALPHA
    )
    combined.blit(shadow, (offset, offset))
    combined.blit(main_text, (0, 0))
    return combined

def smooth_sine_wave(time, period=4.0, min_val=0.0, max_val=1.0):
    """Generate smooth sine wave for animations"""
    normalized = (math.cos(time * (2 * math.pi / period)) + 1) / 2
    return min_val + normalized * (max_val - min_val)

def draw_training_results(environment, episode_count, reward_breakdown):
    """Draw training results overlay for AI environment"""
    current_time = pygame.time.get_ticks() / 1000
    
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    environment.surface.blit(overlay, (0, 0))
    
    title_font = font_scale(60, FONT)
    
    # Determine result type
    if environment.car_finished:
        title = "Episode Finished!"
        title_color = GREEN
    elif environment.car_crashed:
        title = "Episode Crashed"
        title_color = RED
    elif environment.car_timeout:
        title = "Episode Timeout"
        title_color = ORANGE
    else:
        title = "Episode Ended"
        title_color = WHITE
    
    title_text = create_shadowed_text(title, title_font, title_color, BLACK, 4)
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
    environment.surface.blit(title_text, title_rect)
    
    # Episode info
    info_font = font_scale(32, FONT)
    episode_text = create_shadowed_text(f"Episode: {episode_count}", info_font, WHITE)
    episode_rect = episode_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 30))
    environment.surface.blit(episode_text, episode_rect)
    
    # Reward breakdown
    reward_font = font_scale(24, FONT)
    reward_y = HEIGHT//2 + 20
    
    reward_items = [
        f"Total Reward: {reward_breakdown['total']:+.1f}",
        f"Checkpoints: {reward_breakdown.get('checkpoint', 0):+.1f}",
        f"Speed: {reward_breakdown['speed']:+.1f}",
        f"Edge: {reward_breakdown['edge']:+.1f}",
    ]
    
    for item in reward_items:
        reward_text = create_shadowed_text(item, reward_font, WHITE)
        reward_rect = reward_text.get_rect(center=(WIDTH//2, reward_y))
        environment.surface.blit(reward_text, reward_rect)
        reward_y += 35
    
    # Continue prompt
    continue_font = font_scale(28, FONT)
    continue_text = continue_font.render("Next episode starting...", True, WHITE)
    alpha = int(255 * smooth_sine_wave(current_time, period=1.5, min_val=0.3, max_val=1.0))
    continue_text.set_alpha(alpha)
    continue_rect = continue_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 180))
    environment.surface.blit(continue_text, continue_rect)

def draw_reward_overlay(surface, episode_reward_breakdown, current_episode=0):
    """Draw reward breakdown overlay with checkpoint progress"""
    if episode_reward_breakdown is None:
        return
    
    panel_width = 280
    panel_height = 340
    panel_x = surface.get_width() - panel_width - 10
    panel_y = 100
    
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((30, 30, 40, 220))
    pygame.draw.rect(panel, (100, 100, 120), (0, 0, panel_width, panel_height), 2)
    
    title_font = pygame.font.SysFont('Arial', 18, bold=True)
    item_font = pygame.font.SysFont('Arial', 16)
    
    title = title_font.render("Reward Breakdown", True, (255, 255, 255))
    panel.blit(title, (10, 10))
    pygame.draw.line(panel, (100, 100, 120), (10, 35), (panel_width - 10, 35), 1)
    
    y_offset = 45
    line_height = 22
    
    items = [
        ('Checkpoint', 'checkpoint', (100, 255, 100)),
        ('Progress', 'progress', (100, 200, 255)),
        ('Speed', 'speed', (100, 200, 100)),
        ('Edge', 'edge', (255, 150, 100)),
        ('Time', 'time', (150, 150, 150)),
        ('Obstacle', 'obstacle', (255, 100, 50)),
        ('Finish', 'finish', (100, 255, 100)),
        ('Collision', 'collision', (255, 50, 50)),
        ('Timeout', 'timeout', (255, 100, 50)),
        ('Backwards', 'checkpoint', (255, 80, 80)),
    ]
    
    for label, key, color in items:
        value = episode_reward_breakdown.get(key, 0.0)
        
        # Ensure value is a real float
        if isinstance(value, complex):
            value = value.real
        value = float(value)
        
        # Skip near-zero values for clarity (except important ones)
        if abs(value) < 0.01 and key not in ['checkpoint', 'progress', 'speed', 'edge', 'time']:
            continue
        
        label_text = item_font.render(f"{label}:", True, (200, 200, 200))
        panel.blit(label_text, (15, y_offset))
        
        value_text = item_font.render(f"{value:+.1f}", True, color)
        value_rect = value_text.get_rect(right=panel_width - 15, y=y_offset)
        panel.blit(value_text, value_rect)
        
        y_offset += line_height
    
    pygame.draw.line(panel, (100, 100, 120), (10, y_offset), (panel_width - 10, y_offset), 1)
    y_offset += 8
    
    total_value = episode_reward_breakdown.get('total', 0.0)
    if isinstance(total_value, complex):
        total_value = total_value.real
    total_value = float(total_value)
    
    total_label = title_font.render("Total:", True, (255, 255, 255))
    panel.blit(total_label, (15, y_offset))
    
    total_color = (100, 255, 100) if total_value > 0 else (255, 100, 100) if total_value < 0 else (200, 200, 200)
    total_text = title_font.render(f"{total_value:+.1f}", True, total_color)
    total_rect = total_text.get_rect(right=panel_width - 15, y=y_offset)
    panel.blit(total_text, total_rect)
    
    surface.blit(panel, (panel_x, panel_y))

def draw_training_info(surface, episode, steps, reward, epsilon, loss):
    """Draw training info overlay (simple stats box)"""
    font = pygame.font.SysFont('Arial', 20)
    info_surface = pygame.Surface((300, 140))
    info_surface.set_alpha(200)
    info_surface.fill((50, 50, 50))
    surface.blit(info_surface, (surface.get_width() - 310, 10))
    
    text_color = (255, 255, 255)
    texts = [
        f"Episode: {episode}",
        f"Steps: {steps}",
        f"Reward: {reward:.2f}",
        f"Epsilon: {epsilon:.2f}",
        f"Loss: {loss:.4f}" if loss is not None else "Loss: N/A"
    ]
    
    for i, text in enumerate(texts):
        text_surf = font.render(text, True, text_color)
        surface.blit(text_surf, (surface.get_width() - 300, 20 + i * 25))