import pygame
from Constants import *
import random
import math
class TimeBonus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load and scale the time bonus image
        self.image = pygame.image.load(TIME_BONUS_IMAGE).convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))  # Larger size for better visibility
        
        # Add subtle pulsing animation
        self.original_image = self.image
        self.pulse_timer = 0
        self.pulse_speed = 0.1
        self.pulse_scale = 1.0
        
        # Center the rect on the given position
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        
    def update(self):
        # Create subtle pulsing effect
        self.pulse_timer += self.pulse_speed
        self.pulse_scale = 1.0 + 0.1 * abs(math.sin(self.pulse_timer))
        
        # Scale the image for pulsing effect
        scaled_size = (int(32 * self.pulse_scale), int(32 * self.pulse_scale))
        self.image = pygame.transform.scale(self.original_image, scaled_size)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.mask = pygame.mask.from_surface(self.image)

    def generate_bonuses(self, track_name, num_bonuses=10):
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