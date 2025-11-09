# menu.py - FIXED with proper initialization
import pygame
import sys
from scripts.Constants import *
from scripts.utils import MenuScreen, calculate_ui_constants
from scripts.GameManager import game_state_manager
from pathlib import Path


class MainMenu:
    """Main Menu Screen Handler"""
    def __init__(self, screen, clock):
        pygame.font.init()
        self.screen = screen
        self.clock = clock
        self.display_size = (WIDTH, HEIGHT)
        self.font_path = MENUFONT
        self.UI_CONSTANTS = calculate_ui_constants(self.display_size)

        # Background
        self.background = pygame.transform.scale(
            pygame.image.load(MENU), 
            self.display_size
        )

        # Initialize menu screen
        self.menu_screen = MainMenuScreen(self)
        self.menu_screen.enable()  # FIXED: Enable on init

    def quit_game(self):
        pygame.time.delay(300)
        pygame.quit()
        sys.exit()

    def run(self):
        """Main menu render loop"""
        self.screen.blit(self.background, (0, 0))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.quit_game()

        self.clock.tick(60)
        self.menu_screen.update(events)
        self.menu_screen.draw(self.screen)


class SettingsMenu:
    """Settings Menu Screen Handler"""
    def __init__(self, screen, clock):
        pygame.font.init()
        self.screen = screen
        self.clock = clock
        self.display_size = (WIDTH, HEIGHT)
        self.font_path = MENUFONT
        self.UI_CONSTANTS = calculate_ui_constants(self.display_size)

        # Background
        self.background = pygame.transform.scale(
            pygame.image.load(MENU), 
            self.display_size
        )

        # Initialize menu screen
        self.menu_screen = RaceSettingsScreen(self)
        self.menu_screen.enable()  # FIXED: Enable on init

    def run(self):
        """Settings menu render loop"""
        self.screen.blit(self.background, (0, 0))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.time.delay(300)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Return to main menu
                game_state_manager.setState('main_menu')

        self.clock.tick(60)
        self.menu_screen.update(events)
        self.menu_screen.draw(self.screen)


# ============================================================================
# MENU SCREEN IMPLEMENTATIONS
# ============================================================================

class MainMenuScreen(MenuScreen):
    """Main Menu UI"""
    def initialize(self):
        self.title = "RACING GAME"
        self.clear_buttons()

        # Layout constants
        center_x = self.screen.get_width() // 2
        start_y = int(self.screen.get_height() * 0.3)
        button_width = int(self.screen.get_width() * 0.25)
        spacing = self.UI_CONSTANTS['BUTTON_HEIGHT'] + self.UI_CONSTANTS['BUTTON_SPACING']

        # Button configurations: (text, action, color)
        buttons = [
            ('PLAY', lambda: game_state_manager.setState('settings_menu'), GREEN),
            ('TRAIN AI', lambda: game_state_manager.setState('training'), (70, 100, 180)),
            ('QUIT', self.menu.quit_game, (200, 50, 50))
        ]

        for i, (text, action, color) in enumerate(buttons):
            self.create_button(
                text, action,
                center_x - button_width // 2,
                start_y + i * spacing,
                button_width,
                color
            )


class RaceSettingsScreen(MenuScreen):
    """Race Settings UI"""
    # UI Colors
    COLORS = {
        "title": (255, 181, 33),
        "p1": (0, 128, 255),
        "p2": (255, 0, 0),
        "selected": (255, 186, 48),
        "inactive": (86, 86, 86),
        "border": (224, 224, 216),
        "button_bg": (240, 240, 232),
        "start": (90, 158, 68),
        "back": (102, 102, 102)
    }
    
    CAR_COLORS_LIST = ["Red", "Blue", "Black", "Yellow", "White"]

    def __init__(self, menu):
        super().__init__(menu, "Race Settings")
        self.car_images = self._load_car_images()
        
        # Fonts
        self.info_font = pygame.font.Font(self.menu.font_path, int(self.screen.get_height() * 0.02))
        self.header_font = pygame.font.Font(self.menu.font_path, int(self.screen.get_height() * 0.025))
        
        # Button groups
        self.player1_buttons = []
        self.player2_buttons = []
        self.p1_car_buttons = []
        self.p2_car_buttons = []

    def _load_car_images(self):
        """Load and scale car images for display"""
        car_images = {}
        for color_name in self.CAR_COLORS_LIST:
            path = Path(CAR_COLORS[color_name])
            if path.exists():
                image = pygame.image.load(path)
                rotated = pygame.transform.rotate(image, 90)
                scaled = pygame.transform.scale(rotated, (50, 100))
                car_images[color_name] = pygame.transform.scale(scaled, (100, 50))
        return car_images

    def initialize(self):
        self.title = "Race Settings"
        self.clear_buttons()
        self.player1_buttons.clear()
        self.player2_buttons.clear()
        self.p1_car_buttons.clear()
        self.p2_car_buttons.clear()

        # Layout calculations
        screen_w, screen_h = self.screen.get_size()
        center_x = screen_w // 2
        
        # Column positions
        col_offset = int(screen_w * 0.12)
        car_offset = int(screen_w * 0.16)
        
        p1_x = center_x - col_offset
        p2_x = center_x + col_offset
        p1_car_x = center_x - car_offset - col_offset
        p2_car_x = center_x + car_offset + col_offset
        
        # Button dimensions
        button_width = int(screen_w * 0.15)
        car_button_width = int(screen_w * 0.1)
        
        # Vertical layout
        section_top = int(screen_h * 0.20)
        spacing = self.UI_CONSTANTS['BUTTON_HEIGHT'] + int(self.UI_CONSTANTS['BUTTON_SPACING'] * 0.8)

        # Create all buttons
        self._create_player_buttons(p1_x, p2_x, button_width, section_top, spacing)
        self._create_car_buttons(p1_car_x, p2_car_x, car_button_width, section_top, spacing)
        self._create_action_buttons(center_x, screen_w, screen_h)

    def _create_player_buttons(self, p1_x, p2_x, width, top_y, spacing):
        """Create player type selection buttons"""
        for i, player_type in enumerate(["Human", "DQN"]):
            y = top_y + (i + 1) * spacing
            
            # Player 1 button
            btn1 = self.create_button(
                player_type,
                lambda pt=player_type: self._toggle_player1(pt),
                p1_x - width // 2, y, width
            )
            self.player1_buttons.append(btn1)
            
            # Player 2 button
            btn2 = self.create_button(
                player_type,
                lambda pt=player_type: self._toggle_player2(pt),
                p2_x - width // 2, y, width
            )
            self.player2_buttons.append(btn2)

    def _create_car_buttons(self, p1_car_x, p2_car_x, width, top_y, spacing):
        """Create car color selection buttons"""
        for i, color in enumerate(self.CAR_COLORS_LIST):
            y = top_y + (i + 1) * spacing
            
            # Player 1 car button
            btn1 = self.create_button(
                "", 
                lambda c=color: self._select_p1_car(c),
                p1_car_x - width // 2, y, width
            )
            self.p1_car_buttons.append((btn1, color))
            
            # Player 2 car button
            btn2 = self.create_button(
                "",
                lambda c=color: self._select_p2_car(c),
                p2_car_x - width // 2, y, width
            )
            self.p2_car_buttons.append((btn2, color))

    def _create_action_buttons(self, center_x, screen_w, screen_h):
        """Create Start and Back buttons"""
        # Start button
        start_y = int(screen_h * 0.85)
        self.create_button(
            "Start", self._start_race,
            center_x - 150, start_y, 300,
            self.COLORS["start"]
        )
        
        # Back button
        back_x = int(screen_w * 0.02)
        back_y = int(screen_h * 0.02)
        back_width = int(screen_w * 0.08)
        self.create_button(
            "←", lambda: game_state_manager.setState('main_menu'),
            back_x, back_y, back_width
        )

    # === Event Handlers ===
    
    def _toggle_player1(self, selection):
        if game_state_manager.player1_selection == selection:
            game_state_manager.player1_selection = None
        else:
            game_state_manager.player1_selection = selection

    def _toggle_player2(self, selection):
        if game_state_manager.player2_selection == selection:
            game_state_manager.player2_selection = None
        else:
            game_state_manager.player2_selection = selection

    def _select_p1_car(self, color):
        if color != game_state_manager.player2_car_color:
            game_state_manager.player1_car_color = color

    def _select_p2_car(self, color):
        if color != game_state_manager.player1_car_color:
            game_state_manager.player2_car_color = color

    def _start_race(self):
        if game_state_manager.player1_selection or game_state_manager.player2_selection:
            game_state_manager.setState('game')

    # === Drawing ===
    
    def draw(self, surface):
        if not self.enabled:  # FIXED: Check enabled flag
            return
            
        self._draw_title(surface)
        self._draw_section_labels(surface)
        self._draw_all_buttons(surface)
        self._draw_controls_panels(surface)

    def _draw_title(self, surface):
        """Draw screen title with shadow"""
        title_text = self.title_font.render(self.title, True, self.COLORS["title"])
        title_shadow = self.title_font.render(self.title, True, (0, 0, 0))
        
        title_x = (surface.get_width() - title_text.get_width()) // 2
        title_y = int(surface.get_height() * 0.05)
        shadow_offset = max(2, int(4 * (surface.get_height() / 1080)))

        surface.blit(title_shadow, (title_x + shadow_offset, title_y + shadow_offset))
        surface.blit(title_text, (title_x, title_y))

    def _draw_section_labels(self, surface):
        """Draw column headers (Player 1, Player 2, Car labels)"""
        screen_w = surface.get_width()
        center_x = screen_w // 2
        col_offset = int(screen_w * 0.12)
        car_offset = int(screen_w * 0.16)
        label_y = int(surface.get_height() * 0.22)

        labels = [
            ("Player 1", center_x - col_offset, self.COLORS["p1"]),
            ("Player 2", center_x + col_offset, self.COLORS["p2"]),
            ("Car", center_x - car_offset - col_offset, self.COLORS["p1"]),
            ("Car", center_x + car_offset + col_offset, self.COLORS["p2"])
        ]

        for text, x, color in labels:
            text_surf = self.font.render(text, True, color)
            text_rect = text_surf.get_rect(center=(x, label_y))
            surface.blit(text_surf, text_rect)

    def _draw_all_buttons(self, surface):
        """Draw all interactive buttons"""
        # Player type buttons
        for i, button in enumerate(self.player1_buttons):
            player_type = ["Human", "DQN"][i]
            is_selected = game_state_manager.player1_selection == player_type
            self._draw_styled_button(surface, button, is_selected, self.COLORS["p1"])

        for i, button in enumerate(self.player2_buttons):
            player_type = ["Human", "DQN"][i]
            is_selected = game_state_manager.player2_selection == player_type
            self._draw_styled_button(surface, button, is_selected, self.COLORS["p2"])

        # Car selection buttons
        for button, color in self.p1_car_buttons:
            is_selected = game_state_manager.player1_car_color == color
            is_disabled = game_state_manager.player2_car_color == color
            self._draw_car_button(surface, button, color, is_selected, is_disabled)

        for button, color in self.p2_car_buttons:
            is_selected = game_state_manager.player2_car_color == color
            is_disabled = game_state_manager.player1_car_color == color
            self._draw_car_button(surface, button, color, is_selected, is_disabled)

        # Start and Back buttons
        for button in self.buttons[-2:]:
            button.draw(surface)

    def _draw_styled_button(self, surface, button, is_selected, base_color):
        """Draw player type button with selection state"""
        color = base_color if is_selected else self.COLORS["inactive"]
        
        # Background
        pygame.draw.rect(surface, color, button.rect)
        pygame.draw.rect(surface, self.COLORS["border"], button.rect, 2)
        
        # Text
        text_color = (255, 255, 255) if is_selected else (180, 180, 180)
        text_surf = button.font.render(button.text, True, text_color)
        text_rect = text_surf.get_rect(center=button.rect.center)
        surface.blit(text_surf, text_rect)

    def _draw_car_button(self, surface, button, color, is_selected, is_disabled):
        """Draw car selection button with car preview"""
        bg_color = self.COLORS["button_bg"] if is_selected else self.COLORS["inactive"]
        
        # Background
        pygame.draw.rect(surface, bg_color, button.rect)
        
        # Disabled overlay
        if is_disabled:
            overlay = pygame.Surface((button.rect.width, button.rect.height))
            overlay.set_alpha(200)
            overlay.fill((51, 51, 51))
            surface.blit(overlay, button.rect.topleft)
        
        # Border
        pygame.draw.rect(surface, self.COLORS["border"], button.rect, 2)
        
        # Car image
        if color in self.car_images:
            car_rect = self.car_images[color].get_rect(center=button.rect.center)
            surface.blit(self.car_images[color], car_rect)

    def _draw_controls_panels(self, surface):
        """Draw control info for active players"""
        screen_w, screen_h = surface.get_size()
        panel_y = int(screen_h * 0.5)
        
        if game_state_manager.player1_selection:
            left_x = int(screen_w * 0.08)
            self._draw_control_panel(surface, left_x, panel_y, is_player_one=True)
        
        if game_state_manager.player2_selection:
            right_x = int(screen_w * 0.92)
            self._draw_control_panel(surface, right_x, panel_y, is_player_one=False)

    def _draw_control_panel(self, surface, x, y, is_player_one):
        """Draw single control info panel"""
        # Control mappings
        controls = {
            True: {'Forward': 'W', 'Backward': 'S', 'Left': 'A', 'Right': 'D'},
            False: {'Forward': 'Up', 'Backward': 'Down', 'Left': 'Left', 'Right': 'Right'}
        }
        
        control_set = controls[is_player_one]
        primary_color = self.COLORS["p1"] if is_player_one else self.COLORS["p2"]
        
        # Panel dimensions
        box_w, box_h = 200, 250
        box_rect = pygame.Rect(x - box_w // 2, y - box_h // 2, box_w, box_h)
        
        # Backdrop layers
        for i in range(3):
            backdrop = pygame.Surface((box_w - i * 2, box_h - i * 2))
            backdrop.set_alpha(100 - i * 20)
            backdrop.fill(primary_color)
            surface.blit(backdrop, (box_rect.x + i, box_rect.y + i))
        
        # Border
        pygame.draw.rect(surface, self.COLORS["border"], box_rect, 3)
        
        # Title
        title = self.info_font.render("Controls", True, self.COLORS["button_bg"])
        title_rect = title.get_rect(center=(x, box_rect.y + 25))
        surface.blit(title, title_rect)
        
        # Control keys
        spacing = 45
        start_y = box_rect.y + 80
        key_w, key_h = 60, 35
        small_font = pygame.font.Font(self.menu.font_path, 12)
        
        for i, (action, key) in enumerate(control_set.items()):
            action_y = start_y + i * spacing
            
            # Action label (left)
            action_text = small_font.render(action, True, self.COLORS["button_bg"])
            action_rect = action_text.get_rect(center=(x - 45, action_y))
            surface.blit(action_text, action_rect)
            
            # Key box (right)
            key_x = x + 45
            key_rect = pygame.Rect(key_x - key_w // 2, action_y - key_h // 2, key_w, key_h)
            
            key_bg = pygame.Surface((key_w, key_h))
            key_bg.set_alpha(160)
            key_bg.fill(primary_color)
            surface.blit(key_bg, key_rect)
            pygame.draw.rect(surface, self.COLORS["border"], key_rect, 2)
            
            # Key text
            key_text = small_font.render(key, True, self.COLORS["button_bg"])
            key_text_rect = key_text.get_rect(center=(key_x, action_y))
            surface.blit(key_text, key_text_rect)

    def update(self, events):
        """Handle user input"""
        if not self.enabled:  # FIXED: Check enabled flag
            return
            
        mouse_pos = pygame.mouse.get_pos()
        
        # Update hover states
        for button in self.buttons:
            button.update_hover_state(mouse_pos)
        
        # Handle clicks
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self.buttons:
                    if button.selected:
                        button.action()
                        return