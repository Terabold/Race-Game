import pygame
from Constants import *

def font_scale(size, Font=FONT):
    return pygame.font.Font(Font, size)

def draw_finished(environment):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    environment.surface.blit(overlay, (0, 0))
    
    texts = [
        (font_scale(60).render("Race Finished!", True, GREEN), (WIDTH//2, HEIGHT//2 - 100))
    ]
    
    if environment.car1_active:
        status = "Finished!" if environment.car1_finished else "Time Up!"
        texts.append((font_scale(40).render(f"Player 1: {status}", True, DODGERBLUE),
                    (WIDTH//2, HEIGHT//2)))
    
    if environment.car2_active:
        status = "Finished!" if environment.car2_finished else "Time Up!"
        texts.append((font_scale(40).render(f"Player 2: {status}", True, RED),
                    (WIDTH//2, HEIGHT//2 + 50)))
    
    texts.append((font_scale(30).render("Press SPACE to restart", True, WHITE),
                (WIDTH//2, HEIGHT//2 + 120)))
    
    for text, pos in texts:
        rect = text.get_rect(center=pos)
        environment.surface.blit(text, rect)

def draw_countdown(environment, count):
    shadow = font_scale(175, COUNTDOWN_FONT).render(str(count), True, BLACK)
    shadow_surface = pygame.Surface(shadow.get_size(), pygame.SRCALPHA)
    shadow_surface.blit(shadow, (0, 0))
    shadow_surface.set_alpha(200)
    
    shadow_rect = shadow_surface.get_rect(center=(WIDTH // 2 + 5, HEIGHT // 2 + 5))
    text = font_scale(175, COUNTDOWN_FONT).render(str(count), True, RED)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    environment.surface.blits((
        (shadow_surface, shadow_rect),
        (text, text_rect)
    ))

def draw_pause_overlay(self):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    self.surface.blit(overlay, (0, 0))
    
    texts = [
        (font_scale(75).render("GAME PAUSED", True, GREEN), (WIDTH // 2, HEIGHT // 2 - 50)),
        (font_scale(30).render("Press ESC to Resume", True, WHITE), (WIDTH // 2, HEIGHT // 2 + 20)),
        (font_scale(30).render(f"Time Remaining: {self.remaining_time:.1f}", True, WHITE), 
         (WIDTH // 2, HEIGHT // 2 + 70))
    ]
    
    for text, pos in texts:
        rect = text.get_rect(center=pos)
        self.surface.blit(text, rect)

def draw_ui(self): 
    y_offset = 5
    if self.car1_active:
        timer_color = RED if self.car1_time < 1 and not self.car1_finished else GREEN
        timer_text = font_scale(27).render(
            f"P1 Time: {self.car1_time:.1f}" if not self.car1_finished else "P1: Finished!", 
            True, 
            timer_color
        )
        self.surface.blit(timer_text, (10, y_offset))
        y_offset += 30
        
    if self.car2_active:
        timer_color = RED if self.car2_time < 1 and not self.car2_finished else GREEN
        timer_text = font_scale(27).render(
            f"P2 Time: {self.car2_time:.1f}" if not self.car2_finished else "P2: Finished!", 
            True, 
            timer_color
        )
        self.surface.blit(timer_text, (10, y_offset))