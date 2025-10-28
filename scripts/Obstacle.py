import pygame
from scripts.Constants import *
import random

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, ai_mode=False):
        super().__init__()
        
        if ai_mode:
            # In AI mode, create a filled rectangle for the hitbox
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (255, 0, 0), (5, 5, 10, 10))  # Red filled hitbox
        else:
            # Normal mode, load the bomb image
            self.image = pygame.image.load(BOMB).convert_alpha() 
            self.image = pygame.transform.scale(self.image, (20, 20))
        
        # Hitbox mask (same for both modes)
        self.mask_surface = pygame.Surface((20, 20), pygame.SRCALPHA) 
        pygame.draw.rect(self.mask_surface, (255, 255, 255), (5, 5, 10, 10))
        self.mask = pygame.mask.from_surface(self.mask_surface)  
        
        self.rect = self.image.get_rect(center=(x, y))  

    def generate_obstacles(self, num_obstacles=10, ai_mode=False):  
        obstacle_group = pygame.sprite.Group()
        available_positions = TRACK_BONUS_POINTS  
        random.shuffle(available_positions)
        selected_positions = available_positions[:num_obstacles]
        for x, y in selected_positions:
            obstacle = Obstacle(x, y, ai_mode=ai_mode)
            obstacle_group.add(obstacle)
        return obstacle_group

    def reshuffle_obstacles(self, obstacle_group, num_obstacles, ai_mode=False):
        obstacle_group.empty()  
        obstacle_group.add(self.generate_obstacles(num_obstacles, ai_mode=ai_mode))