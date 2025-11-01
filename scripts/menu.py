import pygame
import sys
from scripts.Constants import *
from scripts.utils import MenuScreen, calculate_ui_constants
from scripts.GameManager import game_state_manager
from pathlib import Path

class Menu:
    def __init__(self, screen, clock):
        pygame.font.init()

        self.screen = screen
        self.clock = clock
        self.display_size = (WIDTH, HEIGHT)
        self.font_path = MENUFONT

        self.UI_CONSTANTS = calculate_ui_constants(self.display_size)

        self.background = pygame.image.load(MENU)
        self.background = pygame.transform.scale(self.background, self.display_size)

        # Initialize menus
        self.main_menu = MainMenuScreen(self)
        self.settings_menu = RaceSettingsScreen(self)

        self.active_menu = self.main_menu
        self.main_menu.enable()

    def _show_settings_menu(self):
        self.main_menu.disable()
        self.settings_menu.enable()
        self.active_menu = self.settings_menu

    def _return_to_main(self):
        if self.active_menu == self.settings_menu:
            self.settings_menu.disable()
        self.main_menu.enable()
        self.active_menu = self.main_menu

    def _handle_escape(self):
        if self.active_menu == self.settings_menu:
            self._return_to_main()

    def start_game(self):
        """Start normal gameplay"""
        game_state_manager.training_mode = False
        game_state_manager.setState('game')

    def start_training(self):
        """Start AI training mode as separate state"""
        game_state_manager.training_mode = True
        game_state_manager.setState('training')

    def quit_game(self):
        pygame.time.delay(300)
        pygame.quit()
        sys.exit()

    def run(self):
        self.screen.blit(self.background, (0, 0))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._handle_escape()

        self.clock.tick(60)
        self.active_menu.update(events)
        self.active_menu.draw(self.screen)


class MainMenuScreen(MenuScreen):
    def initialize(self):
        self.title = "RACING GAME"
        self.clear_buttons()

        center_x = self.screen.get_width() // 2
        start_y = int(self.screen.get_height() * 0.3)
        button_width = int(self.screen.get_width() * 0.25)

        button_configs = [
            ('PLAY', self.menu._show_settings_menu, None),
            ('TRAIN AI', self.menu.start_training, (70, 100, 180)),
            ('QUIT', self.menu.quit_game, (200, 50, 50))
        ]

        for text, action, color in button_configs:
            self.create_button(
                text, action,
                center_x - button_width // 2,
                start_y,
                button_width,
                color
            )
            start_y += self.UI_CONSTANTS['BUTTON_HEIGHT'] + self.UI_CONSTANTS['BUTTON_SPACING']


class RaceSettingsScreen(MenuScreen):
    COLORS = {
        "title": "#ffb521",
        "p1_base": "#0080ff",
        "p2_base": "#ff0000",
        "button_hover": "#f0f0e8",
        "selected": "#ffba30",
        "inactive": "#565656",
        "text": "#333333",
        "start": "#5a9e44",
        "back": "#666666",
        "border": "#e0e0d8"
    }

    CAR_COLOR_NAMES = ["Red", "Blue", "Black", "Yellow", "White"]

    def __init__(self, menu):
        super().__init__(menu, "Race Settings")

        self.car_images = self._load_car_images()

        self.info_font = pygame.font.Font(
            self.menu.font_path,
            int(self.screen.get_height() * 0.02)
        )
        self.header_font = pygame.font.Font(
            self.menu.font_path,
            int(self.screen.get_height() * 0.025)
        )

        self.player1_buttons = []
        self.player2_buttons = []
        self.p1_car_buttons = []
        self.p2_car_buttons = []

    def _load_car_images(self):
        car_images = {}
        for color_name in self.CAR_COLOR_NAMES:
            path = CAR_COLORS.get(color_name)
            if not path:
                continue
            p = Path(path)
            if not p.exists():
                continue
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

        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()
        center_x = screen_w // 2

        col_offset = int(screen_w * 0.12)
        car_offset = int(screen_w * 0.16)

        p1_x = center_x - col_offset
        p2_x = center_x + col_offset
        p1_car_x = center_x - car_offset - col_offset
        p2_car_x = center_x + car_offset + col_offset

        button_width = int(screen_w * 0.15)
        car_button_width = int(screen_w * 0.1)
        button_height = self.UI_CONSTANTS['BUTTON_HEIGHT']

        player_section_top = int(screen_h * 0.20)
        section_spacing = button_height + int(self.UI_CONSTANTS['BUTTON_SPACING'] * 0.8)

        self._create_player_buttons(
            p1_x, p2_x, button_width,
            player_section_top, section_spacing
        )
        self._create_car_buttons(
            p1_car_x, p2_car_x, car_button_width,
            player_section_top, section_spacing
        )
        self._create_action_buttons(center_x, screen_w, screen_h)

    def _create_player_buttons(self, p1_x, p2_x, button_width, top_y, spacing):
        for i, text in enumerate(["Human", "DQN"]):
            y = top_y + (i + 1) * spacing

            def make_p1_callback(value):
                def callback():
                    self._toggle_player1(value)
                return callback

            btn1 = self.create_button(
                text,
                make_p1_callback(text),
                p1_x - button_width // 2,
                y,
                button_width
            )
            self.player1_buttons.append(btn1)

            def make_p2_callback(value):
                def callback():
                    self._toggle_player2(value)
                return callback

            btn2 = self.create_button(
                text,
                make_p2_callback(text),
                p2_x - button_width // 2,
                y,
                button_width
            )
            self.player2_buttons.append(btn2)

    def _create_car_buttons(self, p1_car_x, p2_car_x, car_button_width, top_y, spacing):
        """Create car color selection buttons"""
        for i, color in enumerate(self.CAR_COLOR_NAMES):
            y = top_y + (i + 1) * spacing

            def make_p1_car_callback(car_color):
                def callback():
                    self._select_p1_car(car_color)
                return callback

            btn1 = self.create_button(
                "",
                make_p1_car_callback(color),
                p1_car_x - car_button_width // 2,
                y,
                car_button_width
            )
            self.p1_car_buttons.append((btn1, color))

            def make_p2_car_callback(car_color):
                def callback():
                    self._select_p2_car(car_color)
                return callback

            btn2 = self.create_button(
                "",
                make_p2_car_callback(color),
                p2_car_x - car_button_width // 2,
                y,
                car_button_width
            )
            self.p2_car_buttons.append((btn2, color))

    def _create_action_buttons(self, center_x, screen_w, screen_h):
        """Create Start and Back buttons"""
        start_y = int(screen_h * 0.85)
        self.create_button(
            "Start",
            self._start_race,
            center_x - 150,
            start_y,
            300,
            (90, 158, 68)
        )

        back_x = int(screen_w * 0.02)
        back_y = int(screen_h * 0.02)
        back_width = int(screen_w * 0.08)
        self.create_button(
            "←",
            self.menu._return_to_main,
            back_x,
            back_y,
            back_width
        )

    # Player selection handlers
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
            self.menu.start_game()

    # Drawing methods
    def draw(self, surface):
        if not self.enabled:
            return

        self._draw_title(surface)
        self._draw_section_labels(surface)
        self._draw_all_buttons(surface)
        self._draw_controls_panels(surface)

    def _draw_title(self, surface):
        """Draw the screen title with shadow"""
        title_shadow = self.title_font.render(self.title, True, (0, 0, 0))
        title_text = self.title_font.render(
            self.title, True,
            self._hex_to_rgb(self.COLORS["title"])
        )

        title_x = (surface.get_width() - title_text.get_width()) // 2
        title_y = int(surface.get_height() * 0.05)
        shadow_offset = max(2, int(4 * (surface.get_height() / 1080)))

        surface.blit(title_shadow, (title_x + shadow_offset, title_y + shadow_offset))
        surface.blit(title_text, (title_x, title_y))

    def _draw_section_labels(self, surface):
        """Draw Player 1, Player 2, and Car labels"""
        screen_w = surface.get_width()
        center_x = screen_w // 2

        col_offset = int(screen_w * 0.12)
        car_offset = int(screen_w * 0.16)

        p1_x = center_x - col_offset
        p2_x = center_x + col_offset
        p1_car_x = center_x - car_offset - col_offset
        p2_car_x = center_x + car_offset + col_offset

        label_y = int(surface.get_height() * 0.22)

        labels = [
            ("Player 1", p1_x, self.COLORS["p1_base"]),
            ("Player 2", p2_x, self.COLORS["p2_base"]),
            ("Car", p1_car_x, self.COLORS["p1_base"]),
            ("Car", p2_car_x, self.COLORS["p2_base"])
        ]

        for text, x, color in labels:
            self._draw_text(
                surface, text, self.font,
                self._hex_to_rgb(color), x, label_y
            )

    def _draw_all_buttons(self, surface):
        """Draw all buttons with appropriate styling"""
        # Player type buttons
        for i, button in enumerate(self.player1_buttons):
            label_choices = ["Human", "DQN"]
            label = label_choices[i] if i < len(label_choices) else label_choices[-1]
            is_selected = game_state_manager.player1_selection == label
            self._draw_custom_button(
                surface, button, is_selected,
                self._hex_to_rgb(self.COLORS["p1_base"])
            )

        for i, button in enumerate(self.player2_buttons):
            label_choices = ["Human", "DQN"]
            label = label_choices[i] if i < len(label_choices) else label_choices[-1]
            is_selected = game_state_manager.player2_selection == label
            self._draw_custom_button(
                surface, button, is_selected,
                self._hex_to_rgb(self.COLORS["p2_base"])
            )

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

    def _draw_custom_button(self, surface, button, is_selected, base_color):
        """Draw a styled button with selection state"""
        color = base_color if is_selected else self._hex_to_rgb(self.COLORS["inactive"])

        # Background
        button_surface = pygame.Surface(
            (button.rect.width, button.rect.height),
            pygame.SRCALPHA
        )
        button_surface.fill(color)
        surface.blit(button_surface, (button.rect.x, button.rect.y))

        # Border
        pygame.draw.rect(
            surface,
            self._hex_to_rgb(self.COLORS["border"]),
            button.rect, 2
        )

        # Text
        text_color = (255, 255, 255) if is_selected else (180, 180, 180)
        text_surf = button.font.render(button.text, True, text_color)
        text_x = button.rect.x + (button.rect.width - text_surf.get_width()) // 2
        text_y = button.rect.y + (button.rect.height - text_surf.get_height()) // 2
        surface.blit(text_surf, (text_x, text_y))

    def _draw_car_button(self, surface, button, color, is_selected, is_disabled):
        """Draw a car selection button with car image"""
        bg_color = (
            self._hex_to_rgb(self.COLORS["button_hover"])
            if is_selected
            else self._hex_to_rgb(self.COLORS["inactive"])
        )

        # Background
        button_surface = pygame.Surface(
            (button.rect.width, button.rect.height),
            pygame.SRCALPHA
        )
        button_surface.fill(bg_color)
        surface.blit(button_surface, (button.rect.x, button.rect.y))

        # Disabled overlay
        if is_disabled:
            overlay = pygame.Surface((button.rect.width, button.rect.height))
            overlay.set_alpha(200)
            overlay.fill((51, 51, 51))
            surface.blit(overlay, (button.rect.x, button.rect.y))

        # Border
        pygame.draw.rect(
            surface,
            self._hex_to_rgb(self.COLORS["border"]),
            button.rect, 2
        )

        # Car image
        if color in self.car_images:
            car_image = self.car_images[color]
            car_rect = car_image.get_rect(center=button.rect.center)
            surface.blit(car_image, car_rect)

    def _draw_controls_panels(self, surface):
        """Draw control info panels for selected players"""
        screen_w = surface.get_width()
        screen_h = surface.get_height()

        panel_y = int(screen_h * 0.5)
        left_x = int(screen_w * 0.12)
        right_x = int(screen_w * 0.88)

        if game_state_manager.player1_selection:
            self._draw_controls_info(surface, left_x, panel_y, True)

        if game_state_manager.player2_selection:
            self._draw_controls_info(surface, right_x, panel_y, False)

    def _draw_controls_info(self, surface, x, y, is_player_one):
        """Draw the controls information panel"""
        controls = {
            'Player 1': {
                'Forward': 'W',
                'Backward': 'S',
                'Left': 'A',
                'Right': 'D'
            },
            'Player 2': {
                'Forward': 'Up',
                'Backward': 'Down',
                'Left': 'Left',
                'Right': 'Right'
            }
        }

        player = 'Player 1' if is_player_one else 'Player 2'
        control_set = controls[player]
        primary_color = (
            self._hex_to_rgb(self.COLORS["p1_base"])
            if is_player_one
            else self._hex_to_rgb(self.COLORS["p2_base"])
        )

        # Panel dimensions
        box_width = 200
        box_height = 250
        box_rect = pygame.Rect(x - box_width // 2, y - box_height // 2, box_width, box_height)

        # Backdrop with layers
        for i in range(3):
            backdrop = pygame.Surface((box_width - i * 2, box_height - i * 2))
            backdrop.set_alpha(100 - i * 20)
            backdrop.fill(primary_color)
            surface.blit(backdrop, (box_rect.x + i, box_rect.y + i))

        # Border
        pygame.draw.rect(
            surface,
            self._hex_to_rgb(self.COLORS["border"]),
            box_rect, 3
        )

        # Title
        title_y = box_rect.y + 25
        self._draw_text(
            surface, "Controls", self.info_font,
            self._hex_to_rgb(self.COLORS["button_hover"]),
            x, title_y
        )

        # Control keys
        spacing = 45
        start_y = title_y + spacing + 10
        key_width = 60
        key_height = 35
        small_font = pygame.font.Font(self.menu.font_path, 12)

        for i, (action, key) in enumerate(control_set.items()):
            action_y = start_y + i * spacing

            # Action label
            self._draw_text(
                surface, action, small_font,
                self._hex_to_rgb(self.COLORS["button_hover"]),
                x - 45, action_y
            )

            # Key box
            key_x = x + 45
            key_rect = pygame.Rect(
                key_x - key_width // 2,
                action_y - key_height // 2,
                key_width, key_height
            )

            key_bg = pygame.Surface((key_width, key_height))
            key_bg.set_alpha(160)
            key_bg.fill(primary_color)
            surface.blit(key_bg, key_rect)

            pygame.draw.rect(
                surface,
                self._hex_to_rgb(self.COLORS["border"]),
                key_rect, 2
            )

            # Key text
            self._draw_text(
                surface, key, small_font,
                self._hex_to_rgb(self.COLORS["button_hover"]),
                key_x, action_y
            )

    def _draw_text(self, surface, text, font, color, x, y):
        """Helper to draw centered text"""
        render = font.render(text, True, color)
        text_rect = render.get_rect(center=(x, y))
        surface.blit(render, text_rect)

    def _hex_to_rgb(self, hex_color):
        """Convert hex color string to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def update(self, events):
        """Handle user input"""
        if not self.enabled:
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