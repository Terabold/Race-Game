import pygame
from Constants import *
from Car import Car
from TimeBonus import TimeBonus
from drawing import draw_level_complete, draw_game_complete, draw_countdown, draw_pause_overlay, draw_ui
from Checkpoint import Checkpoint

def blit_rotate_center(game, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    game.blit(rotated_image, new_rect.topleft)

class Environment:
    def __init__(self, surface, sound_enabled=True, auto_respawn=False, car_color1=None, car_color2=None):
        self.surface = surface
        self.grass = pygame.image.load(GRASS).convert()
        self.current_level = 0
        self.auto_respawn = auto_respawn
        self.sound_enabled = sound_enabled
        
        self.paused = False
        self.game_state = "countdown"
        self.previous_state = None
        
        self.car1_active = car_color1 is not None
        self.car2_active = car_color2 is not None
        self.car1_finished = False
        self.car2_finished = False
        
        start_pos = LEVELS[0]["car_start_pos"]
        
        self.car1 = Car(start_pos[0], start_pos[1], car_color1) if self.car1_active else None
        self.car2 = Car(start_pos[0], start_pos[1], car_color2) if self.car2_active else None
        
        self.car1_time = LEVELS[0]["target_time"] if self.car1_active else 0
        self.car2_time = LEVELS[0]["target_time"] if self.car2_active else 0
        self.remaining_time = max(self.car1_time, self.car2_time)
        
        self.checkpoint_group1 = pygame.sprite.Group()
        self.checkpoint_group2 = pygame.sprite.Group()
        self.current_checkpoint_index1 = 0 if self.car1_active else None
        self.current_checkpoint_index2 = 0 if self.car2_active else None

        self.time_bonus_group = pygame.sprite.Group()
        self.initial_bonuses = []
        
        self.setup_sound()
        self.load_level(self.current_level)
    
    def load_level(self, level_index):
        level_data = LEVELS[level_index]
        self.current_level_data = level_data
        
        start_pos = level_data["car_start_pos"]
        if self.car1_active:
            self.car1.reset(start_pos[0], start_pos[1])
            self.car1_finished = False
            self.car1_time = level_data["target_time"]  
            
        if self.car2_active:
            self.car2.reset(start_pos[0], start_pos[1])
            self.car2_finished = False
            self.car2_time = level_data["target_time"]  
            
        self.remaining_time = max(
            self.car1_time if self.car1_active else 0,
            self.car2_time if self.car2_active else 0
        )
        
        self.track = pygame.image.load(level_data["track_image"]).convert_alpha()
        self.track_border = pygame.image.load(level_data["border_image"]).convert_alpha()
        self.track_border_mask = pygame.mask.from_surface(self.track_border)
        
        finish_img = pygame.image.load(FINISHLINE).convert_alpha()
        finishline_width, finishline_height = level_data["finishline_size"]
        self.finish_line = pygame.transform.scale(finish_img, (finishline_width, finishline_height))
        self.finish_line_position = level_data["finishline_pos"]
        self.finish_mask = pygame.mask.from_surface(self.finish_line)
        
        self.game_state = "countdown"

        for i, checkpoint_data in enumerate(level_data.get("checkpoints", [])):
            if self.car1_active:
                checkpoint1 = Checkpoint(checkpoint_data["pos"], checkpoint_data["size"], i)
                self.checkpoint_group1.add(checkpoint1)
                
            if self.car2_active:
                checkpoint2 = Checkpoint(checkpoint_data["pos"], checkpoint_data["size"], i)
                self.checkpoint_group2.add(checkpoint2)

        self.time_bonus_group.empty()
        track_name = f"track{level_index + 1}"
        time_bonus_generator = TimeBonus(0, 0)
        num_bonuses = 40 if self.car1_active and self.car2_active else 20
        self.time_bonus_group.add(time_bonus_generator.generate_bonuses(track_name, num_bonuses=num_bonuses))

    def get_closest_active_checkpoint(self, car_num=1):
        checkpoint_group = self.checkpoint_group1 if car_num == 1 else self.checkpoint_group2
        
        unpassed_checkpoints = [cp for cp in checkpoint_group.sprites() if not cp.passed]
        
        if not unpassed_checkpoints:
            return None
        
        closest_checkpoint = unpassed_checkpoints[0]
        for checkpoint in unpassed_checkpoints:
            if checkpoint.index < closest_checkpoint.index:
                closest_checkpoint = checkpoint
                
        return closest_checkpoint
    
    def check_finish(self):
        any_finished = False
        
        if self.car1_active and self.car1 and not self.car1_finished:
            car1_finish = self.car1.collide(self.finish_mask, *self.finish_line_position)
            if car1_finish is not None: 
                if car1_finish[1] != 0 and all(cp.passed for cp in self.checkpoint_group1.sprites()):  
                    self.car1_finished = True
                    self.car1_finish_time = self.remaining_time
                    if self.car1_time > 0 and self.sound_enabled:
                        self.win_sound.play()
                    any_finished = True
                else:
                    self.car1.handle_border_collision()

        if self.car2_active and self.car2 and not self.car2_finished:
            car2_finish = self.car2.collide(self.finish_mask, *self.finish_line_position)
            if car2_finish is not None:  
                if car2_finish[1] != 0 and all(cp.passed for cp in self.checkpoint_group2.sprites()): 
                    self.car2_finished = True
                    self.car2_finish_time = self.remaining_time
                    if self.car2_time > 0 and self.sound_enabled:
                        self.win_sound.play()
                    any_finished = True
                else:
                    self.car2.handle_border_collision()

        all_finished = (
            (self.car1_active and not self.car2_active and self.car1_finished) or
            (not self.car1_active and self.car2_active and self.car2_finished) or
            (self.car1_active and self.car2_active and self.car1_finished and self.car2_finished) or
            self.remaining_time <= 0
        )

        if all_finished:
            self.handle_music(False)
            self.game_state = "game_complete" if self.current_level >= len(LEVELS)-1 else "level_complete"
            return True

        return any_finished
    
    def run_countdown(self):
        if self.game_state == "countdown":
            self.countdown_sound.play()
            for i in range(3, 0, -1):
                self.draw()
                self.draw_countdown(i)
                pygame.display.update()
                pygame.time.wait(1000)
            self.handle_music(True)
            self.game_state = "running"

    def draw(self):
        self.surface.blits((
            (self.grass, (0, 0)),
            (self.track, (0, 0)),
            (self.finish_line, self.finish_line_position),
        ))
        
        if self.car1_active:
            for checkpoint in self.checkpoint_group1:
                if not checkpoint.passed:
                    self.surface.blit(checkpoint.image, checkpoint.rect)
                    
        if self.car2_active:
            for checkpoint in self.checkpoint_group2:
                if not checkpoint.passed:
                    self.surface.blit(checkpoint.image, checkpoint.rect)
                    
        self.time_bonus_group.draw(self.surface)
        self.surface.blit(self.track_border, (0, 0))
            
        if self.car1 and self.car1_active:
            blit_rotate_center(self.surface, self.car1.image, (self.car1.x, self.car1.y), self.car1.angle)
        if self.car2 and self.car2_active:
            blit_rotate_center(self.surface, self.car2.image, (self.car2.x, self.car2.y), self.car2.angle)
   
        if self.game_state == "paused":
            draw_pause_overlay(self)
        elif self.game_state == "running":
            draw_ui(self)
        elif self.game_state == "level_complete":
            draw_level_complete(self)
        elif self.game_state == "game_complete":
            draw_game_complete(self)

    def run_countdown(self):
        if self.game_state == "countdown":
            self.countdown_sound.play()
            for i in range(3, 0, -1):
                self.draw()
                draw_countdown(self, i)  
                pygame.display.update()
                pygame.time.wait(1000)
            self.handle_music(True)
            self.game_state = "running"


    def toggle_pause(self):
        if self.game_state == "paused":
            self.game_state = self.previous_state
            if self.game_state == "running":
                self.handle_music(True)
        elif self.game_state in ["running", "countdown"]:
            self.previous_state = self.game_state
            self.game_state = "paused"
            self.handle_music(False)


    def handle_completion(self):
        if self.game_state == "level_complete":
            if self.car1_finished or self.car2_finished:
                if self.current_level < len(LEVELS) - 1:
                    self.current_level += 1
                    self.load_level(self.current_level)
                else:
                    self.game_state = "game_complete"
                    self.handle_music(False)
            else:
                if self.auto_respawn:
                    self.restart_level()
                else:
                    self.load_level(self.current_level)

    def restart_game(self):
        self.current_level = 0
        self.handle_music(False)
        self.load_level(self.current_level)
        
    def restart_level(self):
        self.handle_music(False)
        self.load_level(self.current_level)

    def update(self):
        if self.game_state == "countdown":
            self.run_countdown()
        elif self.game_state == "running":
            if self.car1_active and not self.car1_finished:
                self.car1_time -= 1 / FPS
                if self.car1_time <= 0:
                    self.car1_time = 0

            if self.car2_active and not self.car2_finished:
                self.car2_time -= 1 / FPS
                if self.car2_time <= 0:
                    self.car2_time = 0

            self.remaining_time = max(
                self.car1_time if self.car1_active else 0,
                self.car2_time if self.car2_active else 0
            )

            car1_failed = not self.car1_active or self.car1_finished or self.car1_time <= 0
            car2_failed = not self.car2_active or self.car2_finished or self.car2_time <= 0

            if car1_failed and car2_failed:
                if self.car1_finished or self.car2_finished:
                    self.game_state = "game_complete" if self.current_level >= len(LEVELS) - 1 else "level_complete"
                    self.handle_music(False)
                else:
                    if self.auto_respawn:
                        self.restart_level()
                    else:
                        self.game_state = "level_complete"
                        self.handle_music(False)
            else:
                self.check_checkpoints()
                self.check_time_bonuses()
            
    def check_checkpoints(self):
        if self.car1_active and self.car1:
            closest_checkpoint1 = self.get_closest_active_checkpoint(1)
            if closest_checkpoint1 and self.car1.collide(closest_checkpoint1.mask, closest_checkpoint1.rect.x, closest_checkpoint1.rect.y):
                closest_checkpoint1.passed = True
                self.current_checkpoint_index1 += 1
                if self.sound_enabled:
                    self.checkpoint_sound.play()

        if self.car2_active and self.car2:
            closest_checkpoint2 = self.get_closest_active_checkpoint(2)
            if closest_checkpoint2 and self.car2.collide(closest_checkpoint2.mask, closest_checkpoint2.rect.x, closest_checkpoint2.rect.y):
                closest_checkpoint2.passed = True
                self.current_checkpoint_index2 += 1
                if self.sound_enabled:
                    self.checkpoint_sound.play()

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

    def check_time_bonuses(self):
        for bonus in self.time_bonus_group.sprites():
            if (self.car1_active and not self.car1_finished and self.car1_time > 0 and 
                self.car1.collide(bonus.mask, bonus.rect.x, bonus.rect.y)):
                self.car1_time += 1.0
                if self.sound_enabled:
                    self.time_bonus_sound.play()
                bonus.kill()
                
            elif (self.car2_active and not self.car2_finished and self.car2_time > 0 and 
                self.car2.collide(bonus.mask, bonus.rect.x, bonus.rect.y)):
                self.car2_time += 1.0
                if self.sound_enabled:
                    self.time_bonus_sound.play()
                bonus.kill()

    def _handle_car_movement(self, car, action):
        moving = action in [1, 2, 5, 6, 7, 8]
        
        if action in [1, 5, 6]:
            car.accelerate(True)
        elif action in [2, 7, 8]:
            car.accelerate(False)
            
        if action in [3, 5, 7]:
            car.rotate(left=True)
        elif action in [4, 6, 8]:
            car.rotate(right=True)
            
        if not moving:
            car.reduce_speed()
    
    def check_collision(self, car):
        if car.collide(self.track_border_mask):
            car.handle_border_collision()
            if self.sound_enabled:
                self.collide_sound.play()
            return True
        return False
                
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
        
        self.checkpoint_sound = pygame.mixer.Sound(CHECKPOINT_SOUND)
        self.checkpoint_sound.set_volume(0.3 * volume_multiplier)

        self.time_bonus_sound = pygame.mixer.Sound(TIME_BONUS_SOUND)  
        self.time_bonus_sound.set_volume(0.08 * (1 if self.sound_enabled else 0))

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
            
        # Get the closest checkpoint
        closest_checkpoint = self.get_closest_active_checkpoint(1)
        if closest_checkpoint:
            checkpoint_x = closest_checkpoint.rect.centerx / WIDTH
            checkpoint_y = closest_checkpoint.rect.centery / HEIGHT
        else:
            checkpoint_x = self.finish_line_position[0] / WIDTH
            checkpoint_y = self.finish_line_position[1] / HEIGHT
        
        # Normalize ray distances
        normalized_rays = self.car1.get_raycast_data()
        
        # Combine all state information
        state_list = [
            *normalized_rays,                    # 7 ray distances
            self.car1.velocity / self.car1.max_velocity,  # Normalized velocity
            self.car1.angle / 360.0,            # Normalized angle
            self.car1.x / WIDTH,                # Normalized x position
            self.car1.y / HEIGHT,               # Normalized y position
            checkpoint_x,                        # Target x position
            checkpoint_y,                        # Target y position
        ]
        
        return state_list