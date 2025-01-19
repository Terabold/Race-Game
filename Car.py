import math
import pygame
from Constants import *

class Car():
    def __init__(self, x, y, car_color = "red") -> None:  
        # Basic car attributes
        self.x = x  
        self.y = y
        self.img = pygame.image.load(CAR_COLORS[car_color]).convert_alpha()
        self.image = pygame.transform.scale(self.img, (19, 38))
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.max_velocity = MAXSPEED
        self.velocity = 0
        self.rotation_velocity = ROTATESPEED
        self.angle = 0
        self.acceleration = ACCELERATION
        
        # # Drift attributes
        # self.drift_momentum = 0
        # self.drift_friction = 0.8
        # self.drift_factor = 0.1

        # # Collision attributes
        # self.recovery_bounce = 1.5
        # self.recovery_slowdown = 0.6
        # self.recovery_straighten = 5

        self.ray_length = 400
        self.ray_count = 7  
        self.ray_angles = [90, 60, 30, 0, -30, -60, -90]  
        self.ray_distances = [self.ray_length] * self.ray_count
        
        self.ray_colors = [
            RED,      # Red (leftmost)
            YELLOW,    # Yellow
            GREEN,      # Green (center)
            DODGERBLUE,    # Cyan
            BLUE,
            WHITE,
            BLACK     # Blue (rightmost)
        ]

    def cast_rays(self, border_mask):
        self.ray_distances = []
        
        center_x = self.x + self.image.get_width() // 2
        center_y = self.y + self.image.get_height() // 2

        for ray_angle in self.ray_angles:
            actual_angle = (self.angle + ray_angle) % 360
            rad_angle = math.radians(actual_angle)
            
            found_collision = False
            # Reduced step size for more precise detection
            for dist in range(1, self.ray_length + 1, 1):  # Step size of 1 for maximum precision
                ray_end_x = int(center_x - math.sin(rad_angle) * dist)
                ray_end_y = int(center_y - math.cos(rad_angle) * dist)
                
                # Check if point is within mask bounds
                if (0 <= ray_end_x < border_mask.get_size()[0] and 
                    0 <= ray_end_y < border_mask.get_size()[1]):
                    try:
                        # Check both the exact point and surrounding pixels
                        check_points = [
                            (ray_end_x, ray_end_y),
                            (ray_end_x + 1, ray_end_y),
                            (ray_end_x - 1, ray_end_y),
                            (ray_end_x, ray_end_y + 1),
                            (ray_end_x, ray_end_y - 1)
                        ]
                        
                        for point in check_points:
                            if (0 <= point[0] < border_mask.get_size()[0] and 
                                0 <= point[1] < border_mask.get_size()[1] and
                                border_mask.get_at(point)):
                                self.ray_distances.append(dist)
                                found_collision = True
                                break
                        
                        if found_collision:
                            break
                            
                    except IndexError:
                        continue
                
            if not found_collision:
                self.ray_distances.append(self.ray_length)

    def draw_rays(self, surface):
        """Draw rays for visualization with unique colors"""
        # Get the center of the car
        center_x = self.x + self.image.get_width() // 2
        center_y = self.y + self.image.get_height() // 2
        
        for i, ray_angle in enumerate(self.ray_angles):
            actual_angle = (self.angle + ray_angle) % 360
            rad_angle = math.radians(actual_angle)
            
            ray_end_x = center_x - math.sin(rad_angle) * self.ray_distances[i]
            ray_end_y = center_y - math.cos(rad_angle) * self.ray_distances[i]
            
            # Draw the ray line with its unique color
            pygame.draw.line(surface, self.ray_colors[i], 
                           (center_x, center_y),
                           (ray_end_x, ray_end_y), 2)

    def get_raycast_data(self):
        """Return normalized raycast distances for AI input"""
        return [dist / self.ray_length for dist in self.ray_distances]
    
    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_velocity
            # if abs(self.velocity) > self.max_velocity * 0.5:
                # self.drift_momentum -= self.velocity * self.drift_factor
        elif right:
            self.angle -= self.rotation_velocity
            # if abs(self.velocity) > self.max_velocity * 0.5:
                # self.drift_momentum += self.velocity * self.drift_factor

    def move(self):
        # Regular movement
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.velocity
        horizontal = math.sin(radians) * self.velocity
        
        # Drift movement
        # drift_radians = math.radians(self.angle + 90)
        # drift_vertical = math.cos(drift_radians) * self.drift_momentum
        # drift_horizontal = math.sin(drift_radians) * self.drift_momentum
        
        # Apply movement
        self.y -= (vertical)  # + drift_vertical)
        self.x -= (horizontal) # + drift_horizontal
        # self.drift_momentum *= self.drift_friction

    def accelerate(self, forward=True):
        if forward:
            self.velocity = min(self.velocity + self.acceleration, self.max_velocity)
        else:
            self.velocity = max(self.velocity - self.acceleration, -self.max_velocity / 2)
        self.move()

    def reduce_speed(self):
        if self.velocity > 0:
            self.velocity = max(self.velocity - self.acceleration * 0.3, 0)
        elif self.velocity < 0:
            self.velocity = min(self.velocity + self.acceleration * 0.3, 0)
        self.move()
        
    def reset(self, x=None, y=None):
        if x is not None and y is not None:
            self.x = x
            self.y = y
        self.velocity = 0
        self.angle = 0
        # self.drift_momentum = 0
        self.rect.center = (self.x, self.y)

    def handle_border_collision(self):
        # Determine if we're going forward or backward
        is_reversing = self.velocity < 0
        
        # Reduce and reverse velocity based on impact
        self.velocity *= -0.5  # Common practice to bounce back at reduced speed
        
        # Move car away from border - adjust direction based on forward/reverse
        radians = math.radians(self.angle)
        push_direction = -1 if is_reversing else 1  # Flip push direction when reversing
        
        self.x += math.sin(radians) * 10 * push_direction
        self.y += math.cos(radians) * 10 * push_direction
        
        # Reduce car's speed to create impact feel
        if abs(self.velocity) > 2:  # Only slow down significantly on hard impacts
            self.velocity *= 0.7

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.image)
        offset = (int(self.x - x), int(self.y - y))
        return mask.overlap(car_mask, offset)