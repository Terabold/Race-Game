import pygame
import os
from scripts.Constants import *  
from scripts.GameManager import game_state_manager
from pathlib import Path


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
    sound_path = Path('data') / 'sfx' / path
    sound = pygame.mixer.Sound(str(sound_path))
    sound.set_volume(volume)
    return sound

def load_sounds(path, volume=DEFAULT_SOUND_VOLUME):
    dir_path = Path('data') / 'sfx' / path
    sounds = []
    for snd_path in sorted(dir_path.iterdir()):
        if snd_path.suffix.lower() in SOUND_EXTENSIONS:
            relative_path = snd_path.relative_to(Path('data') / 'sfx')
            sound = load_sound(str(relative_path), volume)
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
        self.hover_sounds = load_sounds('hover', volume=0.04)
        self.click_sounds = load_sounds('click', volume=0.15)
        self.border_radius = max(6, int(rect.height * 0.1))
        display_height = pygame.display.get_surface().get_height()
        self.shadow_offset = max(2, int(4 * (display_height / 1080)))

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
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        shadow_color = (255, 255, 255, 90) if self.selected else (0, 0, 0, 90)
        shadow_surface.fill(shadow_color)
        surface.blit(shadow_surface, (self.rect.x + self.shadow_offset, self.rect.y + self.shadow_offset))
        # Button background
        if self.bg_color:
            if self.selected:
                button_color = tuple(min(c + 40, 255) for c in self.bg_color)
            else:
                button_color = self.bg_color
        else:
            button_color = (
                self.menu.UI_CONSTANTS['BUTTON_HOVER_COLOR'] if self.selected
                else self.menu.UI_CONSTANTS['BUTTON_COLOR']
            )
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        button_surface.fill(button_color)
        surface.blit(button_surface, (self.rect.x, self.rect.y))
        # Text with shadow
        text_shadow = self.font.render(self.text, True, (0, 0, 0, 180))
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_x = self.rect.x + (self.rect.width - text_surf.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - text_surf.get_height()) // 2
        text_shadow_offset = max(1, int(2 * pygame.display.get_surface().get_height() / 1080))
        surface.blit(text_shadow, (text_x + text_shadow_offset, text_y + text_shadow_offset))
        surface.blit(text_surf, (text_x, text_y))
        # Highlight border if selected
        if self.selected:
            glow_color = self.menu.UI_CONSTANTS['BUTTON_GLOW_COLOR']
            display_width = pygame.display.get_surface().get_width()
            glow_size = max(2, int(3 * (display_width / 1920)))
            for i in range(glow_size, 0, -1):
                alpha = 60 - i * 10
                glow_rect = self.rect.inflate(i * 4, i * 4)
                glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    glow_surface,
                    tuple(list(glow_color) + [alpha]),
                    glow_surface.get_rect(),
                    border_radius=self.border_radius
                )
                surface.blit(glow_surface, (
                    self.rect.x - i * 2,
                    self.rect.y - i * 2
                ))

class MenuScreen:
    def __init__(self, menu, title="Menu"):
        self.menu = menu
        self.screen = menu.screen
        self.UI_CONSTANTS = calculate_ui_constants(DISPLAY_SIZE)
        self.click_sounds = load_sounds('click', volume=0.15)
        font_size = scale_font(40, DISPLAY_SIZE)
        title_font_size = scale_font(70, DISPLAY_SIZE)
        self.font = pygame.font.Font(FONT, font_size)
        self.title_font = pygame.font.Font(FONT, title_font_size)
        self.enabled = False
        self.title = title
        self.buttons = []
        self.music_path = 'data/sfx/music/menu.ogg'
        self.play_music()

    def play_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load(str(self.music_path))
        pygame.mixer.music.set_volume(0.2) 
        pygame.mixer.music.play(-1) 

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
        for button in self.buttons:
            if button.selected:
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        button.action()
                        play_ui_sound(self.click_sounds)
                        return

    def draw(self, surface):
        if not self.enabled:
            return
        # Title with shadow
        title_shadow = self.title_font.render(self.title, True, (0, 0, 0))
        title_text = self.title_font.render(self.title, True, (255, 255, 255))
        title_x = (surface.get_width() - title_text.get_width()) // 2
        title_y = int(surface.get_height() * 0.1)
        shadow_offset = max(2, int(4 * (surface.get_height() / 1080)))
        surface.blit(title_shadow, (title_x + shadow_offset, title_y + shadow_offset))
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
            
