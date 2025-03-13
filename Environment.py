import pygame
from Constants import *
from Car import Car
from Obstacle import Obstacle
from drawing import draw_finished, draw_failed, draw_ui, draw_countdown, draw_pause_overlay
import math

class Environment:
    def __init__(self, surface, ai_train_mode=False, car_color1=None, car_color2=None):
        self.surface = surface
        self.grass = pygame.image.load(GRASS).convert()
        self.ai_train_mode = ai_train_mode
        
        self.game_states = ["countdown", "running", "finished", "failed", "paused"]
        self.game_state = "running" if ai_train_mode else "countdown"
        self.previous_state = None
        
        self.car1_active = car_color1 is not None
        self.car2_active = car_color2 is not None
        self.car1_finished = False
        self.car2_finished = False

        start_x, start_y = CAR_START_POS
        self._setup_cars(start_x, start_y, car_color1, car_color2)
        
        self.num_obstacles = 40 if self.car1_active and self.car2_active else 20
        self.obstacle_group = pygame.sprite.Group()
        self._generate_obstacles()
        
        self._setup_track()
        
        self.car1_time = TARGET_TIME if self.car1_active else 0
        self.car2_time = TARGET_TIME if self.car2_active else 0
        self.remaining_time = max(self.car1_time, self.car2_time)
                
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
        obstacle_generator = Obstacle(0, 0)
        self.obstacle_group.add(
            obstacle_generator.generate_obstacles(self.num_obstacles) 
        )

    def run_countdown(self):
        if self.game_state == "countdown":
            if not self.ai_train_mode:
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
                self.handle_music(True)
            else:
                self.game_state = "running"
                
    def draw(self):
        self.surface.blits((
            (self.grass, (0, 0)),
            (self.track, (0, 0)),
            (self.finish_line, self.finish_line_position),
        ))

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
        self.handle_music(False)

        start_x, start_y = CAR_START_POS
        
        if self.car1_active and self.car2_active:
            if self.car1_active:
                self.car1.reset(start_x + 20, start_y)
                self.car1_finished = False
                self.car1_time = TARGET_TIME
                
            if self.car2_active:
                self.car2.reset(start_x - 20, start_y)
                self.car2_finished = False
                self.car2_time = TARGET_TIME
        else:
            if self.car1_active:
                self.car1.reset(start_x, start_y)
                self.car1_finished = False
                self.car1_time = TARGET_TIME
                
            if self.car2_active:
                self.car2.reset(start_x, start_y)
                self.car2_finished = False
                self.car2_time = TARGET_TIME

        self.remaining_time = max(self.car1_time, self.car2_time)

        obstacle_generator = Obstacle(0, 0)
        obstacle_generator.reshuffle_obstacles(self.obstacle_group, self.num_obstacles)

        self.state_timer = 0
        self.game_state = "running" if self.ai_train_mode else "countdown"
        
        if not self.ai_train_mode:
            self.handle_music(False)
            
        self.run_countdown()

    def check_game_end_condition(self):
        any_racing = ((self.car1_active and not self.car1_finished and not self.car1.failed and self.car1_time > 0) or 
                    (self.car2_active and not self.car2_finished and not self.car2.failed and self.car2_time > 0))
        
        if not any_racing:
            self.handle_music(False)
            
            any_finished = ((self.car1_active and self.car1_finished) or 
                            (self.car2_active and self.car2_finished))
            
            if any_finished:
                self.game_state = "finished"
                if not self.ai_train_mode and (self.car1_finished or self.car2_finished):
                    self.win_sound.play()
            else:
                self.game_state = "failed"
                
            if self.ai_train_mode:
                self.restart_game()
                
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
                self.car1.velocity *= 0.25  
                if not self.ai_train_mode:
                    self.obstacle_sound.play()
                obstacle.kill()
            
            elif (self.car2_active and not self.car2_finished and not self.car2.failed and 
                  self.car2_time > 0 and pygame.sprite.collide_mask(self.car2, obstacle)):
                self.car2.velocity *= 0.25  
                if not self.ai_train_mode:
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
            if not self.ai_train_mode:
                self.collide_sound.play()
            collision_detected = True
        
        if overlap := self.finish_mask.overlap(car.mask, finish_offset):
            if overlap[1] <= 2: 
                car.failed = True
                car.can_move = False 
                if not self.ai_train_mode:
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
                    if not self.ai_train_mode:
                        self.win_sound.play()
                    any_finished = True

        if self.car2_active and not self.car2_finished and not self.car2.failed:
            car2_offset = (int(self.car2.rect.left - self.finish_line_position[0]), 
                           int(self.car2.rect.top - self.finish_line_position[1]))
            if finish := self.finish_mask.overlap(self.car2.mask, car2_offset):
                if finish[1] > 2: 
                    self.car2_finished = True
                    if not self.ai_train_mode:
                        self.win_sound.play()
                    any_finished = True
                    
        if any_finished:
            self.check_game_end_condition()

        return any_finished
                
    def setup_sound(self):
        volume_multiplier = 0 if self.ai_train_mode else 1
        
        self.background_music = pygame.mixer.Sound(BACKGROUND_MUSIC)
        self.background_music.set_volume(0.01 * volume_multiplier)
        
        self.collide_sound = pygame.mixer.Sound(COLLIDE_SOUND)
        self.collide_sound.set_volume(4 * volume_multiplier)
        
        self.win_sound = pygame.mixer.Sound(WIN_SOUND)
        self.win_sound.set_volume(0.2 * volume_multiplier)

        self.obstacle_sound = pygame.mixer.Sound(OBSTACLE_SOUND)  
        self.obstacle_sound.set_volume(0.08 * volume_multiplier)

        self.countdown_sound = pygame.mixer.Sound(COUNTDOWN_SOUND)
        self.countdown_sound.set_volume(0.1 * volume_multiplier)

        self.is_music_playing = False

    def toggle_pause(self):
        if self.game_state == "running":
            self.previous_state = self.game_state
            self.game_state = "paused"
            self.handle_music(False)
        elif self.game_state == "paused":
            self.game_state = self.previous_state
            self.handle_music(True)

    def handle_music(self, play=True):
        if play and not self.is_music_playing and not self.ai_train_mode:
            self.background_music.play(-1)
            self.is_music_playing = True
        elif not play and self.is_music_playing:
            self.background_music.stop()
            self.is_music_playing = False

    def state(self):
        if not self.car1_active:
            return None
            
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