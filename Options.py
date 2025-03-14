import pygame
import sys
from Constants import *

class GameMenu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((MENUWIDTH, MENUHEIGHT))
        pygame.display.set_caption("Race Settings")
        
        self.background = pygame.image.load(MENU)
        
        self.font_big = pygame.font.Font(MENUFONT, 25)
        self.font_small = pygame.font.Font(MENUFONT, 20)
        self.font_title = pygame.font.Font(MENUFONT, 60)  

        self.player1_active = False
        self.player2_active = False

        self.ai_train_mode = False  
        self.player1_selection = None
        self.player2_selection = None
        self.player1_car_color = "Blue"
        self.player2_car_color = "Red"  

        # Softer color palette with more saturated green and less harsh white
        self.colors = {
            "title": "#b68f40",    # Gold/bronze from launcher
            "p1_base": "#4a7bac",  # More vibrant blue
            "p2_base": "#ac4a4a",  # More vibrant red
            "button_base": "#d7fcd4", # From launcher
            "button_hover": "#f0f0e8", # Softer off-white instead of pure white
            "selected": "#b68f40",  # Gold/bronze to match title
            "inactive": "#565656",  # Darker gray
            "text": "#333333",     # Dark gray instead of BLACK
            "start": "#5a9e44",    # More saturated green
            "back": "#666666",     # Soft dark gray
            "border": "#e0e0d8"    # Off-white for borders instead of pure white
        }

        self.car_images = {}
        for color, path in CAR_COLORS.items():
            image = pygame.image.load(path)
            rotated_image = pygame.transform.rotate(image, 90)
            self.car_images[color] = pygame.transform.scale(rotated_image, (50, 100))
        
        for color in self.car_images:
            self.car_images[color] = pygame.transform.scale(self.car_images[color], (100, 50))

    def create_car_button(self, x, y, width, height, color, is_selected, is_disabled=False):
        rect = pygame.Rect(x - width//2, y - height//2, width, height)
        
        if is_selected:
            pygame.draw.rect(self.screen, self.colors["button_hover"], rect)
        else:
            pygame.draw.rect(self.screen, self.colors["inactive"], rect)
        
        if is_disabled:
            s = pygame.Surface((width, height))
            s.set_alpha(200)  
            s.fill(self.colors["text"])  
            self.screen.blit(s, (rect.x, rect.y))
        pygame.draw.rect(self.screen, self.colors["border"], rect, 2)  
        
        car_image = self.car_images[color]
        car_rect = car_image.get_rect(center=rect.center)
        self.screen.blit(car_image, car_rect)
        return rect

    def draw_controls_info(self, x, y, is_player_one):
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
        primary_color = self.colors["p1_base"] if is_player_one else self.colors["p2_base"]
        
        box_height = 250
        box_width = 200  
        box_rect = pygame.Rect(x - box_width//2, y, box_width, box_height)
        
        for i in range(3):
            s = pygame.Surface((box_width - i*2, box_height - i*2))
            s.set_alpha(100 - i*20)
            s.fill(primary_color)
            self.screen.blit(s, (box_rect.x + i, box_rect.y + i))
        
        pygame.draw.rect(self.screen, self.colors["border"], box_rect, 3)
        
        title_y = y + 25
        self.draw_text("Controls", self.font_small, self.colors["button_hover"], x, title_y)
        
        spacing = 45  
        start_y = title_y + spacing + 10
        key_width = 60  
        key_height = 35  
        
        for i, (action, key) in enumerate(control_set.items()):
            self.draw_text(action, pygame.font.Font(MENUFONT, 12), self.colors["button_hover"], x - 45, start_y + i * spacing) 
            
            key_x = x + 45 
            
            key_y = start_y + i * spacing - key_height//2
            
            key_rect = pygame.Rect(key_x - key_width//2, key_y, key_width, key_height)
            s = pygame.Surface((key_width, key_height))
            s.set_alpha(160)
            s.fill(primary_color)
            self.screen.blit(s, key_rect)
            pygame.draw.rect(self.screen, self.colors["border"], key_rect, 2)
            
            self.draw_text(key, pygame.font.Font(MENUFONT, 12), self.colors["button_hover"], key_x, start_y + i * spacing)

    def draw_text(self, text, font, color, x, y):
        render = font.render(text, True, color)
        text_rect = render.get_rect(center=(x, y))
        self.screen.blit(render, text_rect)

    def create_radio_button(self, x, y, selected):
        radius = 20  
        color = self.colors["selected"] if selected else self.colors["inactive"]
        pygame.draw.circle(self.screen, color, (x, y), radius)
        pygame.draw.circle(self.screen, self.colors["border"], (x, y), radius, 2)
        return pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)

    def create_button(self, x, y, width, height, text, color, disabled=False):
        rect = pygame.Rect(x - width//2, y - height//2, width, height)
        
        if disabled:
            s = pygame.Surface((width, height))
            s.set_alpha(128)
            s.fill(color)
            self.screen.blit(s, (rect.x, rect.y))
        else:
            pygame.draw.rect(self.screen, color, rect)
        
        pygame.draw.rect(self.screen, self.colors["border"], rect, 2)
        
        text_color = self.colors["inactive"] if disabled else self.colors["button_hover"]
        text_surface = self.font_big.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        return rect
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        button_width, button_height = 220, 80 
        car_button_width, car_button_height = 130, 80  
        center_x = MENUWIDTH // 2
        
        p1_x = center_x - 125  
        p2_x = center_x + 125  
        
        p1_car_x = p1_x - 195  
        p2_car_x = p2_x + 195  
        
        player_section_top = 185  
        section_spacing = 90 
        
        controls_p1_x = 130 
        controls_p2_x = MENUWIDTH - 130 
        controls_y = 290 

        start_button_y = MENUHEIGHT - 90
        back_button_x = 100  
        back_button_y = 50  
        
        while running:
            self.screen.blit(self.background, (0,0))
            
            self.draw_text("Race Settings", self.font_title, self.colors["text"], center_x + 3, 78)
            self.draw_text("Race Settings", self.font_title, self.colors["title"], center_x, 75)
            
            if self.player1_selection:
                self.draw_controls_info(controls_p1_x, controls_y, True)
            if self.player2_selection:
                self.draw_controls_info(controls_p2_x, controls_y, False)

            self.draw_text("Player 1", self.font_small, self.colors["p1_base"], p1_x, player_section_top)
            player1_buttons = [
                self.create_button(
                    p1_x, 
                    player_section_top + (i + 1) * section_spacing,
                    button_width, 
                    button_height, 
                    text, 
                    self.colors["p1_base"] if self.player1_selection == text else self.colors["inactive"]
                )
                for i, text in enumerate(["Human", "DQN"])   
            ]
            
            self.draw_text("Car", self.font_small, self.colors["p1_base"], p1_car_x, player_section_top)
            p1_color_buttons = [
                self.create_car_button(
                    p1_car_x,
                    player_section_top + (i + 1) * section_spacing,
                    car_button_width,
                    car_button_height,
                    color,
                    self.player1_car_color == color,
                    color == self.player2_car_color
                )
                for i, color in enumerate(["Red", "Blue", "Green", "Yellow", "ice"])
            ]
            
            self.draw_text("Player 2", self.font_small, self.colors["p2_base"], p2_x, player_section_top)
            player2_buttons = [
                self.create_button(
                    p2_x, 
                    player_section_top + (i + 1) * section_spacing,
                    button_width, 
                    button_height, 
                    text, 
                    self.colors["p2_base"] if self.player2_selection == text else self.colors["inactive"]
                )
                for i, text in enumerate(["Human", "DQN"]) 
            ]
            
            self.draw_text("Car", self.font_small, self.colors["p2_base"], p2_car_x, player_section_top)
            p2_color_buttons = [
                self.create_car_button(
                    p2_car_x,
                    player_section_top + (i + 1) * section_spacing,
                    car_button_width,
                    car_button_height,
                    color,
                    self.player2_car_color == color,
                    color == self.player1_car_color
                )
                for i, color in enumerate(["Red", "Blue", "Green", "Yellow", "ice"])
            ]

            start_button = self.create_button(center_x, start_button_y, 300, 100, "Start Race", self.colors["start"])
            
            back_button = self.create_button(back_button_x, back_button_y, 150, 60, "Back", self.colors["back"])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    
                    if back_button.collidepoint(mouse_pos):
                        return None 
                    
                    for i, rect in enumerate(player1_buttons):
                        if rect.collidepoint(mouse_pos):
                            if self.player1_selection == ["Human", "DQN"][i]:
                                self.player1_selection = None
                            else:
                                self.player1_selection = ["Human", "DQN"][i]
                    
                    for i, rect in enumerate(p1_color_buttons):
                        if rect.collidepoint(mouse_pos) and ["Red", "Blue", "Green", "Yellow", "ice"][i] != self.player2_car_color:
                            self.player1_car_color = ["Red", "Blue", "Green", "Yellow", "ice"][i]

                    for i, rect in enumerate(player2_buttons):
                        if rect.collidepoint(mouse_pos):
                            if self.player2_selection == ["Human", "DQN"][i]:
                                self.player2_selection = None
                            else:
                                self.player2_selection = ["Human", "DQN"][i]

                    for i, rect in enumerate(p2_color_buttons):
                        if rect.collidepoint(mouse_pos) and ["Red", "Blue", "Green", "Yellow", "ice"][i] != self.player1_car_color:
                            self.player2_car_color = ["Red", "Blue", "Green", "Yellow", "ice"][i]

                    if start_button.collidepoint(mouse_pos):
                        if self.player1_selection or self.player2_selection:
                            return {
                                'player1': self.player1_selection, 
                                'player2': self.player2_selection,
                                'car_color1': self.player1_car_color,
                                'car_color2': self.player2_car_color
                            }
            
            pygame.display.flip()
            clock.tick(60)