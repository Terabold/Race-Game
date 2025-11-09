# AIEnvironment.py - FIXED STATE SIZE (20 values)
import pygame
import math
from scripts.Constants import *
from scripts.Car import Car
from scripts.Obstacle import Obstacle
from scripts.checkpoint import CheckpointManager


class AIEnvironment:
    def __init__(self, surface):
        self.surface = surface
        
        # Car
        self.car = Car(*CAR_START_POS, "Red")
        
        # Obstacles
        self.num_obstacles = 15
        self.obstacle_group = pygame.sprite.Group()
        self._generate_obstacles()
        
        # Track
        self._setup_track()
        
        # Checkpoint manager
        self.checkpoint_manager = CheckpointManager()
        
        # Time
        self.max_time = TARGET_TIME
        self.time_remaining = self.max_time
        
        # Episode state
        self.episode_ended = False
        self.car_finished = False
        self.car_crashed = False
        self.car_timeout = False
    
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
        obstacle_generator = Obstacle(0, 0, show_image=False)
        self.obstacle_group.add(
            obstacle_generator.generate_obstacles(self.num_obstacles)
        )
    
    def reset(self):
        self.car.reset(*CAR_START_POS)
        
        # Reshuffle obstacles
        obstacle_generator = Obstacle(0, 0, show_image=False)
        obstacle_generator.reshuffle_obstacles(self.obstacle_group, self.num_obstacles)
        
        self.checkpoint_manager.reset()
        
        self.time_remaining = self.max_time
        self.episode_ended = False
        self.car_finished = False
        self.car_crashed = False
        self.car_timeout = False
    
    def get_state(self):
        """
        State: 14 values total
        - 11 rays (normalized)
        - 1 velocity (normalized)
        - 2 orientation (sin/cos)
        """
        self.car.cast_rays(self.track_border_mask, self.obstacle_group)
        
        # 1. Rays (11 values) - normalized
        normalized_rays = [d / self.car.ray_length for d in self.car.ray_distances]
        
        # 2. Velocity (1 value)
        norm_vel = max(0.0, self.car.velocity / self.car.max_velocity)
        
        # 3. Car orientation (2 values - sin/cos to avoid 0/360 discontinuity)
        angle_rad = math.radians(self.car.angle)
        angle_sin = math.sin(angle_rad)
        angle_cos = math.cos(angle_rad)
        
        state = [
            *normalized_rays,  # 0-10 (11 values)
            norm_vel,          # 11
            angle_sin,         # 12
            angle_cos,         # 13
        ]
        
        return state
    
    def step(self, action):
        if self.episode_ended:
            return self.get_state(), {
                'collision': False, 'finished': False, 'hit_obstacle': False,
                'timeout': False, 'checkpoint_crossed': False, 'backward_crossed': False
            }, True
        
        pre_velocity = self.car.velocity
        self._handle_car_movement(action)
        
        car_pos = (self.car.position.x, self.car.position.y)
        crossed, backward = self.checkpoint_manager.check_crossing(car_pos)
        
        step_info = {
            'collision': False, 'finished': False, 'hit_obstacle': False,
            'timeout': False, 'checkpoint_crossed': crossed, 'backward_crossed': backward
        }
        
        step_info['hit_obstacle'] = self._check_obstacle(pre_velocity)
        step_info['finished'] = self._check_finish()
        step_info['collision'] = self._check_collision()
        
        self.time_remaining = max(0, self.time_remaining - 1/FPS)
        if self.time_remaining <= 0 and not self.car_finished and not self.car_crashed:
            self.car.can_move = False
            self.car_timeout = True
            step_info['timeout'] = True
            self.episode_ended = True
        
        done = self.episode_ended
        next_state = self.get_state()
        return next_state, step_info, done
    
    def _handle_car_movement(self, action):
        if action is None: return
        moving = action in [1, 2, 5, 6, 7, 8]
        if action in [3, 5, 7]: self.car.rotate(left=True)
        elif action in [4, 6, 8]: self.car.rotate(right=True)
        if action in [1, 5, 6]: self.car.accelerate(True)
        elif action in [2, 7, 8]: self.car.accelerate(False)
        if not moving: self.car.reduce_speed()
    
    def _check_obstacle(self, pre_velocity):
        for obstacle in self.obstacle_group.sprites():
            if pygame.sprite.collide_mask(self.car, obstacle):
                self.car.velocity *= 0.25
                obstacle.kill()
                return pre_velocity > 1.0
        return False
    
    def _check_finish(self):
        if self.car_finished or self.car_crashed: return False
        offset = (
            int(self.car.rect.left - self.finish_line_position[0]),
            int(self.car.rect.top - self.finish_line_position[1])
        )
        if overlap := self.finish_mask.overlap(self.car.mask, offset):
            if overlap[1] > 2:
                self.car_finished = True
                self.episode_ended = True
                return True
        return False
    
    def _check_collision(self):
        if self.car_crashed: return False
        offset = (int(self.car.rect.left), int(self.car.rect.top))
        finish_offset = (
            int(self.car.rect.left - self.finish_line_position[0]),
            int(self.car.rect.top - self.finish_line_position[1])
        )
        if self.track_border_mask.overlap(self.car.mask, offset):
            self.car.failed = True
            self.car.can_move = False
            self.car_crashed = True
            self.episode_ended = True
            return True
        if overlap := self.finish_mask.overlap(self.car.mask, finish_offset):
            if overlap[1] <= 2:
                self.car.failed = True
                self.car.can_move = False
                self.car_crashed = True
                self.episode_ended = True
                return True
        return False
    
    def draw(self):
        self.surface.fill((0, 0, 0))
        self.obstacle_group.draw(self.surface)
        self.checkpoint_manager.draw(self.surface)
        
        if not self.car_finished and not self.car_crashed:
            self.car.draw_rays(self.surface)
        
        self.surface.blit(self.track_border, (0, 0))
        self.surface.blit(self.car.image, self.car.rect)
        self.surface.blit(self.finish_line, self.finish_line_position)
        
        # Simple UI
        font = pygame.font.Font(None, 24)
        
        time_color = GREEN if self.time_remaining > 10 else (YELLOW if self.time_remaining > 3 else RED)
        time_text = font.render(f"Time: {self.time_remaining:.1f}s", True, time_color)
        self.surface.blit(time_text, (10, 10))
        
        cp_text = font.render(f"CP: {self.checkpoint_manager.crossed_count}/16", True, WHITE)
        self.surface.blit(cp_text, (10, 40))
        
        speed_ratio = self.car.velocity / self.car.max_velocity if self.car.max_velocity > 0 else 0
        speed_text = font.render(f"Speed: {speed_ratio:.1%}", True, WHITE)
        self.surface.blit(speed_text, (10, 70))