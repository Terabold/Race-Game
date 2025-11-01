# AIEnvironment.py - COMPLETE FIXED VERSION
import pygame
import math
from scripts.Constants import *
from scripts.Car import Car
from scripts.Obstacle import Obstacle
from scripts.checkpoint import CheckpointManager

# ----------------------------------------------------------------------
#  UI STYLE
# ----------------------------------------------------------------------
UI_FONT_SIZE      = 22
UI_DEBUG_SIZE     = 18
UI_COLOR          = (255, 255, 255)
SHADOW_COLOR      = (0, 0, 0)
LINE_HEIGHT       = 26
DEBUG_LINE_HEIGHT = 20
MARGIN_X          = 15
MARGIN_Y_TOP      = 10
MARGIN_Y_BOTTOM   = 10


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

    # ==============================================================
    #  SETUP
    # ==============================================================
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

    # ==============================================================
    #  RESET
    # ==============================================================
    def reset(self):
        self.car.reset(*CAR_START_POS)

        # Reshuffle obstacles
        obstacle_generator = Obstacle(0, 0, ai_mode=True)
        obstacle_generator.reshuffle_obstacles(self.obstacle_group, self.num_obstacles, ai_mode=True)

        self.checkpoint_manager.reset()

        self.time_remaining = self.max_time
        self.episode_ended = False
        self.car_finished = False
        self.car_crashed = False
        self.car_timeout = False

    # ==============================================================
    #  STATE - SIMPLIFIED (NO CHECKPOINT INFO)
    # ==============================================================
    def get_state(self):
        """
        Simplified state: Only rays, velocity, and car orientation
        Total: 20 values (17 rays + 1 velocity + 2 orientation)
        """
        self.car.cast_rays(self.track_border_mask, self.obstacle_group)

        # 1. Rays – normalized
        normalized_rays = [d / self.car.ray_length for d in self.car.ray_distances]

        # 2. Velocity
        norm_vel = max(0.0, self.car.velocity / self.car.max_velocity)

        # 3. Car orientation (sin/cos to avoid 0/360 discontinuity)
        angle_rad = math.radians(self.car.angle)
        angle_sin = math.sin(angle_rad)
        angle_cos = math.cos(angle_rad)

        return [
            *normalized_rays,   # 0–16 (17 values)
            norm_vel,           # 17
            angle_sin,          # 18 (orientation Y component)
            angle_cos,          # 19 (orientation X component)
        ]

    # ==============================================================
    #  STEP
    # ==============================================================
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

    # ------------------------------------------------------------------
    #  MOVEMENT & COLLISIONS
    # ------------------------------------------------------------------
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

    # ==============================================================
    #  DRAW
    # ==============================================================
    def _draw_text(self, text: str, pos: tuple, color=UI_COLOR, size=UI_FONT_SIZE):
        font = pygame.font.Font(None, size)
        shadow = font.render(text, True, SHADOW_COLOR)
        main   = font.render(text, True, color)
        self.surface.blit(shadow, (pos[0]+1, pos[1]+1))
        self.surface.blit(main,   pos)

    def draw(self):
        self.surface.fill((0, 0, 0))
        self.obstacle_group.draw(self.surface)
        self.checkpoint_manager.draw(self.surface)

        if not self.car_finished and not self.car_crashed:
            self.car.draw_rays(self.surface)

        self.surface.blit(self.track_border, (0, 0))
        self.surface.blit(self.car.image, self.car.rect)
        self.surface.blit(self.finish_line, self.finish_line_position)

        # --- UI: Top-left ---
        x, y = MARGIN_X, MARGIN_Y_TOP
        time_color = GREEN if self.time_remaining > 10 else (YELLOW if self.time_remaining > 3 else RED)
        self._draw_text(f"Time: {self.time_remaining:.1f}s", (x, y), time_color)
        y += LINE_HEIGHT
        
        # Show checkpoint progress
        total_checkpoints = self.checkpoint_manager.total_checkpoints
        current_progress = self.checkpoint_manager.crossed_count
        if self.car_finished:
            current_progress = total_checkpoints
        
        self._draw_text(f"CP: {current_progress}/{total_checkpoints}", (x, y))
        y += LINE_HEIGHT
        
        speed_ratio = self.car.velocity / self.car.max_velocity if self.car.max_velocity > 0 else 0
        speed_color = GREEN if speed_ratio > 0.7 else (YELLOW if speed_ratio > 0.3 else RED)
        self._draw_text(f"Speed: {speed_ratio:.1%}", (x, y), speed_color)

        # --- DEBUG: Bottom-left ---
        state = self.get_state()
        y_debug = self.surface.get_height() - MARGIN_Y_BOTTOM - (4 * DEBUG_LINE_HEIGHT)
        
        # Show first few rays only (to save space)
        ray_preview = " ".join(f"{r:.2f}" for r in state[:17]) + "..."
        self._draw_text(f"Rays[0-4]: {ray_preview}", (MARGIN_X, y_debug), size=UI_DEBUG_SIZE)
        y_debug += DEBUG_LINE_HEIGHT
        
        self._draw_text(f"Vel: {state[17]:.2f}", (MARGIN_X, y_debug), size=UI_DEBUG_SIZE)
        y_debug += DEBUG_LINE_HEIGHT
        
        self._draw_text(f"Angle: sin={state[18]:.2f} cos={state[19]:.2f}", (MARGIN_X, y_debug), size=UI_DEBUG_SIZE)
        y_debug += DEBUG_LINE_HEIGHT
        
        # Show min/max rays for situational awareness
        min_ray = min(state[:17]) if state[:17] else 0
        max_ray = max(state[:17]) if state[:17] else 0
        self._draw_text(f"Ray range: [{min_ray:.2f}, {max_ray:.2f}]", (MARGIN_X, y_debug), size=UI_DEBUG_SIZE)