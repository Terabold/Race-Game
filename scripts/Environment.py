import pygame
from scripts.Constants import *
from scripts.Car import Car
from scripts.Obstacle import Obstacle
from scripts.utils import (draw_finished, draw_failed, draw_ui, 
                         draw_countdown, draw_pause_overlay, load_sound)
from pathlib import Path
import math

class Environment:
    """Environment for normal gameplay (human vs human, or human vs AI demo)"""
    def __init__(self, surface, car_color1=None, car_color2=None):
        self.surface = surface
        self.grass = pygame.image.load(GRASS).convert()

        self.game_state = "countdown"
        self.previous_state = None

        # Car setup
        self.car1_active = car_color1 is not None
        self.car2_active = car_color2 is not None
        self.car1_finished = False
        self.car2_finished = False

        start_x, start_y = CAR_START_POS
        self._setup_cars(start_x, start_y, car_color1, car_color2)

        # Obstacles
        self.num_obstacles = 15
        self.obstacle_group = pygame.sprite.Group()
        self._generate_obstacles()

        # Track
        self._setup_track()

        # Timers
        self.car1_time = TARGET_TIME if self.car1_active else 0
        self.car2_time = TARGET_TIME if self.car2_active else 0
        self.remaining_time = max(self.car1_time, self.car2_time)

        # Sound
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
        self.track = pygame.image.load(TRACK).convert_alpha()
        self.track_border = pygame.image.load(TRACK_BORDER).convert_alpha()
        self.track_border_mask = pygame.mask.from_surface(self.track_border)

        self.finish_line = pygame.transform.scale(
            pygame.image.load(FINISHLINE).convert_alpha(),
            FINISHLINE_SIZE
        )
        self.finish_line_position = FINISHLINE_POS
        self.finish_mask = pygame.mask.from_surface(self.finish_line)

    def _generate_obstacles(self):
        obstacle_generator = Obstacle(0, 0, ai_mode=False)
        self.obstacle_group.add(
            obstacle_generator.generate_obstacles(self.num_obstacles, ai_mode=False)
        )

    def run_countdown(self):
        if self.game_state == "countdown":
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

            self.game_state = "running"
            self.handle_music(play=True)

    def draw(self):
        self.surface.blits((
            (self.grass, (0, 0)),
            (self.track, (0, 0)),
            (self.finish_line, self.finish_line_position),
        ))

        self.obstacle_group.draw(self.surface)
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

        obstacle_generator = Obstacle(0, 0, ai_mode=False)
        obstacle_generator.reshuffle_obstacles(self.obstacle_group, self.num_obstacles, ai_mode=False)

        self.game_state = "countdown"
        self.countdown_sound.stop()
        self.handle_music(play=False)
        self.run_countdown()

    def check_game_end_condition(self):
        car1_racing = self.car1_active and not self.car1_finished and not self.car1.failed and self.car1_time > 0
        car2_racing = self.car2_active and not self.car2_finished and not self.car2.failed and self.car2_time > 0

        if not car1_racing and not car2_racing:
            any_finished = (self.car1_active and self.car1_finished) or (self.car2_active and self.car2_finished)

            if any_finished:
                self.game_state = "finished"
                self.handle_music(play=False)
                self.win_sound.play()
            else:
                self.game_state = "failed"
                self.handle_music(play=False)

            return True

        return False

    def update(self):
        if self.game_state == "countdown":
            self.run_countdown()

        elif self.game_state == "running":
            if self.car1_active and not self.car1_finished and not self.car1.failed:
                self.car1_time = max(0, self.car1_time - 1/FPS)
                if self.car1_time <= 0:
                    self.car1.can_move = False

            if self.car2_active and not self.car2_finished and not self.car2.failed:
                self.car2_time = max(0, self.car2_time - 1/FPS)
                if self.car2_time <= 0:
                    self.car2.can_move = False

            self.remaining_time = max(self.car1_time, self.car2_time)
            self.check_game_end_condition()

        self.all_sprites.update()

    def move(self, action1, action2):
        """
        Execute actions and return step information for both cars.
        """
        if self.game_state != "running":
            return False, {}, {}

        car1_info = {'collision': False, 'finished': False, 'hit_obstacle': False}
        car2_info = {'collision': False, 'finished': False, 'hit_obstacle': False}

        # Car 1
        if self.car1_active and not self.car1_finished and not self.car1.failed and self.car1_time > 0:
            pre_failed = self.car1.failed
            pre_finished = self.car1_finished
            pre_velocity = self.car1.velocity
            
            self._handle_car_movement(self.car1, action1)
            
            hit_obstacle = self._check_single_car_obstacle(self.car1, pre_velocity)
            just_finished = self._check_single_car_finish(self.car1, pre_finished)
            just_collided = self._check_single_car_collision(self.car1, pre_failed)
            
            car1_info = {
                'collision': just_collided,
                'finished': just_finished,
                'hit_obstacle': hit_obstacle
            }

        # Car 2
        if self.car2_active and not self.car2_finished and not self.car2.failed and self.car2_time > 0:
            pre_failed = self.car2.failed
            pre_finished = self.car2_finished
            pre_velocity = self.car2.velocity
            
            self._handle_car_movement(self.car2, action2)
            
            hit_obstacle = self._check_single_car_obstacle(self.car2, pre_velocity)
            just_finished = self._check_single_car_finish(self.car2, pre_finished)
            just_collided = self._check_single_car_collision(self.car2, pre_failed)
            
            car2_info = {
                'collision': just_collided,
                'finished': just_finished,
                'hit_obstacle': hit_obstacle
            }

        done = self.check_game_end_condition()
        return done, car1_info, car2_info

    def _check_single_car_obstacle(self, car, pre_velocity):
        """Check if a single car hit an obstacle and apply velocity reduction."""
        for obstacle in self.obstacle_group.sprites():
            if pygame.sprite.collide_mask(car, obstacle):
                car.velocity *= 0.25
                self.obstacle_sound.play()
                obstacle.kill()
                return pre_velocity > 1.0
        return False

    def _check_single_car_finish(self, car, was_finished):
        """Check if a car just crossed the finish line."""
        if was_finished or car.failed:
            return False
        
        car_offset = (int(car.rect.left - self.finish_line_position[0]),
                     int(car.rect.top - self.finish_line_position[1]))
        
        if finish_overlap := self.finish_mask.overlap(car.mask, car_offset):
            if finish_overlap[1] > 2:
                if car == self.car1:
                    self.car1_finished = True
                else:
                    self.car2_finished = True
                self.win_sound.play()
                return True
        
        return False

    def _check_single_car_collision(self, car, was_failed):
        """Check if a car just crashed."""
        if was_failed:
            return False
        
        offset = (int(car.rect.left), int(car.rect.top))
        finish_offset = (int(car.rect.left - self.finish_line_position[0]),
                        int(car.rect.top - self.finish_line_position[1]))
        
        if self.track_border_mask.overlap(car.mask, offset):
            car.failed = True
            car.can_move = False
            self.collide_sound.play()
            self.check_game_end_condition()
            return True
        
        if finish_overlap := self.finish_mask.overlap(car.mask, finish_offset):
            if finish_overlap[1] <= 2:
                car.failed = True
                car.can_move = False
                self.collide_sound.play()
                self.check_game_end_condition()
                return True
        
        return False

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

    def setup_sound(self):
        self.collide_sound = load_sound(COLLIDE_SOUND, volume=0.25)
        self.win_sound = load_sound(WIN_SOUND, volume=0.25)
        self.obstacle_sound = load_sound(OBSTACLE_SOUND, volume=0.25)
        self.countdown_sound = load_sound(COUNTDOWN_SOUND, volume=0.6)

        self.is_music_playing = False
        
        if pygame.mixer.get_init():
            pygame.mixer.music.load(str(Path(BACKGROUND_MUSIC)))
            pygame.mixer.music.set_volume(DEFAULT_SOUND_VOLUME)
        else:
            self.background_music = load_sound(BACKGROUND_MUSIC, volume=DEFAULT_SOUND_VOLUME)

    def toggle_pause(self):
        if self.game_state == "running":
            self.previous_state = self.game_state
            self.game_state = "paused"
            self.handle_music(play=False)
        elif self.game_state == "paused":
            self.game_state = self.previous_state
            self.handle_music(play=True)

    def handle_music(self, play=True):
        if not pygame.mixer.get_init():
            return

        if play:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
                self.is_music_playing = True
            else:
                if not self.is_music_playing:
                    pygame.mixer.music.play(-1)
                    self.is_music_playing = True
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
            self.is_music_playing = False

    def get_state(self, car_num=1):
        """Get current state for AI agent (for demo/inference mode)"""
        if car_num == 1:
            if not self.car1_active:
                return None
            car = self.car1
        elif car_num == 2:
            if not self.car2_active:
                return None
            car = self.car2
        else:
            return None

        car.cast_rays(self.track_border_mask, self.obstacle_group)

        normalized_rays = [dist / car.ray_length for dist in car.ray_distances]

        state = [
            *normalized_rays,
            car.velocity / car.max_velocity,
            math.cos(math.radians(car.angle)),
            math.sin(math.radians(car.angle)),
            car.position.x / WIDTH,
            car.position.y / HEIGHT
        ]

        return state