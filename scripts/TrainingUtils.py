import numpy as np
import pygame
import math
from scripts.Constants import *

# ============================================================================
# REWARD CALCULATION
# ============================================================================

def calculate_reward(environment, collision=False, just_finished=False, action=None, hit_obstacle=False, timeout=False, episode=0, **kwargs):
    """
    Dynamic reward calculation with progressive speed targeting.
    Gradually shift from rewarding 0.90 speed to 1.0 speed over 5000 episodes.
    """
    car = environment.car
    
    breakdown = {
        'speed': 0.0,
        'edge': 0.0,
        'time': 0.0,
        'finish': 0.0,
        'collision': 0.0,
        'timeout': 0.0,
        'total': 0.0
    }

    # TERMINAL REWARDS
    if just_finished:
        breakdown['finish'] = 250.0
        breakdown['total'] = 250.0
        return breakdown
    
    if collision:
        breakdown['collision'] = -200.0
        breakdown['total'] = -200.0
        return breakdown
    
    if timeout:
        breakdown['timeout'] = -400.0
        breakdown['total'] = -400.0
        return breakdown
    
    # STEP REWARDS
    
    # PROGRESSIVE SPEED TARGETING
    # Calculate target speed ratio that increases from 0.90 to 1.0 over episodes
    start_episode = 3067  # Your current episode
    target_episode = start_episode + 5000  # 5000 episodes from now = 8067
    
    # Linear progression from 0.90 to 1.0
    if episode < start_episode:
        target_speed_ratio = 0.90
    elif episode >= target_episode:
        target_speed_ratio = 1.0
    else:
        # Interpolate between 0.90 and 1.0
        progress = (episode - start_episode) / (target_episode - start_episode)
        target_speed_ratio = 0.90 + (0.10 * progress)
    
    # Current speed ratio - ensure it's always positive and clamp to valid range
    speed_ratio = abs(car.velocity / car.max_velocity)
    speed_ratio = max(0.0, min(1.5, speed_ratio))  # Clamp between 0 and 1.5
    
    # Reward based on how close we are to target speed
    # Maximum reward when at or above target speed
    if speed_ratio >= target_speed_ratio:
        # At or above target - full reward with exponential scaling
        breakdown['speed'] = 2.0 * (speed_ratio ** 1.5)
    else:
        # Below target - reduced reward based on distance from target
        speed_performance = speed_ratio / target_speed_ratio if target_speed_ratio > 0 else 0.0
        breakdown['speed'] = 2.0 * (speed_performance ** 2) * (speed_ratio ** 1.5)
    
    # EDGE - Keep minimal to avoid conflicting with speed incentive
    min_ray = min(car.ray_distances) if car.ray_distances else 0
    min_ray_normalized = min_ray / car.ray_length
    if min_ray_normalized < 0.10:
        breakdown['edge'] = -1.0
    elif min_ray_normalized < 0.20:
        breakdown['edge'] = -0.2
    else:
        breakdown['edge'] = 0.05
    
    # TIME - Small constant penalty
    breakdown['time'] = -0.2

    # Calculate total
    breakdown['total'] = sum(breakdown.values())
    
    return breakdown


# ============================================================================
# TRAINING STATISTICS
# ============================================================================

def save_training_stats(episode, rewards, losses, epsilon, filename="training_stats.csv"):
    """Save training statistics to CSV"""
    import csv
    import os
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Episode', 'Reward', 'Avg_Loss', 'Epsilon'])
        avg_loss = np.mean(losses) if losses else 0
        writer.writerow([episode, rewards, avg_loss, epsilon])


# ============================================================================
# TRAINING DRAWING FUNCTIONS
# ============================================================================

def font_scale(size, Font=FONT):
    """Helper to create scaled fonts"""
    return pygame.font.Font(Font, size)

def create_shadowed_text(text, font, color, shadow_color=BLACK, offset=4):
    """Create text with shadow effect"""
    shadow = font.render(text, True, shadow_color)
    main_text = font.render(text, True, color)
    
    combined = pygame.Surface((shadow.get_width() + offset, shadow.get_height() + offset), pygame.SRCALPHA)
    combined.blit(shadow, (offset, offset))
    combined.blit(main_text, (0, 0))
    return combined

def smooth_sine_wave(time, period=4.0, min_val=0.0, max_val=1.0):
    """Generate smooth sine wave for animations"""
    normalized = (math.cos(time * (2 * math.pi / period)) + 1) / 2
    return min_val + normalized * (max_val - min_val)

def draw_ai_environment_ui(environment):
    """Draw UI specifically for AI training environment"""
    y_offset = 10
    
    # Draw status
    if hasattr(environment, 'car_finished') and environment.car_finished:
        status_text = "FINISHED!"
        timer_color = GREEN
    elif hasattr(environment, 'car_crashed') and environment.car_crashed:
        status_text = "CRASHED!"
        timer_color = RED
    elif hasattr(environment, 'car_timeout') and environment.car_timeout:
        status_text = "TIMEOUT!"
        timer_color = ORANGE
    else:
        status_text = f"Training..."
        timer_color = WHITE
    
    status_font = font_scale(28, FONT)
    status_text_surface = create_shadowed_text(status_text, status_font, timer_color)
    environment.surface.blit(status_text_surface, (WIDTH - status_text_surface.get_width() - 20, y_offset))
    
    # Draw speed info
    if hasattr(environment, 'car'):
        speed_ratio = environment.car.velocity / environment.car.max_velocity
        speed_text = f"Speed: {speed_ratio:.1%}"
        speed_color = GREEN if speed_ratio > 0.7 else YELLOW if speed_ratio > 0.3 else RED
        
        speed_surface = create_shadowed_text(speed_text, status_font, speed_color)
        environment.surface.blit(speed_surface, (WIDTH - speed_surface.get_width() - 20, y_offset + 40))

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
        f"Speed: {reward_breakdown['speed']:+.1f}",
        f"Edge: {reward_breakdown['edge']:+.1f}",
        f"Time: {reward_breakdown['time']:+.1f}"
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
    """Draw reward breakdown overlay with target speed indicator"""
    if episode_reward_breakdown is None:
        return
    
    panel_width = 250
    panel_height = 280
    panel_x = surface.get_width() - panel_width - 10
    panel_y = 100
    
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((30, 30, 40, 220))
    pygame.draw.rect(panel, (100, 100, 120), (0, 0, panel_width, panel_height), 2)
    
    title_font = pygame.font.SysFont('Arial', 18, bold=True)
    item_font = pygame.font.SysFont('Arial', 16)
    small_font = pygame.font.SysFont('Arial', 14)
    
    title = title_font.render("Reward Breakdown", True, (255, 255, 255))
    panel.blit(title, (10, 10))
    pygame.draw.line(panel, (100, 100, 120), (10, 35), (panel_width - 10, 35), 1)
    
    y_offset = 45
    line_height = 20
    
    # Calculate current target speed
    start_episode = 3067
    target_episode = start_episode + 5000
    if current_episode < start_episode:
        target_speed = 0.90
    elif current_episode >= target_episode:
        target_speed = 1.0
    else:
        progress = (current_episode - start_episode) / (target_episode - start_episode)
        target_speed = 0.90 + (0.10 * progress)
    
    # Show target speed
    target_text = small_font.render(f"Target Speed: {target_speed:.2f}", True, (150, 200, 255))
    panel.blit(target_text, (15, y_offset))
    y_offset += line_height
    
    items = [
        ('Speed', 'speed', (100, 200, 100)),
        ('Edge', 'edge', (255, 150, 100)),
        ('Time', 'time', (150, 150, 150)),
        ('Finish', 'finish', (100, 255, 100)),
        ('Collision', 'collision', (255, 50, 50)),
        ('Timeout', 'timeout', (255, 100, 50)),
    ]
    
    for label, key, color in items:
        value = episode_reward_breakdown.get(key, 0.0)
        
        # Ensure value is a real float
        if isinstance(value, complex):
            value = value.real
        value = float(value)
        
        if abs(value) < 0.01 and key not in ['speed', 'edge', 'time']:
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