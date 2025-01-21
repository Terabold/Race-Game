import pygame
from Constants import *
import random

class TimeBonus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(TIME_BONUS_IMAGE).convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))  # Fixed size
        
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        
    def generate_bonuses(self, track_name, num_bonuses=10):
        bonus_group = pygame.sprite.Group()
        
        if track_name not in TRACK_BONUS_POINTS:
            return bonus_group
            
        available_positions = list(TRACK_BONUS_POINTS[track_name])
        if not available_positions:
            return bonus_group
            
        random.shuffle(available_positions)
        
        selected_positions = available_positions[:num_bonuses]
        
        for x, y in selected_positions:
            bonus = TimeBonus(x, y)
            bonus_group.add(bonus)
            
        return bonus_group