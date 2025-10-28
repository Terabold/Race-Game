import pygame
from scripts.Constants import *
from scripts.Car import Car
from scripts.Obstacle import Obstacle
from pathlib import Path
import math
import random

class AIEnvironment:
    """Optimized environment specifically for AI training"""
    def __init__(self, surface):
        self.surface = surface
        
        # Single car for training
        start_x, start_y = CAR_START_POS
        self.car = Car(start_x, start_y, "Red")
        
        # Obstacles
        self.num_obstacles = 15
        self.obstacle_group = pygame.sprite.Group()
        self._generate_obstacles()
        
        # Track
        self._setup_track()
        
        # Timers
        self.max_time = TARGET_TIME
        self.time_remaining = self.max_time
        
        # Episode state
        self.episode_ended = False
        self.car_finished = False
        self.car_crashed = False
        self.car_timeout = False
        
        # Font for time display
        self.font = pygame.font.Font(FONT, 32)
        
    def _setup_track(self):
        self.track_border = pygame.image.load(TRACK_BORDER).convert_alpha()
        self.track_border_mask = pygame.mask.from_surface(self.track_border)
        
        self.finish_line = pygame.transform.scale(
            pygame.image.load(FINISHLINE).convert_alpha(),
            FINISHLINE_SIZE
        )
        self.finish_line_position = FINISHLINE_POS
        self.finish_mask = pygame.mask.from_surface(self.finish_line)
    
    def _generate_obstacles(self):
        obstacle_generator = Obstacle(0, 0, ai_mode=True)
        self.obstacle_group.add(
            obstacle_generator.generate_obstacles(self.num_obstacles, ai_mode=True)
        )
    
    def reset(self):
        """Reset environment for new episode"""
        start_x, start_y = CAR_START_POS
        self.car.reset(start_x, start_y)
        
        # Reset obstacles
        obstacle_generator = Obstacle(0, 0, ai_mode=True)
        obstacle_generator.reshuffle_obstacles(self.obstacle_group, self.num_obstacles, ai_mode=True)
        
        # Reset timers and state
        self.time_remaining = self.max_time
        self.episode_ended = False
        self.car_finished = False
        self.car_crashed = False
        self.car_timeout = False
    
    def get_state(self):
        """Get current state vector for AI"""
        # Cast rays
        self.car.cast_rays(self.track_border_mask, self.obstacle_group)
        
        # Normalize ray distances (11 rays)
        normalized_rays = [dist / self.car.ray_length for dist in self.car.ray_distances]
        
        # Build state vector: 11 rays + 1 velocity + 2 angle + 2 position = 16 total
        state = [
            *normalized_rays,                           # 11 values
            self.car.velocity / self.car.max_velocity,  # 1 value
            math.cos(math.radians(self.car.angle)),     # 1 value
            math.sin(math.radians(self.car.angle)),     # 1 value
            self.car.position.x / WIDTH,                # 1 value
            self.car.position.y / HEIGHT                # 1 value
        ]
        
        return state
    
    def step(self, action):
        """
        Execute one step with the given action.
        
        Returns:
            state: next state vector
            step_info: dict with collision, finished, hit_obstacle, timeout flags
            done: whether episode ended
        """
        if self.episode_ended:
            return self.get_state(), {
                'collision': False,
                'finished': False,
                'hit_obstacle': False,
                'timeout': False
            }, True
        
        # Store pre-action state
        pre_velocity = self.car.velocity
        
        # Execute action
        self._handle_car_movement(action)
        
        # Initialize step info
        step_info = {
            'collision': False,
            'finished': False,
            'hit_obstacle': False,
            'timeout': False
        }
        
        # Check obstacle FIRST (before other checks)
        step_info['hit_obstacle'] = self._check_obstacle(pre_velocity)
        
        # Check finish line (must check BEFORE collision)
        step_info['finished'] = self._check_finish()
        
        # Check collision
        step_info['collision'] = self._check_collision()
        
        # Update timer and check timeout
        self.time_remaining = max(0, self.time_remaining - 1/FPS)
        if self.time_remaining <= 0 and not self.car_finished and not self.car_crashed:
            self.car.can_move = False
            self.car_timeout = True
            step_info['timeout'] = True
            self.episode_ended = True
        
        # Check if episode ended
        done = self.episode_ended
        
        # Get next state
        next_state = self.get_state()
        
        return next_state, step_info, done
    
    def _handle_car_movement(self, action):
        """Execute the action on the car"""
        if action is None:
            return
        
        moving = action in [1, 2, 5, 6, 7, 8]
        
        if action in [3, 5, 7]:
            self.car.rotate(left=True)
        elif action in [4, 6, 8]:
            self.car.rotate(right=True)
        
        if action in [1, 5, 6]:
            self.car.accelerate(True)
        elif action in [2, 7, 8]:
            self.car.accelerate(False)
        
        if not moving:
            self.car.reduce_speed()
    
    def _check_obstacle(self, pre_velocity):
        """Check if car hit obstacle and apply velocity reduction"""
        for obstacle in self.obstacle_group.sprites():
            if pygame.sprite.collide_mask(self.car, obstacle):
                self.car.velocity *= 0.25
                obstacle.kill()
                # Return True only if velocity was significant before hit
                return pre_velocity > 1.0
        return False
    
    def _check_finish(self):
        """Check if car crossed finish line"""
        if self.car_finished or self.car_crashed:
            return False
        
        car_offset = (
            int(self.car.rect.left - self.finish_line_position[0]),
            int(self.car.rect.top - self.finish_line_position[1])
        )
        
        if finish_overlap := self.finish_mask.overlap(self.car.mask, car_offset):
            # Bottom edge of finish line (y > 2) = successful finish
            if finish_overlap[1] > 2:
                self.car_finished = True
                self.episode_ended = True
                return True
        
        return False
    
    def _check_collision(self):
        """Check if car crashed into wall"""
        if self.car_crashed:
            return False
        
        offset = (int(self.car.rect.left), int(self.car.rect.top))
        finish_offset = (
            int(self.car.rect.left - self.finish_line_position[0]),
            int(self.car.rect.top - self.finish_line_position[1])
        )
        
        # Check track border collision
        if self.track_border_mask.overlap(self.car.mask, offset):
            self.car.failed = True
            self.car.can_move = False
            self.car_crashed = True
            self.episode_ended = True
            return True
        
        # Check top edge of finish line (y <= 2) = collision
        if finish_overlap := self.finish_mask.overlap(self.car.mask, finish_offset):
            if finish_overlap[1] <= 2:
                self.car.failed = True
                self.car.can_move = False
                self.car_crashed = True
                self.episode_ended = True
                return True
        
        return False
    
    def draw(self):
        """Draw environment (minimal for performance)"""
        self.surface.fill((0, 0, 0))
        
        # Draw obstacles
        self.obstacle_group.draw(self.surface)
        
        # Draw rays
        if not self.car_finished and not self.car_crashed:
            self.car.draw_rays(self.surface)
        
        # Draw track border
        self.surface.blit(self.track_border, (0, 0))
        
        # Draw car
        self.surface.blit(self.car.image, self.car.rect)
        
        # Draw time remaining
        self._draw_time_remaining()
    
    def _draw_time_remaining(self):
        """Draw the time remaining display"""
        time_color = GREEN if self.time_remaining > 10 else (
            YELLOW if self.time_remaining > 3 else RED
        )
        
        time_text = f"Time: {self.time_remaining:.1f}s"
        text_surface = self.font.render(time_text, True, time_color)
        
        # Add shadow for better visibility
        shadow_surface = self.font.render(time_text, True, BLACK)
        self.surface.blit(shadow_surface, (17, 17))
        self.surface.blit(text_surface, (15, 15))