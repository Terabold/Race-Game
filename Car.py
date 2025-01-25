import math
import pygame
from pygame.math import Vector2
from Constants import *

class Car:
    def __init__(self, x, y, car_color="Red"):
        self.position = Vector2(x, y)
        self.car_color = car_color
        self.img = pygame.image.load(CAR_COLORS[car_color]).convert_alpha()
        self.image = pygame.transform.scale(self.img, (19, 38))
        self.rect = self.image.get_rect(center=self.position)
        
        # Movement parameters
        self.max_velocity = MAXSPEED
        self.velocity = 0
        self.rotation_velocity = ROTATESPEED
        self.angle = 0  # Stored in degrees
        self.acceleration = ACCELERATION

        # Drift parameters
        self.drift_angle = 0
        self.drift_momentum = 0
        self.drift_factor = 0.1
        self.drift_friction = 0.87
        self.grip = 0.95

        # Collision recovery
        self.recovery_slowdown = 0.6

        # Raycasting
        self.ray_length = 400
        self.ray_count = 7
        self.ray_angles = [90, 60, 30, 0, -30, -60, -90]
        self.ray_distances = [self.ray_length] * self.ray_count
        self.ray_colors = [RED, YELLOW, GREEN, DODGERBLUE, BLUE, WHITE, BLACK]
        self.ray_directions = [Vector2(0, -1).rotate(-a).normalize() for a in self.ray_angles]

    def cast_rays(self, border_mask):
        self.ray_distances = []
        car_rotation = -(self.angle + self.drift_angle)
        
        for direction in self.ray_directions:
            ray_dir = direction.rotate(car_rotation)
            found = False
            
            for dist in range(1, self.ray_length + 1, 5):
                end_pos = self.position + ray_dir * dist
                x, y = int(end_pos.x), int(end_pos.y)
                
                if 0 <= x < border_mask.get_size()[0] and 0 <= y < border_mask.get_size()[1]:
                    if border_mask.get_at((x, y)):
                        self.ray_distances.append(dist)
                        found = True
                        break
            
            if not found:
                self.ray_distances.append(self.ray_length)

    def draw_rays(self, surface):
        car_rotation = -(self.angle + self.drift_angle)
        
        for i, (color, direction) in enumerate(zip(self.ray_colors, self.ray_directions)):
            ray_dir = direction.rotate(car_rotation)
            end_pos = self.position + ray_dir * self.ray_distances[i]
            pygame.draw.line(surface, color, self.position, end_pos, 2)

    def get_raycast_data(self):
        return [dist / self.ray_length for dist in self.ray_distances]

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_velocity
            if abs(self.velocity) > self.max_velocity * 0.5:
                self.drift_momentum -= self.velocity * self.drift_factor
        elif right:
            self.angle -= self.rotation_velocity
            if abs(self.velocity) > self.max_velocity * 0.5:
                self.drift_momentum += self.velocity * self.drift_factor

    def move(self):
        self.previous_position = Vector2(self.position)

        radians = math.radians(self.angle + self.drift_angle)
        direction = Vector2(math.sin(radians), math.cos(radians))
        perp_direction = Vector2(math.cos(radians), -math.sin(radians))

        movement = direction * self.velocity + perp_direction * self.drift_momentum
        self.position -= movement
        
        self.rect.center = self.position
        self.drift_momentum *= self.drift_friction
        self.drift_angle *= self.drift_friction

    def handle_border_collision(self):
        self.position = Vector2(self.previous_position)
        self.rect.center = self.position

        self.velocity *= -self.recovery_slowdown
        self.drift_momentum *= -self.recovery_slowdown

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.image)
        offset = (int(self.position.x - x), int(self.position.y - y))
        return mask.overlap(car_mask, offset)

    def accelerate(self, forward=True):
        if forward:
            self.velocity = min(self.velocity + self.acceleration, self.max_velocity)
        else:
            self.velocity = max(self.velocity - self.acceleration, -self.max_velocity / 2)
        
        self.drift_momentum *= self.grip
        self.move()

    def reduce_speed(self):
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
        self.drift_momentum = 0
        self.drift_angle = 0
        self.rect.center = self.position
