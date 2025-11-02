import math
import pygame
from pygame.math import Vector2
from scripts.Constants import *

class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, car_color="Red"):
        super().__init__()
        self.position = Vector2(x, y)
        self.car_color = car_color

        # Load and setup car image
        self.img = pygame.image.load(CAR_COLORS[car_color]).convert_alpha()
        self.image = pygame.transform.scale(self.img, (19, 38))
        self.original_image = self.image
        self.rect = self.image.get_rect(center=self.position)
        self.mask = pygame.mask.from_surface(self.image)

        # Physics
        self.max_velocity = MAXSPEED
        self.velocity = 0
        self.rotation_velocity = ROTATESPEED
        self.angle = 0
        self.acceleration = ACCELERATION

        # State
        self.failed = False
        self.can_move = True

        # Ray sensors - simplified to single distance list
        self.ray_length = 400
        self.ray_angles = [-90, -75, -60, -45, -30, -20, -15, -10, 0, 10, 15, 20, 30, 45, 60, 75, 90]
        self.ray_distances = [self.ray_length] * len(self.ray_angles)
        self.ray_collision_points = [None] * len(self.ray_angles)
        
        # Pre-calculate ray directions
        self.ray_directions = []
        for angle in self.ray_angles:
            direction = Vector2(0, -1).rotate(-angle)
            self.ray_directions.append(direction.normalize())

    def cast_rays(self, border_mask, obstacle_group=None):
        """Cast rays and store minimum distance (border or obstacle)"""
        car_rotation = -self.angle
        step = 1
        width, height = border_mask.get_size()

        for idx, direction in enumerate(self.ray_directions):
            ray_dir = direction.rotate(car_rotation)
            min_dist = self.ray_length
            
            for dist in range(step, self.ray_length + 1, step):
                end_pos = self.position + ray_dir * dist
                x, y = int(end_pos.x), int(end_pos.y)

                if not (0 <= x < width and 0 <= y < height):
                    break
                    
                # Check border collision
                if border_mask.get_at((x, y)):
                    min_dist = dist
                    break
                
                # Check obstacle collision
                if obstacle_group:
                    for obstacle in obstacle_group:
                        if obstacle.rect.collidepoint(x, y):
                            obs_offset = (x - obstacle.rect.x, y - obstacle.rect.y)
                            mask_w, mask_h = obstacle.mask.get_size()
                            if 0 <= obs_offset[0] < mask_w and 0 <= obs_offset[1] < mask_h:
                                if obstacle.mask.get_at(obs_offset):
                                    min_dist = dist
                                    break
                    if min_dist < self.ray_length:
                        break

            self.ray_distances[idx] = min_dist
            self.ray_collision_points[idx] = self.position + ray_dir * min_dist

    def draw_rays(self, surface):
        """Draw ray sensors"""
        for collision_point in self.ray_collision_points:
            if collision_point:
                pygame.draw.line(surface, GREEN, 
                               (int(self.position.x), int(self.position.y)),
                               (int(collision_point.x), int(collision_point.y)), 2)
                pygame.draw.circle(surface, WHITE, 
                                 (int(collision_point.x), int(collision_point.y)), 3)

    def rotate(self, left=False, right=False):
        if not self.can_move:
            return
        if left:
            self.angle += self.rotation_velocity
        elif right:
            self.angle -= self.rotation_velocity

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        # Only regenerate mask when actually rotating
        if left or right:
            self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        if not self.can_move:
            return
        radians = math.radians(self.angle)
        direction = Vector2(math.sin(radians), math.cos(radians))
        self.position -= direction * self.velocity
        self.rect.center = self.position

    def accelerate(self, forward=True):
        if not self.can_move:
            return
        if forward:
            self.velocity = min(self.velocity + self.acceleration, self.max_velocity)
        else:
            self.velocity = max(self.velocity - self.acceleration, -self.max_velocity / 2)
        self.move()

    def reduce_speed(self):
        if not self.can_move:
            return
        if self.velocity > 0:
            self.velocity = max(self.velocity - self.acceleration * 0.3, 0)
        elif self.velocity < 0:
            self.velocity = min(self.velocity + self.acceleration * 0.3, 0)
        self.move()

    def reset(self, x=None, y=None):
        if x is not None and y is not None:
            self.position = Vector2(x, y)
        self.velocity = 0
        self.angle = 0
        self.failed = False
        self.can_move = True
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.position)
        self.mask = pygame.mask.from_surface(self.image)
        self.ray_distances = [self.ray_length] * len(self.ray_angles)
        self.ray_collision_points = [None] * len(self.ray_angles)