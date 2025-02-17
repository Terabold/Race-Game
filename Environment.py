import pygame
from Constants import *
from Car import Car
from Obstacle import Obstacle
from drawing import draw_finished, draw_countdown, draw_pause_overlay, draw_ui

class Environment:
    def __init__(self, surface, sound_enabled=True, auto_respawn=False, car_color1=None, car_color2=None, countdown_enabled=False):
        self.surface = surface
        self.grass = pygame.image.load(GRASS).convert()
        self.auto_respawn = auto_respawn
        self.sound_enabled = sound_enabled
        
        self.paused = False
        self.game_state = "countdown"
        self.previous_state = None
        
        self.car1_active = car_color1 is not None
        self.car2_active = car_color2 is not None
        self.car1_finished = False
        self.car2_finished = False

        start_x, start_y = CAR_START_POS

        if self.car1_active and self.car2_active:
            self.car1 = Car(start_x + 20, start_y, car_color1)
            self.car2 = Car(start_x - 20, start_y, car_color2)
        else:
            if self.car1_active:
                self.car1 = Car(start_x, start_y, car_color1)
            if self.car2_active:
                self.car2 = Car(start_x, start_y, car_color2)

        self.all_sprites = pygame.sprite.Group()
        if self.car1_active:
            self.all_sprites.add(self.car1)
        if self.car2_active:
            self.all_sprites.add(self.car2)  

        self.num_obstacles = 40 if self.car1_active and self.car2_active else 20
        self.countdown_enabled = countdown_enabled

        self.track = pygame.image.load(TRACK).convert_alpha()
        self.track_border = pygame.image.load(TRACK_BORDER).convert_alpha()
        self.track_border_mask = pygame.mask.from_surface(self.track_border)
        
        self.finish_line = pygame.transform.scale(
            pygame.image.load(FINISHLINE).convert_alpha(),
            FINISHLINE_SIZE
        )
        self.finish_line_position = FINISHLINE_POS
        self.finish_mask = pygame.mask.from_surface(self.finish_line)
        

        self.car1_time = TARGET_TIME if self.car1_active else 0
        self.car2_time = TARGET_TIME if self.car2_active else 0
        self.remaining_time = max(self.car1_time, self.car2_time)
        
        self.obstacle_group = pygame.sprite.Group()
        obstacle_generator = Obstacle(0, 0)
        self.obstacle_group.add(
            obstacle_generator.generate_obstacles(self.num_obstacles) 
        )
        
        self.setup_sound()


    def run_countdown(self):
        if self.game_state == "countdown":
            if self.countdown_enabled:
                self.countdown_sound.play()
                for i in range(3, 0, -1):
                    self.draw()
                    draw_countdown(self, i)
                    pygame.display.update()
                    pygame.time.wait(1000)
                self.handle_music(True)
                self.game_state = "running"
            else:
                self.handle_music(True)
                self.game_state = "running"

    
    def draw(self):
        self.surface.blits((
            (self.grass, (0, 0)),
            (self.track, (0, 0)),
            (self.finish_line, self.finish_line_position),
        ))
                    
        self.obstacle_group.draw(self.surface)
        self.surface.blit(self.track_border, (0, 0))
            
        self.all_sprites.draw(self.surface)

        if self.game_state == "paused":
            draw_pause_overlay(self)
        elif self.game_state == "running":
            draw_ui(self)
        elif self.game_state == "finished":
            draw_finished(self)

    def restart_game(self):
        self.handle_music(False)
        start_x, start_y = CAR_START_POS
        if self.car1_active:
            self.car1.reset(start_x + 20, start_y)
            self.car1_finished = False
            self.car1_time = TARGET_TIME
        if self.car2_active:
            self.car2.reset(start_x - 20, start_y)
            self.car2_finished = False
            self.car2_time = TARGET_TIME
        self.remaining_time = max(self.car1_time, self.car2_time)

        obstacle_generator = Obstacle(0, 0)  
        obstacle_generator.reshuffle_obstacles(self.obstacle_group, self.num_obstacles)

        if self.auto_respawn:
            if self.countdown_enabled:
                self.game_state = "countdown" 
            else:
                self.game_state = "running"    
                self.handle_music(True)
        else:
            self.game_state = "countdown" 

    def update(self):
        if self.game_state == "countdown":
            self.run_countdown()
        elif self.game_state == "running":
            if self.car1_active and not self.car1_finished:
                self.car1_time = max(0, self.car1_time - 1/FPS)
            if self.car2_active and not self.car2_finished:
                self.car2_time = max(0, self.car2_time - 1/FPS)
            self.remaining_time = max(self.car1_time, self.car2_time)
            
            if self.check_finish():
                if self.auto_respawn:
                    self.restart_game() 
            self.check_obstacle()

    def move(self, action1, action2):
        if self.game_state != "running":
            return False

        if self.car1_active and not self.car1_finished and self.car1_time > 0:
            self._handle_car_movement(self.car1, action1)
            self.check_collision(self.car1)

        if self.car2_active and not self.car2_finished and self.car2_time > 0:
            self._handle_car_movement(self.car2, action2)
            self.check_collision(self.car2)

        return self.check_finish()

    def check_obstacle(self): 
        for obstacle in self.obstacle_group.sprites(): 
            if (self.car1_active and not self.car1_finished and self.car1_time > 0 and 
                pygame.sprite.collide_mask(self.car1, obstacle)):
                self.car1.velocity *= 0.25  
                if self.sound_enabled:
                    self.obstacle_sound.play()
                obstacle.kill()
                    
            elif (self.car2_active and not self.car2_finished and self.car2_time > 0 and 
                pygame.sprite.collide_mask(self.car2, obstacle)):
                self.car2.velocity *= 0.25  
                if self.sound_enabled:
                    self.obstacle_sound.play()
                obstacle.kill()

    def check_collision(self, car):
        offset = (int(car.rect.left), int(car.rect.top))
        finish_offset = (int(car.rect.left - self.finish_line_position[0]), 
                        int(car.rect.top - self.finish_line_position[1]))
        
        if self.track_border_mask.overlap(car.mask, offset):
            car.handle_border_collision()
            if self.sound_enabled:
                self.collide_sound.play()
            return True
        
        if overlap := self.finish_mask.overlap(car.mask, finish_offset):
            if overlap[1] <= 2: 
                car.handle_border_collision()
                if self.sound_enabled:
                    self.collide_sound.play()
                return True
        return False

    def _handle_car_movement(self, car, action):
        moving = action in [1, 2, 5, 6, 7, 8]
        
        if action in [3, 5, 7]:
            car.rotate(left=True)
            if (car.check_and_handle_rotation_collision(self.track_border_mask) or 
                car.check_and_handle_rotation_collision(self.finish_mask, self.finish_line_position)):
                if self.sound_enabled:
                    self.collide_sound.play()

        elif action in [4, 6, 8]:
            car.rotate(right=True)
            if (car.check_and_handle_rotation_collision(self.track_border_mask) or 
                car.check_and_handle_rotation_collision(self.finish_mask, self.finish_line_position)):
                if self.sound_enabled:
                    self.collide_sound.play()
        
        if action in [1, 5, 6]:
            car.accelerate(True)
        elif action in [2, 7, 8]:
            car.accelerate(False)
        
        if not moving:
            car.reduce_speed()
    
    def check_finish(self):
        any_finished = False
        
        if self.car1_active and self.car1 and not self.car1_finished:
            car1_offset = (int(self.car1.rect.left - self.finish_line_position[0]), 
                        int(self.car1.rect.top - self.finish_line_position[1]))
            if finish := self.finish_mask.overlap(self.car1.mask, car1_offset):
                if finish[1] != 0:  
                    self.car1_finished = True
                    if self.sound_enabled:
                        self.win_sound.play()
                    any_finished = True

        if self.car2_active and self.car2 and not self.car2_finished:
            car2_offset = (int(self.car2.rect.left - self.finish_line_position[0]), 
                        int(self.car2.rect.top - self.finish_line_position[1]))
            if finish := self.finish_mask.overlap(self.car2.mask, car2_offset):
                if finish[1] != 0:  
                    self.car2_finished = True
                    if self.sound_enabled:
                        self.win_sound.play()
                    any_finished = True

        # Check if either car has finished or time has run out
        if any_finished or self.remaining_time <= 0:
            self.handle_music(False)
            self.game_state = "finished"
            
            if self.auto_respawn:
                self.restart_game()
                if self.countdown_enabled:
                    self.game_state = "countdown"  
                else:
                    self.game_state = "running"  
                return True 
            return True 

        return any_finished
                
    def setup_sound(self):
        volume_multiplier = 1 if self.sound_enabled else 0
        
        self.background_music = pygame.mixer.Sound(BACKGROUND_MUSIC)
        self.background_music.set_volume(0.01 * volume_multiplier)
        
        self.countdown_sound = pygame.mixer.Sound(COUNTDOWN_SOUND)
        self.countdown_sound.set_volume(0.1 * volume_multiplier)
        
        self.collide_sound = pygame.mixer.Sound(COLLIDE_SOUND)
        self.collide_sound.set_volume(4 * volume_multiplier)
        
        self.win_sound = pygame.mixer.Sound(WIN_SOUND)
        self.win_sound.set_volume(0.2 * volume_multiplier)

        self.obstacle_sound = pygame.mixer.Sound(OBSTACLE_SOUND)  
        self.obstacle_sound.set_volume(0.08 * volume_multiplier)

        self.is_music_playing = False

    def handle_music(self, play=True):
        if play and not self.is_music_playing:
            self.background_music.play(-1)
            self.is_music_playing = True
        elif not play:
            self.background_music.stop()
            self.is_music_playing = False

    def state(self):
        """Returns state parameters for AI training"""
        if not self.car1_active:
            return None
        
        # Normalize ray distances
        normalized_rays = self.car1.get_raycast_data()
        
        # Combine all state information
        state_list = [
            *normalized_rays,                    # 7 ray distances
            self.car1.velocity / self.car1.max_velocity,  # Normalized velocity
            self.car1.angle / 360.0,            # Normalized angle
            self.car1.x / WIDTH,                # Normalized x position
            self.car1.y / HEIGHT,               # Normalized y position
        ]
        
        return state_list