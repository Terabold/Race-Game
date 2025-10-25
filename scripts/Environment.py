import pygame
from scripts.Constants import *
from scripts.Car import Car
from scripts.Obstacle import Obstacle
from scripts.drawing import draw_finished, draw_failed, draw_ui, draw_countdown, draw_pause_overlay
from scripts.utils import load_sound
from pathlib import Path
import math
import numpy as np

class Environment:
    def __init__(self, surface, ai_train_mode=False, car_color1=None, car_color2=None):
        # Set up game window and basic properties
        self.surface = surface
        self.grass = pygame.image.load(GRASS).convert()
        self.ai_train_mode = ai_train_mode

        # Game state management
        self.game_states = ["countdown", "running", "finished", "failed", "paused"]
        self.game_state = "running" if ai_train_mode else "countdown"
        self.previous_state = None

        # Episode marker for external savers (Game/trainer)
        self.episode_ended = False

        # Car setup
        self.car1_active = car_color1 is not None
        self.car2_active = car_color2 is not None
        self.car1_finished = False
        self.car2_finished = False

        # Set up cars at start position
        start_x, start_y = CAR_START_POS
        self._setup_cars(start_x, start_y, car_color1, car_color2)

        # Create random obstacles
        self.num_obstacles = 15
        self.obstacle_group = pygame.sprite.Group()
        self._generate_obstacles()

        # Load track images and create masks
        self._setup_track()

        # Set up timer
        self.car1_time = TARGET_TIME if self.car1_active else 0
        self.car2_time = TARGET_TIME if self.car2_active else 0
        self.remaining_time = max(self.car1_time, self.car2_time)

        # Initialize sound effects
        self.setup_sound()

    def _setup_cars(self, start_x, start_y, car_color1, car_color2):
        self.all_sprites = pygame.sprite.Group()

        if self.car1_active and self.car2_active:
            self.car1 = Car(start_x + 20, start_y, car_color1)
            self.car2 = Car(start_x - 20, start_y, car_color2)
        else:
            if self.car1_active:
                self.car1 = Car(start_x, start_y, car_color1)
            if self.car2_active:
                self.car2 = Car(start_x, start_y, car_color2)

        if self.car1_active:
            self.all_sprites.add(self.car1)
        if self.car2_active:
            self.all_sprites.add(self.car2)

    def _setup_track(self):
        # Load track images
        self.track = pygame.image.load(TRACK).convert_alpha()
        self.track_border = pygame.image.load(TRACK_BORDER).convert_alpha()
        self.track_border_mask = pygame.mask.from_surface(self.track_border)

        # Set up finish line
        self.finish_line = pygame.transform.scale(
            pygame.image.load(FINISHLINE).convert_alpha(),
            FINISHLINE_SIZE
        )
        self.finish_line_position = FINISHLINE_POS
        self.finish_mask = pygame.mask.from_surface(self.finish_line)

    def _generate_obstacles(self):
        obstacle_generator = Obstacle(0, 0)
        self.obstacle_group.add(
            obstacle_generator.generate_obstacles(self.num_obstacles)
        )

    def run_countdown(self):
        if self.game_state == "countdown":
            if not self.ai_train_mode:
                # Play countdown sound
                self.countdown_sound.play()
                for i in range(3, 0, -1):
                    self.surface.fill((0, 0, 0))
                    self.surface.blits((
                        (self.grass, (0, 0)),
                        (self.track, (0, 0)),
                        (self.finish_line, self.finish_line_position),
                    ))
                    self.obstacle_group.draw(self.surface)
                    self.surface.blit(self.track_border, (0, 0))
                    self.all_sprites.draw(self.surface)

                    draw_countdown(self, i)
                    pygame.display.update()
                    pygame.time.wait(1000)

                # Countdown finished -> start running and start background music
                self.game_state = "running"
                self.handle_music(play=True)
            else:
                # Skip countdown in AI training mode
                self.game_state = "running"

    def draw(self):
        # Skip heavy drawing in AI training mode for speed
        if not self.ai_train_mode:
            self.surface.blits((
                (self.grass, (0, 0)),
                (self.track, (0, 0)),
                (self.finish_line, self.finish_line_position),
            ))
        else:
            self.surface.fill((0, 0, 0))

        # Draw obstacles and optional rays
        self.obstacle_group.draw(self.surface)

        if self.ai_train_mode:
            if self.car1_active and not self.car1_finished and not self.car1.failed:
                self.car1.draw_rays(self.surface)
            if self.car2_active and not self.car2_finished and not self.car2.failed:
                self.car2.draw_rays(self.surface)

        self.surface.blit(self.track_border, (0, 0))
        self.all_sprites.draw(self.surface)

        if self.game_state == "running":
            draw_ui(self)
        elif self.game_state == "finished":
            draw_finished(self)
        elif self.game_state == "failed":
            draw_failed(self)
        elif self.game_state == "paused":
            draw_pause_overlay(self)

    def restart_game(self):
        # Reset car positions and state for the next episode
        start_x, start_y = CAR_START_POS

        if self.car1_active:
            x_pos = start_x + 20 if self.car2_active else start_x
            self.car1.reset(x_pos, start_y)
            self.car1_finished = False
            self.car1_time = TARGET_TIME

        if self.car2_active:
            x_pos = start_x - 20 if self.car1_active else start_x
            self.car2.reset(x_pos, start_y)
            self.car2_finished = False
            self.car2_time = TARGET_TIME

        self.remaining_time = max(self.car1_time, self.car2_time)

        obstacle_generator = Obstacle(0, 0)
        obstacle_generator.reshuffle_obstacles(self.obstacle_group, self.num_obstacles)

        self.state_timer = 0
        # In training mode restart immediately as running (no countdown)
        self.game_state = "running" if self.ai_train_mode else "countdown"

        if not self.ai_train_mode:
            # Stop all sounds and music before countdown
            if hasattr(self, 'countdown_sound'):
                self.countdown_sound.stop()
            self.handle_music(play=False)
            # Run countdown (will start music after countdown finishes)
            self.run_countdown()

    def check_game_end_condition(self):
        car1_racing = self.car1_active and not self.car1_finished and not self.car1.failed and self.car1_time > 0
        car2_racing = self.car2_active and not self.car2_finished and not self.car2.failed and self.car2_time > 0

        if not car1_racing and not car2_racing:
            # Mark episode end so external controllers (Game/trainer) can react
            self.episode_ended = True

            # Check if any car finished the race
            any_finished = (self.car1_active and self.car1_finished) or (self.car2_active and self.car2_finished)

            if any_finished:
                # At least one car finished - show victory screen for human mode
                self.game_state = "finished"
                if not self.ai_train_mode:
                    self.handle_music(play=False)
                    self.win_sound.play()
            else:
                # No car finished - show failure screen for human mode
                self.game_state = "failed"
                if not self.ai_train_mode:
                    self.handle_music(play=False)

            # Auto-restart in AI training mode
            if self.ai_train_mode:
                self.restart_game()

            return True

        return False

    def update(self):
        if self.game_state == "countdown":
            self.run_countdown()

        elif self.game_state == "running":
            # Timers for human play
            if self.car1_active and not self.car1_finished and not self.car1.failed:
                self.car1_time = max(0, self.car1_time - 1/FPS)
                if self.car1_time <= 0:
                    self.car1.can_move = False

            if self.car2_active and not self.car2_finished and not self.car2.failed:
                self.car2_time = max(0, self.car2_time - 1/FPS)
                if self.car2_time <= 0:
                    self.car2.can_move = False

            self.remaining_time = max(self.car1_time, self.car2_time)

            # Check for end condition and possibly auto-restart
            self.check_game_end_condition()

            if self.ai_train_mode:
                if self.car1_active and not self.car1_finished and not self.car1.failed:
                    self.car1.cast_rays(self.track_border_mask, self.obstacle_group)
                if self.car2_active and not self.car2_finished and not self.car2.failed:
                    self.car2.cast_rays(self.track_border_mask, self.obstacle_group)

            self.check_obstacle()

        self.all_sprites.update()

    def move(self, action1, action2):
        if self.game_state != "running":
            return False

        if self.car1_active and not self.car1_finished and not self.car1.failed and self.car1_time > 0:
            self._handle_car_movement(self.car1, action1)
            self.check_collision(self.car1)

        if self.car2_active and not self.car2_finished and not self.car2.failed and self.car2_time > 0:
            self._handle_car_movement(self.car2, action2)
            self.check_collision(self.car2)

        self.check_finish()
        return self.check_game_end_condition()

    def check_obstacle(self):
        for obstacle in self.obstacle_group.sprites():
            if (self.car1_active and not self.car1_finished and not self.car1.failed and
                self.car1_time > 0 and pygame.sprite.collide_mask(self.car1, obstacle)):
                # Mark obstacle hit for reward logic
                self.car1.hit_obstacle = True
                self.car1.velocity *= 0.25
                self.obstacle_sound.play()
                obstacle.kill()

            elif (self.car2_active and not self.car2_finished and not self.car2.failed and
                  self.car2_time > 0 and pygame.sprite.collide_mask(self.car2, obstacle)):
                self.car2.hit_obstacle = True
                self.car2.velocity *= 0.25
                self.obstacle_sound.play()
                obstacle.kill()

    def check_collision(self, car):
        if car.failed:
            return False

        offset = (int(car.rect.left), int(car.rect.top))
        finish_offset = (int(car.rect.left - self.finish_line_position[0]),
                         int(car.rect.top - self.finish_line_position[1]))

        collision_detected = False

        if self.track_border_mask.overlap(car.mask, offset):
            car.failed = True
            car.can_move = False
            self.collide_sound.play()
            collision_detected = True

        if overlap := self.finish_mask.overlap(car.mask, finish_offset):
            if overlap[1] <= 2:
                car.failed = True
                car.can_move = False
                self.collide_sound.play()
                collision_detected = True

        if collision_detected:
            self.check_game_end_condition()

        return collision_detected

    def _handle_car_movement(self, car, action):
        if action is None:
            return

        moving = action in [1, 2, 5, 6, 7, 8]

        if action in [3, 5, 7]:
            car.rotate(left=True)
        elif action in [4, 6, 8]:
            car.rotate(right=True)

        if action in [1, 5, 6]:
            car.accelerate(True)
        elif action in [2, 7, 8]:
            car.accelerate(False)

        if not moving:
            car.reduce_speed()

    def check_finish(self):
        any_finished = False

        if self.car1_active and not self.car1_finished and not self.car1.failed:
            car1_offset = (int(self.car1.rect.left - self.finish_line_position[0]),
                           int(self.car1.rect.top - self.finish_line_position[1]))

            if finish := self.finish_mask.overlap(self.car1.mask, car1_offset):
                if finish[1] > 2:
                    self.car1_finished = True
                    self.win_sound.play()
                    any_finished = True

        if self.car2_active and not self.car2_finished and not self.car2.failed:
            car2_offset = (int(self.car2.rect.left - self.finish_line_position[0]),
                           int(self.car2.rect.top - self.finish_line_position[1]))

            if finish := self.finish_mask.overlap(self.car2.mask, car2_offset):
                if finish[1] > 2:
                    self.car2_finished = True
                    self.win_sound.play()
                    any_finished = True

        if any_finished:
            self.check_game_end_condition()

        return any_finished

    def setup_sound(self):
        """
        Load sounds with proper AI training mode handling.
        Volume multiplier approach: 0 in AI mode, 1 in human mode.
        """
        # Volume multiplier: silent in AI training, normal in human play
        volume_multiplier = 0 if self.ai_train_mode else 1
        
        # Load sound effects with conditional volume
        self.collide_sound = load_sound(COLLIDE_SOUND, volume=0.25 * volume_multiplier)
        self.win_sound = load_sound(WIN_SOUND, volume=0.25 * volume_multiplier)
        self.obstacle_sound = load_sound(OBSTACLE_SOUND, volume=0.25 * volume_multiplier)
        self.countdown_sound = load_sound(COUNTDOWN_SOUND, volume=0.6 * volume_multiplier)

        # Background music setup
        self.is_music_playing = False
        
        # Only set up music for human play mode
        if not self.ai_train_mode and pygame.mixer.get_init():
            # Prefer pygame.mixer.music for streaming
            pygame.mixer.music.load(str(Path(BACKGROUND_MUSIC)))
            pygame.mixer.music.set_volume(DEFAULT_SOUND_VOLUME * volume_multiplier)
        else:
            # Fallback or AI mode: use regular Sound (will be silent in AI mode)
            self.background_music = load_sound(BACKGROUND_MUSIC, volume=DEFAULT_SOUND_VOLUME * volume_multiplier)

    def toggle_pause(self):
        if self.game_state == "running":
            self.previous_state = self.game_state
            self.game_state = "paused"
            self.handle_music(play=False)
        elif self.game_state == "paused":
            self.game_state = self.previous_state
            self.handle_music(play=True)

    def handle_music(self, play=True):
        """
        Play or stop background music.
        Safe for both AI and human modes.
        """
        # Skip music entirely in AI training mode
        if self.ai_train_mode:
            return
            
        if not pygame.mixer.get_init():
            return

        if play:
            # Check if using pygame.mixer.music
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
                self.is_music_playing = True
            else:
                # Start music for the first time
                if not self.is_music_playing:
                    pygame.mixer.music.play(-1)
                    self.is_music_playing = True
        else:
            # Stop/pause music
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
            self.is_music_playing = False

    def state(self):
        # If no active car, return None
        if not self.car1_active:
            return None

        # Cast rays and build a compact state vector
        self.car1.cast_rays(self.track_border_mask, self.obstacle_group)

        normalized_border_rays = [dist / self.car1.ray_length for dist in self.car1.ray_distances_border]
        normalized_obstacle_rays = [dist / self.car1.ray_length for dist in self.car1.ray_distances_obstacles]

        state_list = [
            *normalized_border_rays,
            *normalized_obstacle_rays,
            self.car1.velocity / self.car1.max_velocity,
            math.cos(math.radians(self.car1.angle)),
            math.sin(math.radians(self.car1.angle)),
            self.car1.position.x / WIDTH,
            self.car1.position.y / HEIGHT
        ]

        return state_list

    def get_state_dim(self):
        """Return the dimension of the state space for DQN agent"""
        num_rays = len(self.car1.ray_angles) if self.car1_active else 0
        return num_rays * 2 + 1 + 2 + 2

    def get_action_dim(self):
        """Return the dimension of the action space for DQN agent"""
        return 8

    def get_state_for_player(self, player_num):
        if player_num == 1 and self.car1_active:
            self.car1.cast_rays(self.track_border_mask, self.obstacle_group)

            normalized_border_rays = [dist / self.car1.ray_length for dist in self.car1.ray_distances_border]
            normalized_obstacle_rays = [dist / self.car1.ray_length for dist in self.car1.ray_distances_obstacles]

            state_list = [
                *normalized_border_rays,
                *normalized_obstacle_rays,
                self.car1.velocity / self.car1.max_velocity,
                math.cos(math.radians(self.car1.angle)),
                math.sin(math.radians(self.car1.angle)),
                self.car1.position.x / WIDTH,
                self.car1.position.y / HEIGHT
            ]

            return state_list

        elif player_num == 2 and self.car2_active:
            self.car2.cast_rays(self.track_border_mask, self.obstacle_group)

            normalized_border_rays = [dist / self.car2.ray_length for dist in self.car2.ray_distances_border]
            normalized_obstacle_rays = [dist / self.car2.ray_length for dist in self.car2.ray_distances_obstacles]

            state_list = [
                *normalized_border_rays,
                *normalized_obstacle_rays,
                self.car2.velocity / self.car2.max_velocity,
                math.cos(math.radians(self.car2.angle)),
                math.sin(math.radians(self.car2.angle)),
                self.car2.position.x / WIDTH,
                self.car2.position.y / HEIGHT
            ]

            return state_list

        return None