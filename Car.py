import math
import pygame
from pygame.math import Vector2
from Constants import *

class Car(pygame.sprite.Sprite): 
    def __init__(self, x, y, car_color="Red"):
        super().__init__() 
        self.position = Vector2(x, y)
        self.car_color = car_color
        self.img = pygame.image.load(CAR_COLORS[car_color]).convert_alpha()
        self.image = pygame.transform.scale(self.img, (19, 38))  
        self.original_image = self.image  
        self.rect = self.image.get_rect(center=self.position)
        self.mask = pygame.mask.from_surface(self.image)  
        
        self.max_velocity = MAXSPEED
        self.velocity = 0
        self.rotation_velocity = ROTATESPEED
        self.angle = 0  
        self.acceleration = ACCELERATION
        self.failed = False
        self.can_move = True  

        self.drift_angle = 0 
        
        self.ray_length = 400
        self.ray_angles = [0, 10, 20, 30, 40, 75, -10, -20, -30, -40, -75]
        self.ray_count = len(self.ray_angles)
        self.ray_distances = [self.ray_length] * self.ray_count
        self.ray_color = GREEN
        self.ray_directions = [Vector2(0, -1).rotate(-a).normalize() for a in self.ray_angles]
        self.ray_collision_points = [None] * self.ray_count

    def cast_rays(self, border_mask, obstacle_group=None):
        """
        Cast rays to detect both borders and obstacles efficiently.
        """
        self.ray_distances_border = []
        self.ray_distances_obstacles = []
        self.ray_collision_points = []
        car_rotation = -self.angle 

        for direction in self.ray_directions:
            ray_dir = direction.rotate(car_rotation)
            found_border = False
            found_obstacle = False
            border_dist = self.ray_length
            obstacle_dist = self.ray_length
            collision_point = None

            for dist in range(1, self.ray_length + 1, 5):
                end_pos = self.position + ray_dir * dist
                x, y = int(end_pos.x), int(end_pos.y)

                # Check if we're within screen bounds
                if 0 <= x < border_mask.get_size()[0] and 0 <= y < border_mask.get_size()[1]:
                    
                    # Check border collision first
                    if not found_border and border_mask.get_at((x, y)):
                        border_dist = dist
                        found_border = True
                    
                    # Check obstacle collision if obstacle_group exists
                    if obstacle_group and not found_obstacle:
                        for obstacle in obstacle_group:
                            if obstacle.rect.collidepoint(x, y):
                                obs_offset = (x - obstacle.rect.x, y - obstacle.rect.y)
                                try:
                                    if 0 <= obs_offset[0] < obstacle.mask.get_size()[0] and 0 <= obs_offset[1] < obstacle.mask.get_size()[1]:
                                        if obstacle.mask.get_at(obs_offset):
                                            obstacle_dist = dist
                                            found_obstacle = True
                                            break
                                except IndexError:
                                    pass
                
                # If both detections are done, break early for efficiency
                if found_border and found_obstacle:
                    break

            # Store the shortest distance found for each type
            self.ray_distances_border.append(border_dist)
            self.ray_distances_obstacles.append(obstacle_dist)
            self.ray_collision_points.append(self.position + ray_dir * min(border_dist, obstacle_dist))

    def draw_rays(self, surface):
        """
        Draw rays with collision points highlighted - using a single color
        """
        for collision_point, direction in zip(self.ray_collision_points, self.ray_directions):
            if collision_point:
                # Draw the ray line from car to collision point
                pygame.draw.line(surface, self.ray_color, self.position, collision_point, 2)
                # Draw a small circle at the collision point
                pygame.draw.circle(surface, WHITE, (int(collision_point.x), int(collision_point.y)), 4)
                pygame.draw.circle(surface, self.ray_color, (int(collision_point.x), int(collision_point.y)), 3)

    def get_raycast_data(self):
        """
        Return normalized ray distances for AI training
        """
        return [dist / self.ray_length for dist in self.ray_distances]

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
        self.rect.center = self.position
        self.mask = pygame.mask.from_surface(self.image)