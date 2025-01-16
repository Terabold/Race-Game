import pygame
import random
from Constants import *

class TimeBonus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create a larger, more visible bonus sprite
        size = 15  # Increased size
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw a gold square with a black border
        pygame.draw.rect(self.image, GOLD, (0, 0, size, size))
        pygame.draw.rect(self.image, BLACK, (0, 0, size, size), 2)
        
        # Add a larger "+" symbol in the center
        font = pygame.font.Font(None, 30)  # Larger font
        plus_text = font.render("+", True, BLACK)
        plus_rect = plus_text.get_rect(center=(size/2, size/2))
        self.image.blit(plus_text, plus_rect)
        
        # Center the rect on the given position
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def generate_bonuses(self, track_name, num_bonuses=10):
        """Generate a specified number of randomly placed time bonuses"""
        bonus_group = pygame.sprite.Group()
        
        if track_name not in TRACK_BONUS_POINTS:
            return bonus_group
            
        # Get available positions for this track
        available_positions = list(TRACK_BONUS_POINTS[track_name])
        if not available_positions:
            return bonus_group
            
        random.shuffle(available_positions)
        
        # Take only the requested number of positions
        selected_positions = available_positions[:num_bonuses]
        
        # Create bonus sprites and add them to the group
        for x, y in selected_positions:
            bonus = TimeBonus(x, y)
            bonus_group.add(bonus)
            
        return bonus_group