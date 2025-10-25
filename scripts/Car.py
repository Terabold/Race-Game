import math
import pygame
from pygame.math import Vector2
from scripts.Constants import *

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

        # Obstacle collision flag for reward logic
        self.hit_obstacle = False

        # Ray sensor setup
        self.ray_length = 400
        self.ray_angles = [
            0,      # Primary forward
            15,     # Fine-tune right
            -15,    # Fine-tune left
            30,     # Bomb/path right
            -30,    # Bomb/path left
            45,     # Mid-range cornering right
            -45,    # Mid-range cornering left
            60,     # Wide vision right
            -60,    # Wide vision left
            90,     # Immediate side wall check right
            -90     # Immediate side wall check left
        ]
        self.ray_count = len(self.ray_angles)
        self.ray_distances_border = [self.ray_length] * self.ray_count
        self.ray_distances_obstacles = [self.ray_length] * self.ray_count
        self.ray_distances = [self.ray_length] * self.ray_count
        self.ray_color = GREEN

        # Pre-calculate normalized ray directions (local space)
        self.ray_directions = []
        for angle in self.ray_angles:
            direction = Vector2(0, -1).rotate(-angle)
            self.ray_directions.append(direction.normalize())

        self.ray_collision_points = [None] * self.ray_count

    def cast_rays(self, border_mask, obstacle_group=None):
        """Cast rays to detect track borders and obstacles."""
        self.ray_distances_border = [self.ray_length] * self.ray_count
        self.ray_distances_obstacles = [self.ray_length] * self.ray_count
        self.ray_collision_points = [None] * self.ray_count

        car_rotation = -self.angle
        step = 10

        width, height = border_mask.get_size()

        for idx, direction in enumerate(self.ray_directions):
            ray_dir = direction.rotate(car_rotation)

            found_border = False
            found_obstacle = False
            border_dist = self.ray_length
            obstacle_dist = self.ray_length

            for dist in range(1, self.ray_length + 1, step):
                end_pos = self.position + ray_dir * dist
                x, y = int(end_pos.x), int(end_pos.y)

                if 0 <= x < width and 0 <= y < height:
                    if not found_border and border_mask.get_at((x, y)):
                        border_dist = dist
                        found_border = True

                    if obstacle_group and not found_obstacle:
                        for obstacle in obstacle_group:
                            if obstacle.rect.collidepoint(x, y):
                                obs_offset = (x - obstacle.rect.x, y - obstacle.rect.y)
                                mask_w, mask_h = obstacle.mask.get_size()
                                if 0 <= obs_offset[0] < mask_w and 0 <= obs_offset[1] < mask_h:
                                    if obstacle.mask.get_at(obs_offset):
                                        obstacle_dist = dist
                                        found_obstacle = True
                                        break

                if found_border and found_obstacle:
                    break

            self.ray_distances_border[idx] = border_dist
            self.ray_distances_obstacles[idx] = obstacle_dist
            min_dist = min(border_dist, obstacle_dist)
            self.ray_distances[idx] = min_dist
            self.ray_collision_points[idx] = self.position + ray_dir * min_dist

    def draw_rays(self, surface):
        """Draw the ray sensors and collision points."""
        for i, collision_point in enumerate(self.ray_collision_points):
            if collision_point:
                pygame.draw.line(surface, self.ray_color, (int(self.position.x), int(self.position.y)),
                                 (int(collision_point.x), int(collision_point.y)), 2)
                pygame.draw.circle(surface, WHITE, (int(collision_point.x), int(collision_point.y)), 3)

    def get_raycast_data(self):
        """Return normalized min-distances for rays (0.0..1.0)."""
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
        self.hit_obstacle = False
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.position)
        self.rect.center = self.position
        self.mask = pygame.mask.from_surface(self.image)
        self.ray_distances_border = [self.ray_length] * self.ray_count
        self.ray_distances_obstacles = [self.ray_length] * self.ray_count
        self.ray_distances = [self.ray_length] * self.ray_count
        self.ray_collision_points = [None] * self.ray_count