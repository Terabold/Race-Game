import math
import pygame
from pygame.math import Vector2
from Constants import *

class Car(pygame.sprite.Sprite): 
    def __init__(self, x, y, car_color="Red"):
        super().__init__() 
        # Basic setup
        self.position = Vector2(x, y)
        self.car_color = car_color
        
        # Load car image based on color
        self.img = pygame.image.load(CAR_COLORS[car_color]).convert_alpha()
        self.image = pygame.transform.scale(self.img, (19, 38))  
        self.original_image = self.image  
        self.rect = self.image.get_rect(center=self.position)
        self.mask = pygame.mask.from_surface(self.image)  
        
        # Physics properties
        self.max_velocity = MAXSPEED
        self.velocity = 0
        self.rotation_velocity = ROTATESPEED
        self.angle = 0  
        self.acceleration = ACCELERATION
        
        # Game state
        self.failed = False
        self.can_move = True  
        self.drift_angle = 0 
        
        # Ray sensor setup
        self.ray_length = 400
        # Various sensor angles to detect surroundings
        self.ray_angles = [0, 10, 20, 30, 75, -10, -20, -30, -75, -180, 90, -90]
        self.ray_count = len(self.ray_angles)
        self.ray_distances = [self.ray_length] * self.ray_count
        self.ray_color = GREEN
        
        # Pre-calculate normalized ray directions
        self.ray_directions = []
        for angle in self.ray_angles:
            # Start with upward vector and rotate by angle
            direction = Vector2(0, -1).rotate(-angle)
            self.ray_directions.append(direction.normalize())
            
        self.ray_collision_points = [None] * self.ray_count

    def cast_rays(self, border_mask, obstacle_group=None):
        """Cast rays to detect track borders and obstacles"""
        # Reset ray data
        self.ray_distances_border = []
        self.ray_distances_obstacles = []
        self.ray_collision_points = []
        
        # Get current car rotation
        car_rotation = -self.angle  # Negative because pygame rotation is clockwise

        # Cast each ray
        for direction in self.ray_directions:
            # Rotate ray direction according to car's current angle
            ray_dir = direction.rotate(car_rotation)
            
            # Track detection flags and distances
            found_border = False
            found_obstacle = False
            border_dist = self.ray_length
            obstacle_dist = self.ray_length
            collision_point = None

            # Step along ray path
            for dist in range(1, self.ray_length + 1, 5):  # Step by 5 for performance
                # Calculate endpoint of current ray segment
                end_pos = self.position + ray_dir * dist
                x, y = int(end_pos.x), int(end_pos.y)

                # Make sure we're within screen bounds
                if 0 <= x < border_mask.get_size()[0] and 0 <= y < border_mask.get_size()[1]:
                    
                    # Check if ray hit track border
                    if not found_border and border_mask.get_at((x, y)):
                        border_dist = dist
                        found_border = True
                    
                    # Check if ray hit an obstacle
                    if obstacle_group and not found_obstacle:
                        for obstacle in obstacle_group:
                            if obstacle.rect.collidepoint(x, y):
                                # Convert to obstacle local coordinates
                                obs_offset = (x - obstacle.rect.x, y - obstacle.rect.y)
                                
                                # Make sure we're within obstacle mask bounds
                                try:
                                    if (0 <= obs_offset[0] < obstacle.mask.get_size()[0] and 
                                        0 <= obs_offset[1] < obstacle.mask.get_size()[1]):
                                        # Check mask collision
                                        if obstacle.mask.get_at(obs_offset):
                                            obstacle_dist = dist
                                            found_obstacle = True
                                            break
                                except IndexError:
                                    # Skip if we're out of bounds
                                    pass
                
                # If we've found both border and obstacle hit, we can stop casting this ray
                if found_border and found_obstacle:
                    break

            # Store distances for this ray
            self.ray_distances_border.append(border_dist)
            self.ray_distances_obstacles.append(obstacle_dist)
            
            # Store collision point (using the closer of the two hits)
            min_dist = min(border_dist, obstacle_dist)
            self.ray_collision_points.append(self.position + ray_dir * min_dist)

    def draw_rays(self, surface):
        """Draw the ray sensors and collision points"""
        for i, collision_point in enumerate(self.ray_collision_points):
            if collision_point:
                # Draw ray line
                pygame.draw.line(surface, self.ray_color, self.position, collision_point, 2)
                
                # Draw collision point with white outline
                pygame.draw.circle(surface, WHITE, (int(collision_point.x), int(collision_point.y)), 4)
                pygame.draw.circle(surface, self.ray_color, (int(collision_point.x), int(collision_point.y)), 3)

    def get_raycast_data(self):
        """Return normalized ray distances for AI training"""
        return [dist / self.ray_length for dist in self.ray_distances]

    def rotate(self, left=False, right=False):
        # Skip if car can't move
        if not self.can_move:  
            return
            
        # Update angle based on rotation direction
        if left:
            self.angle += self.rotation_velocity
        elif right:
            self.angle -= self.rotation_velocity

        # Rotate image and update rect and mask
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        # Skip if car can't move
        if not self.can_move:  
            return
            
        # Convert angle to radians and calculate direction vector
        radians = math.radians(self.angle)
        direction = Vector2(math.sin(radians), math.cos(radians))
        
        # Update position based on velocity and direction
        # Note: pygame y-axis is inverted, so we subtract
        self.position -= direction * self.velocity
        self.rect.center = self.position

    def accelerate(self, forward=True):
        # Skip if car can't move
        if not self.can_move:  
            return
            
        # Update velocity based on direction
        if forward:
            # Accelerate forward with max speed limit
            self.velocity = min(self.velocity + self.acceleration, self.max_velocity)
        else:
            # Accelerate backward with half the max speed limit
            self.velocity = max(self.velocity - self.acceleration, -self.max_velocity / 2)
        
        # Apply movement
        self.move()

    def reduce_speed(self):
        # Skip if car can't move
        if not self.can_move: 
            return
            
        # Apply deceleration
        if self.velocity > 0:
            # Slow down if moving forward
            self.velocity = max(self.velocity - self.acceleration * 0.3, 0)
        elif self.velocity < 0:
            # Slow down if moving backward
            self.velocity = min(self.velocity + self.acceleration * 0.3, 0)
        
        # Apply movement if still moving
        self.move()

    def reset(self, x=None, y=None):
        # Reset position if provided
        if x is not None and y is not None:
            self.position = Vector2(x, y)
        
        # Reset physics state
        self.velocity = 0
        self.angle = 0
        self.failed = False
        self.can_move = True  
        
        # Reset image and collision
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.position)
        self.rect.center = self.position
        self.mask = pygame.mask.from_surface(self.image)