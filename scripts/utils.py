import pygame
import os
from scripts.Constants import *
from scripts.GameManager import game_state_manager
from pathlib import Path
import math
# Helper dummy sound to avoid initializing or playing audio when not desired
class DummySound:
    def __init__(self):
        pass
    def play(self, *args, **kwargs):
        return None
    def set_volume(self, *args, **kwargs):
        return None
    def stop(self, *args, **kwargs):
        return None

def scale_position(x_percent, y_percent, display_size):
    return (int(display_size[0] * x_percent), int(display_size[1] * y_percent))

def scale_size(width_percent, height_percent, display_size):
    return (int(display_size[0] * width_percent), int(display_size[1] * height_percent))

def play_ui_sound(sound_list):
    if sound_list:
        sound_list[0].play()

def scale_font(base_size, display_size, reference_size=REFERENCE_SIZE):
    width_ratio = display_size[0] / reference_size[0]
    height_ratio = display_size[1] / reference_size[1]
    scale_factor = (width_ratio * height_ratio) ** 0.5
    scaled_size = max(MIN_FONT_SIZE, min(MAX_FONT_SIZE, int(base_size * scale_factor)))
    return scaled_size

def calculate_ui_constants(display_size):
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

def load_image(path, scale=None, remove_color=DEFAULT_REMOVE_COLOR):
    img_path = Path(BASE_IMG_PATH) / path
    img = pygame.image.load(str(img_path)).convert()
    if remove_color is not None:
        img.set_colorkey(remove_color)
    if scale is not None:
        img = pygame.transform.scale(img, scale)
    return img

def load_images(path, scale=None, remove_color=DEFAULT_REMOVE_COLOR):
    dir_path = Path(BASE_IMG_PATH) / path
    images = []
    for img_path in sorted(dir_path.iterdir()):
        if img_path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.bmp'):
            relative_path = img_path.relative_to(BASE_IMG_PATH)
            images.append(load_image(str(relative_path), scale, remove_color))
    return images

def load_sound(path, volume=DEFAULT_SOUND_VOLUME):
    """
    Load a pygame Sound if possible; otherwise return a DummySound.
    Tries to initialize the mixer if it is not initialized yet. If initialization
    or loading fails, returns DummySound rather than raising.
    This function is used by Environment.setup_sound and elsewhere.
    """
    # If mixer not initialized, try to initialize it (so countdown/music can play)
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except Exception:
            return DummySound()

    sound_path = Path(path)
    if not sound_path.exists() or not sound_path.is_file():
        return DummySound()

    if sound_path.suffix.lower() not in SOUND_EXTENSIONS:
        return DummySound()

    try:
        snd = pygame.mixer.Sound(str(sound_path))
        snd.set_volume(volume)
        return snd
    except Exception:
        return DummySound()

def load_sounds(path, volume=DEFAULT_SOUND_VOLUME):
    dir_path = Path(path)
    sounds = []
    if not dir_path.exists() or not dir_path.is_dir():
        return sounds
    for snd_path in sorted(dir_path.iterdir()):
        if snd_path.suffix.lower() in SOUND_EXTENSIONS:
            sound = load_sound(str(snd_path), volume)
            sounds.append(sound)
    return sounds

class Button:
    def __init__(self, rect, text, action, font, menu, bg_color=None):
        self.rect = rect
        self.text = text
        self.action = action
        self.font = font
        self.menu = menu
        self.selected = False
        self.previously_selected = False
        self.bg_color = bg_color
        # Menus purposely silent for simplicity
        self.hover_sounds = []
        self.click_sounds = []
        self.border_radius = max(6, int(rect.height * 0.1))

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def just_hovered(self):
        return self.selected and not self.previously_selected

    def update_hover_state(self, mouse_pos):
        self.previously_selected = self.selected
        self.selected = self.is_hovered(mouse_pos)
        if self.just_hovered():
            play_ui_sound(self.hover_sounds)
        return self.just_hovered()

    def handle_click(self, event):
        if self.selected and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            play_ui_sound(self.click_sounds)
            self.action()
            return True
        return False

    def draw(self, surface):
        # Simplified flat button design
        if self.bg_color:
            button_color = self.bg_color if not self.selected else tuple(min(c + 30, 255) for c in self.bg_color)
        else:
            button_color = (70, 70, 70) if not self.selected else (100, 100, 100)
        pygame.draw.rect(surface, button_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, border_radius=self.border_radius)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_x = self.rect.x + (self.rect.width - text_surf.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - text_surf.get_height()) // 2
        surface.blit(text_surf, (text_x, text_y))

class MenuScreen:
    def __init__(self, menu, title="Menu"):
        self.menu = menu
        self.screen = menu.screen
        self.UI_CONSTANTS = calculate_ui_constants(DISPLAY_SIZE)
        font_size = scale_font(40, DISPLAY_SIZE)
        title_font_size = scale_font(70, DISPLAY_SIZE)
        self.font = pygame.font.Font(FONT, font_size)
        self.title_font = pygame.font.Font(FONT, title_font_size)
        self.enabled = False
        self.title = title
        self.buttons = []

    def enable(self):
        self.enabled = True
        self.initialize()

    def disable(self):
        self.enabled = False

    def initialize(self):
        pass

    def update(self, events):
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
        if not self.enabled:
            return
        title_text = self.title_font.render(self.title, True, (255, 255, 255))
        title_x = (surface.get_width() - title_text.get_width()) // 2
        title_y = int(surface.get_height() * 0.1)
        surface.blit(title_text, (title_x, title_y))
        for button in self.buttons:
            button.draw(surface)

    def clear_buttons(self):
        self.buttons.clear()

    def create_button(self, text, action, x, y, width=None, bg_color=None):
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

    def create_centered_button_list(self, button_texts, button_actions, center_x, start_y, bg_colors=None):
        max_width = self.UI_CONSTANTS['BUTTON_MIN_WIDTH']
        for text in button_texts:
            text_surf = self.font.render(text, True, (255, 255, 255))
            width = text_surf.get_width() + self.UI_CONSTANTS['BUTTON_TEXT_PADDING']
            max_width = max(max_width, width)
        left_x = center_x - (max_width // 2)
        for i, (text, action) in enumerate(zip(button_texts, button_actions)):
            bg_color = None
            if bg_colors and i < len(bg_colors):
                bg_color = bg_colors[i]
            y_pos = start_y + i * (self.UI_CONSTANTS['BUTTON_HEIGHT'] + self.UI_CONSTANTS['BUTTON_SPACING'])
            self.create_button(text, action, left_x, y_pos, max_width, bg_color)

    def create_grid_buttons(self, texts, actions, start_x, start_y, fixed_width=None, bg_colors=None):
        if fixed_width is None:
            fixed_width = self.UI_CONSTANTS['BUTTON_MIN_WIDTH']
        columns = self.UI_CONSTANTS['GRID_COLUMNS']
        for i, (text, action) in enumerate(zip(texts, actions)):
            bg_color = None
            if bg_colors and i < len(bg_colors):
                bg_color = bg_colors[i]
            row = i // columns
            col = i % columns
            button_x = start_x + col * (fixed_width + self.UI_CONSTANTS['BUTTON_SPACING'])
            button_y = start_y + row * (self.UI_CONSTANTS['BUTTON_HEIGHT'] + self.UI_CONSTANTS['BUTTON_SPACING'])
            self.create_button(text, action, button_x, button_y, fixed_width, bg_color)
            
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