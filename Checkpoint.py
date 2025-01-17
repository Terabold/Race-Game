import pygame
import math
from Constants import *

class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, pos, size, index):
        super().__init__()
        self.image = pygame.image.load(CHECKPOINT).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(topleft=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.passed = False
        self.index = index
        self.pos = pos
        
    def get_distance_to(self, x, y):
        checkpoint_center_x = self.rect.centerx
        checkpoint_center_y = self.rect.centery
        return math.sqrt((checkpoint_center_x - x)**2 + (checkpoint_center_y - y)**2)