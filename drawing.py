import pygame
from Constants import *
import math
def font_scale(size, Font=FONT):
    return pygame.font.Font(Font, size)

def create_shadowed_text(text, font, color, shadow_color=BLACK, offset=4):
    shadow = font.render(text, True, shadow_color)
    main_text = font.render(text, True, color)
    
    combined = pygame.Surface((shadow.get_width() + offset, shadow.get_height() + offset), pygame.SRCALPHA)
    combined.blit(shadow, (offset, offset))
    combined.blit(main_text, (0, 0))
    return combined

def smooth_sine_wave(time, period=4.0, min_val=0.0, max_val=1.0):
    normalized = (math.cos(time * (2 * math.pi / period)) + 1) / 2
    return min_val + normalized * (max_val - min_val)

def draw_finished(environment):
    current_time = pygame.time.get_ticks() / 1000
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    environment.surface.blit(overlay, (0, 0))
    
    title_font = font_scale(80, FONT)
    title_text = create_shadowed_text("Race Finished!", title_font, GREEN, BLACK, 5)
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 120))
    environment.surface.blit(title_text, title_rect)
    
    if environment.car1_active:
        status = "Finished!" if environment.car1_finished else "Time Up!"
        p1_text = create_shadowed_text(f"Player 1: {status}", font_scale(42, FONT), DODGERBLUE)
        p1_rect = p1_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
        environment.surface.blit(p1_text, p1_rect)
    
    if environment.car2_active:
        status = "Finished!" if environment.car2_finished else "Time Up!"
        p2_text = create_shadowed_text(f"Player 2: {status}", font_scale(42, FONT), RED)
        p2_rect = p2_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
        environment.surface.blit(p2_text, p2_rect)
    
    restart_font = font_scale(36, FONT)
    restart_text = restart_font.render("Press SPACE to restart", True, WHITE)
    alpha = int(255 * smooth_sine_wave(current_time, period=1.2, min_val=0.0, max_val=1.0))
    restart_text_with_alpha = restart_text.copy()
    restart_text_with_alpha.set_alpha(alpha)
    restart_rect = restart_text_with_alpha.get_rect(center=(WIDTH//2, HEIGHT//2 + 140))
    environment.surface.blit(restart_text_with_alpha, restart_rect)

def draw_failed(environment):
    current_time = pygame.time.get_ticks() / 1000
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    
    pygame.draw.rect(overlay, (255, 0, 0, 30), (0, 0, WIDTH, HEIGHT))
    
    environment.surface.blit(overlay, (0, 0))
    
    title_font = font_scale(80, FONT)
    title_text = create_shadowed_text("Race Failed!", title_font, RED, BLACK, 5)
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 120))
    environment.surface.blit(title_text, title_rect)
    
    if environment.car1_active:
        reason = "Crashed!" if environment.car1.failed else "Time Up!"
        p1_text = create_shadowed_text(f"Player 1: {reason}", font_scale(42, FONT), DODGERBLUE)
        p1_rect = p1_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
        environment.surface.blit(p1_text, p1_rect)
    
    if environment.car2_active:
        reason = "Crashed!" if environment.car2.failed else "Time Up!"
        p2_text = create_shadowed_text(f"Player 2: {reason}", font_scale(42, FONT), RED)
        p2_rect = p2_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
        environment.surface.blit(p2_text, p2_rect)
    
    restart_font = font_scale(36, FONT)
    restart_text = restart_font.render("Press SPACE to try again", True, WHITE)
    alpha = int(255 * smooth_sine_wave(current_time, period=1.8, min_val=0.1, max_val=1.0))
    restart_text_with_alpha = restart_text.copy()
    restart_text_with_alpha.set_alpha(alpha)
    restart_rect = restart_text_with_alpha.get_rect(center=(WIDTH//2, HEIGHT//2 + 140))
    environment.surface.blit(restart_text_with_alpha, restart_rect)

def draw_pause_overlay(environment):
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    
    environment.surface.blit(overlay, (0, 0))
    
    title_font = font_scale(80, FONT)
    title_text = create_shadowed_text("GAME PAUSED", title_font, GREEN, BLACK, 5)
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 70))
    environment.surface.blit(title_text, title_rect)
    
    resume_text = create_shadowed_text("Press ESC to Resume", font_scale(34, FONT), WHITE)
    resume_rect = resume_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
    environment.surface.blit(resume_text, resume_rect)
    
    time_color = GREEN if environment.remaining_time > 10 else (
                YELLOW if environment.remaining_time > 3 else RED)
    time_text = create_shadowed_text(
        f"Time Remaining: {environment.remaining_time:.1f}", 
        font_scale(34, FONT), time_color
    )
    time_rect = time_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
    environment.surface.blit(time_text, time_rect)

def draw_ui(environment):
    y_offset = 10  
    
    if environment.car1_active:
        if environment.car1.failed:
            status_text = "Failed!"
            timer_color = RED
        elif environment.car1_finished:
            status_text = "P1: Finished!"
            timer_color = GREEN
        else:
            status_text = f"P1 Time: {environment.car1_time:.1f}"
            if environment.car1_time < 3:
                timer_color = RED
            else:
                timer_color = GREEN
        
        timer_text = create_shadowed_text(status_text, font_scale(32, FONT), timer_color)
        environment.surface.blit(timer_text, (15, y_offset))
        y_offset += 40  
        
    if environment.car2_active:
        if environment.car2.failed:
            status_text = "Failed!"
            timer_color = RED
        elif environment.car2_finished:
            status_text = "P2: Finished!"
            timer_color = GREEN
        else:
            status_text = f"P2 Time: {environment.car2_time:.1f}"
            if environment.car2_time < 3:
                timer_color = RED
            else:
                timer_color = GREEN
        
        timer_text = create_shadowed_text(status_text, font_scale(32, FONT), timer_color)
        environment.surface.blit(timer_text, (15, y_offset))

def draw_countdown(environment, count):
    shadow = font_scale(180, COUNTDOWN_FONT).render(str(count), True, BLACK)
    shadow_surface = pygame.Surface(shadow.get_size(), pygame.SRCALPHA)
    shadow_surface.blit(shadow, (0, 0))
    shadow_surface.set_alpha(200)
    
    shadow_rect = shadow_surface.get_rect(center=(WIDTH // 2 + 6, HEIGHT // 2 + 6))
    text = font_scale(180, COUNTDOWN_FONT).render(str(count), True, RED)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    environment.surface.blits((
        (shadow_surface, shadow_rect),
        (text, text_rect)
    ))