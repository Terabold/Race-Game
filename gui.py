import pygame
import sys
from Constants import *

class GameMenu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Race Game Menu")
        
        # Font setup
        self.font_big = pygame.font.Font(FONT, 45)
        self.font_big = pygame.font.Font(FONT, 45)
        self.font_small = pygame.font.Font(FONT, 33)
        
        # Selections
        self.sound_enabled = True
        self.auto_respawn = True
        self.player1_selection = None
        self.player2_selection = None
        self.player1_car_color = "Red"
        self.player2_car_color = "Red"  # For future use
        self.music_enabled = True  # Music toggle state

        # Music setup
        pygame.mixer.init()
        self.music_file = LOBBY_MUSIC
        pygame.mixer.music.load(self.music_file)
        pygame.mixer.music.set_volume(0.02)  # Default volume
        pygame.mixer.music.play(-1)  # Loop music

    def draw_text(self, text, font, color, x, y):
        render = font.render(text, True, color)
        text_rect = render.get_rect(center=(x, y))
        self.screen.blit(render, text_rect)

    def create_radio_button(self, x, y, selected):
        """Creates a radio button."""
        color = GREEN if selected else FOGGRAY
        pygame.draw.circle(self.screen, color, (x, y), 15)
        pygame.draw.circle(self.screen, BLACK, (x, y), 15, 2)

    def create_button(self, x, y, width, height, text, color, disabled=False):
        rect = pygame.Rect(x - width//2, y - height//2, width, height)
        
        # Draw button with reduced alpha if disabled
        if disabled:
            s = pygame.Surface((width, height))
            s.set_alpha(128)
            s.fill(color)
            self.screen.blit(s, (rect.x, rect.y))
        else:
            pygame.draw.rect(self.screen, color, rect)
        
        pygame.draw.rect(self.screen, BLACK, rect, 2)
        
        text_color = FOGGRAY if disabled else BLACK
        text_surface = self.font_small.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        return rect
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        button_width, button_height = 200, 80
        color_button_width = 120  # Smaller width for color buttons
        center_x = WIDTH // 2
        
        # Vertical spacing
        player_section_top = 150
        section_spacing = 90
        settings_section_y = HEIGHT - 300
        start_button_y = HEIGHT - 125

        while running:
            # Load and scale background
            background = pygame.image.load(MENU).convert()
            background = pygame.transform.scale(background, (WIDTH, HEIGHT))
            self.screen.blit(background, (0, 0))
            
            # Title
            self.draw_text("Race Game Car-Drift", self.font_big, DODGERBLUE, center_x, 50)
            
            # Player 1 Section
            self.draw_text("Player 1", self.font_small, BLACK, center_x - 300, player_section_top)
            
            # Player 1 Type Selection
            player1_buttons = [
                self.create_button(
                    center_x - 300, 
                    player_section_top + (i + 1) * section_spacing,
                    button_width, 
                    button_height, 
                    text, 
                    GREEN if self.player1_selection == text else GRAY
                )
                for i, text in enumerate(["Human", "DQN", "Min_Max", "Alpha_Beta"])
            ]
            
            # Player 1 Car Color Selection (horizontally to the left)
            self.draw_text("Car Color", self.font_small, BLACK, center_x - 500, player_section_top + section_spacing)
            p1_color_buttons = [
                self.create_button(
                    center_x - 500,
                    player_section_top + (i + 2) * section_spacing,
                    color_button_width,
                    button_height,
                    color,
                    GREEN if self.player1_car_color == color else GRAY
                )
                for i, color in enumerate(["Red", "Blue", "Green", "Yellow", "ice"])
            ]
            
            # Player 2 Section (Disabled for now)
            self.draw_text("Player 2 (Coming Soon)", self.font_small, FOGGRAY, center_x + 300, player_section_top)
            
            # Player 2 Type Selection (Disabled)
            player2_buttons = [
                self.create_button(
                    center_x + 300, 
                    player_section_top + (i + 1) * section_spacing,
                    button_width, 
                    button_height, 
                    text, 
                    GRAY,
                    disabled=True
                )
                for i, text in enumerate(["Human", "DQN", "Min_Max", "Alpha_Beta"])
            ]
            
            # Player 2 Car Color Selection (horizontally to the right, disabled)
            self.draw_text("Car Color", self.font_small, FOGGRAY, center_x + 500, player_section_top + section_spacing)
            p2_color_buttons = [
                self.create_button(
                    center_x + 500,
                    player_section_top + (i + 2) * section_spacing,
                    color_button_width,
                    button_height,
                    color,
                    GRAY,
                    disabled=True
                )
                for i, color in enumerate(["Red", "Blue", "Green", "Yellow", "ice"])
            ]
            
            # Settings toggles in the same row
            self.draw_text("Lobby Music", self.font_small, BLACK, center_x - 200, settings_section_y)
            self.create_radio_button(center_x - 200, settings_section_y + 50, self.music_enabled)

            self.draw_text("Game Sound", self.font_small, BLACK, center_x, settings_section_y)
            self.create_radio_button(center_x, settings_section_y + 50, self.sound_enabled)

            self.draw_text("Auto Respawn", self.font_small, BLACK, center_x + 200, settings_section_y)
            self.create_radio_button(center_x + 200, settings_section_y + 50, self.auto_respawn)

            # Start Button (at the bottom)
            start_button = self.create_button(center_x, start_button_y, 500, 150, "Start Race", GREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    
                    # Check Player 1 buttons
                    for i, rect in enumerate(player1_buttons):
                        if rect.collidepoint(mouse_pos):
                            self.player1_selection = ["Human", "DQN", "Min_Max", "Alpha_Beta"][i]
                    
                    # Check Player 1 Car Color buttons
                    for i, rect in enumerate(p1_color_buttons):
                        if rect.collidepoint(mouse_pos):
                            self.player1_car_color = ["Red", "Blue", "Green", "Yellow", "ice"][i]
                    
                    # Music toggle
                    if pygame.Rect(center_x - 215, settings_section_y + 35, 30, 30).collidepoint(mouse_pos):
                        self.music_enabled = not self.music_enabled
                        if self.music_enabled:
                            pygame.mixer.music.play(-1)
                        else:
                            pygame.mixer.music.stop()

                    # Sound toggle
                    if pygame.Rect(center_x - 15, settings_section_y + 35, 30, 30).collidepoint(mouse_pos):
                        self.sound_enabled = not self.sound_enabled

                    # Auto Respawn toggle
                    if pygame.Rect(center_x + 185, settings_section_y + 35, 30, 30).collidepoint(mouse_pos):
                        self.auto_respawn = not self.auto_respawn
                    
                    # Start game
                    if start_button.collidepoint(mouse_pos):
                        if self.player1_selection:
                            pygame.mixer.music.stop()
                            return {
                                'player1': self.player1_selection,
                                'player2': None,  # For future use
                                'sound_enabled': self.sound_enabled,
                                'auto_respawn': self.auto_respawn,
                                'car_color': self.player1_car_color
                            }
                        else:
                            print("Please select options for Player 1.")
            
            pygame.display.flip()
            clock.tick(60)
