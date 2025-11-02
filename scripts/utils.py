import pygame
import os
import math
from scripts.Constants import *
from pathlib import Path


# ============================================================================
# FONT AND TEXT UTILITIES
# ============================================================================

def font_scale(size, Font=FONT):
    """Create scaled font"""
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


# ============================================================================
# SOUND LOADING
# ============================================================================

def load_sound(path, volume=DEFAULT_SOUND_VOLUME):
    """Load pygame Sound"""
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    
    sound = pygame.mixer.Sound(str(Path(path)))
    sound.set_volume(volume)
    return sound


# ============================================================================
# UI CONSTANTS CALCULATION
# ============================================================================

def calculate_ui_constants(display_size):
    """Calculate UI scaling constants based on display size"""
    ref_width, ref_height = 1920, 1080
    width_scale = display_size[0] / ref_width
    height_scale = display_size[1] / ref_height
    general_scale = min(width_scale, height_scale)
    
    return {
        'BUTTON_HEIGHT': int(80 * height_scale),
        'BUTTON_MIN_WIDTH': int(200 * width_scale),
        'BUTTON_TEXT_PADDING': int(40 * general_scale),
        'BUTTON_SPACING': int(20 * general_scale),
        'BUTTON_COLOR': (40, 40, 70, 220),
        'BUTTON_HOVER_COLOR': (60, 60, 100, 240),
        'BUTTON_GLOW_COLOR': (100, 150, 255),
        'GRID_COLUMNS': 5,
        'MAPS_PER_PAGE': 20,
    }


# ============================================================================
# GAME DRAWING FUNCTIONS
# ============================================================================

def draw_finished(environment):
    """Draw race finished overlay"""
    current_time = pygame.time.get_ticks() / 1000
    
    # Dark overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    environment.surface.blit(overlay, (0, 0))
    
    # Title
    title_font = font_scale(80, FONT)
    title_text = create_shadowed_text("Race Finished!", title_font, GREEN, BLACK, 5)
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 120))
    environment.surface.blit(title_text, title_rect)
    
    # Player 1 status
    if environment.car1_active:
        status = "Finished!" if environment.car1_finished else "Time Up!"
        p1_text = create_shadowed_text(f"Player 1: {status}", font_scale(42, FONT), DODGERBLUE)
        p1_rect = p1_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
        environment.surface.blit(p1_text, p1_rect)
    
    # Player 2 status
    if environment.car2_active:
        status = "Finished!" if environment.car2_finished else "Time Up!"
        p2_text = create_shadowed_text(f"Player 2: {status}", font_scale(42, FONT), RED)
        p2_rect = p2_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
        environment.surface.blit(p2_text, p2_rect)
    
    # Restart prompt (pulsing)
    restart_font = font_scale(36, FONT)
    restart_text = restart_font.render("Press SPACE to restart", True, WHITE)
    alpha = int(255 * smooth_sine_wave(current_time, period=1.2, min_val=0.0, max_val=1.0))
    restart_text_with_alpha = restart_text.copy()
    restart_text_with_alpha.set_alpha(alpha)
    restart_rect = restart_text_with_alpha.get_rect(center=(WIDTH//2, HEIGHT//2 + 140))
    environment.surface.blit(restart_text_with_alpha, restart_rect)


def draw_failed(environment):
    """Draw race failed overlay"""
    current_time = pygame.time.get_ticks() / 1000
    
    # Red-tinted overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    pygame.draw.rect(overlay, (255, 0, 0, 30), (0, 0, WIDTH, HEIGHT))
    environment.surface.blit(overlay, (0, 0))
    
    # Title
    title_font = font_scale(80, FONT)
    title_text = create_shadowed_text("Race Failed!", title_font, RED, BLACK, 5)
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 120))
    environment.surface.blit(title_text, title_rect)
    
    # Player 1 status
    if environment.car1_active:
        reason = "Crashed!" if environment.car1.failed else "Time Up!"
        p1_text = create_shadowed_text(f"Player 1: {reason}", font_scale(42, FONT), DODGERBLUE)
        p1_rect = p1_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
        environment.surface.blit(p1_text, p1_rect)
    
    # Player 2 status
    if environment.car2_active:
        reason = "Crashed!" if environment.car2.failed else "Time Up!"
        p2_text = create_shadowed_text(f"Player 2: {reason}", font_scale(42, FONT), RED)
        p2_rect = p2_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
        environment.surface.blit(p2_text, p2_rect)
    
    # Retry prompt (pulsing)
    restart_font = font_scale(36, FONT)
    restart_text = restart_font.render("Press SPACE to try again", True, WHITE)
    alpha = int(255 * smooth_sine_wave(current_time, period=1.8, min_val=0.1, max_val=1.0))
    restart_text_with_alpha = restart_text.copy()
    restart_text_with_alpha.set_alpha(alpha)
    restart_rect = restart_text_with_alpha.get_rect(center=(WIDTH//2, HEIGHT//2 + 140))
    environment.surface.blit(restart_text_with_alpha, restart_rect)


def draw_pause_overlay(environment):
    """Draw pause overlay"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    environment.surface.blit(overlay, (0, 0))
    
    # Pause title
    title_font = font_scale(80, FONT)
    title_text = create_shadowed_text("GAME PAUSED", title_font, GREEN, BLACK, 5)
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 70))
    environment.surface.blit(title_text, title_rect)
    
    # Resume instruction
    resume_text = create_shadowed_text("Press ESC to Resume", font_scale(34, FONT), WHITE)
    resume_rect = resume_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
    environment.surface.blit(resume_text, resume_rect)
    
    # Time remaining
    time_color = GREEN if environment.remaining_time > 10 else (YELLOW if environment.remaining_time > 3 else RED)
    time_text = create_shadowed_text(
        f"Time Remaining: {environment.remaining_time:.1f}", 
        font_scale(34, FONT), time_color
    )
    time_rect = time_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
    environment.surface.blit(time_text, time_rect)


def draw_ui(environment):
    """Draw game UI (timers, status)"""
    y_offset = 10
    
    # Player 1 timer
    if environment.car1_active:
        if environment.car1.failed:
            status_text = "Failed!"
            timer_color = RED
        elif environment.car1_finished:
            status_text = "P1: Finished!"
            timer_color = GREEN
        else:
            status_text = f"P1 Time: {environment.car1_time:.1f}"
            timer_color = RED if environment.car1_time < 3 else GREEN
        
        timer_text = create_shadowed_text(status_text, font_scale(32, FONT), timer_color)
        environment.surface.blit(timer_text, (15, y_offset))
        y_offset += 40
    
    # Player 2 timer
    if environment.car2_active:
        if environment.car2.failed:
            status_text = "Failed!"
            timer_color = RED
        elif environment.car2_finished:
            status_text = "P2: Finished!"
            timer_color = GREEN
        else:
            status_text = f"P2 Time: {environment.car2_time:.1f}"
            timer_color = RED if environment.car2_time < 3 else GREEN
        
        timer_text = create_shadowed_text(status_text, font_scale(32, FONT), timer_color)
        environment.surface.blit(timer_text, (15, y_offset))


def draw_countdown(environment, count):
    """Draw countdown number"""
    # Shadow
    shadow = font_scale(180, COUNTDOWN_FONT).render(str(count), True, BLACK)
    shadow_surface = pygame.Surface(shadow.get_size(), pygame.SRCALPHA)
    shadow_surface.blit(shadow, (0, 0))
    shadow_surface.set_alpha(200)
    shadow_rect = shadow_surface.get_rect(center=(WIDTH // 2 + 6, HEIGHT // 2 + 6))
    
    # Main text
    text = font_scale(180, COUNTDOWN_FONT).render(str(count), True, RED)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    environment.surface.blit(shadow_surface, shadow_rect)
    environment.surface.blit(text, text_rect)


# ============================================================================
# MENU BUTTON CLASS
# ============================================================================

class Button:
    """Simple button for menus"""
    def __init__(self, rect, text, action, font, menu, bg_color=None):
        self.rect = rect
        self.text = text
        self.action = action
        self.font = font
        self.menu = menu
        self.selected = False
        self.previously_selected = False
        self.bg_color = bg_color
        self.border_radius = max(6, int(rect.height * 0.1))

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def update_hover_state(self, mouse_pos):
        self.previously_selected = self.selected
        self.selected = self.is_hovered(mouse_pos)
        return self.selected and not self.previously_selected

    def draw(self, surface):
        # Background
        if self.bg_color:
            button_color = self.bg_color if not self.selected else tuple(min(c + 30, 255) for c in self.bg_color)
        else:
            button_color = (70, 70, 70) if not self.selected else (100, 100, 100)
        
        pygame.draw.rect(surface, button_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, border_radius=self.border_radius)
        
        # Text
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


# ============================================================================
# MENU SCREEN BASE CLASS
# ============================================================================

class MenuScreen:
    """Base class for menu screens"""
    def __init__(self, menu, title="Menu"):
        self.menu = menu
        self.screen = menu.screen
        self.UI_CONSTANTS = calculate_ui_constants(DISPLAY_SIZE)
        self.font = pygame.font.Font(FONT, 40)
        self.title_font = pygame.font.Font(FONT, 70)
        self.enabled = False
        self.title = title
        self.buttons = []

    def enable(self):
        self.enabled = True
        self.initialize()

    def disable(self):
        self.enabled = False

    def initialize(self):
        """Override in subclass"""
        pass

    def update(self, events):
        """Handle input"""
        if not self.enabled:
            return
        
        mouse_pos = pygame.mouse.get_pos()
        
        for button in self.buttons:
            button.update_hover_state(mouse_pos)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self.buttons:
                    if button.selected:
                        button.action()
                        return

    def draw(self, surface):
        """Draw menu"""
        if not self.enabled:
            return
        
        # Title
        title_text = self.title_font.render(self.title, True, (255, 255, 255))
        title_x = (surface.get_width() - title_text.get_width()) // 2
        title_y = int(surface.get_height() * 0.1)
        surface.blit(title_text, (title_x, title_y))
        
        # Buttons
        for button in self.buttons:
            button.draw(surface)

    def clear_buttons(self):
        self.buttons.clear()

    def create_button(self, text, action, x, y, width=None, bg_color=None):
        """Create a button"""
        if width is None:
            text_surf = self.font.render(text, True, (255, 255, 255))
            width = text_surf.get_width() + self.UI_CONSTANTS['BUTTON_TEXT_PADDING']
            width = max(width, self.UI_CONSTANTS['BUTTON_MIN_WIDTH'])
        
        button = Button(
            pygame.Rect(x, y, width, self.UI_CONSTANTS['BUTTON_HEIGHT']),
            text, action, self.font, self.menu, bg_color
        )
        self.buttons.append(button)
        return button