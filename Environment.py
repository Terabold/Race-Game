import pygame
import numpy as np
import torch
from Constants import *
from Car import Car
from Checkpoint import Checkpoint
from TimeBonus import TimeBonus

def font_scale(size, Font=FONT):
    return pygame.font.Font(Font, size)

def blit_rotate_center(game, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    game.blit(rotated_image, new_rect.topleft)

class Environment:
    def __init__(self, surface, sound_enabled=True, auto_respawn=False, car_color1=None, car_color2=None):
        self.surface = surface
        self.grass = pygame.transform.scale(pygame.image.load(GRASS).convert(), (WIDTH, HEIGHT))
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
        
        if self.car1_active:
            self.car1 = Car(start_pos[0], start_pos[1], car_color1)
        else:
            self.car1 = None

        if self.car2_active:
            self.car2 = Car(start_pos[0], start_pos[1], car_color2)  
        else:
            self.car2 = None
        
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
    
    def calculate_score(self, remaining_time, collected_bonuses):
        return int(remaining_time * 100 + collected_bonuses * 50)
    
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
        
        self.checkpoint_group1.empty()
        self.checkpoint_group2.empty()
        self.current_checkpoint_index1 = 0
        self.current_checkpoint_index2 = 0
        
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
        current_checkpoint_index = self.current_checkpoint_index1 if car_num == 1 else self.current_checkpoint_index2
        
        unpassed_checkpoints = [cp for cp in checkpoint_group.sprites() if not cp.passed]
        
        if not unpassed_checkpoints:
            return None
        
        closest_checkpoint = unpassed_checkpoints[0]
        for checkpoint in unpassed_checkpoints:
            if checkpoint.index < closest_checkpoint.index:
                closest_checkpoint = checkpoint
                
        return closest_checkpoint
    
    def check_finish(self):
        if not self.car1_finished and self.car1_active:
            car1_finish = self.car1.collide(self.finish_mask, *self.finish_line_position)
            if car1_finish and all(cp.passed for cp in self.checkpoint_group1.sprites()):
                self.car1_finished = True
                self.car1_finish_time = self.remaining_time
                self.car1_score = self.calculate_score(self.remaining_time, 
                                                     len(self.initial_bonuses) - len(self.time_bonus_group))
                self.win_sound.play()

        if self.car2_active and not self.car2_finished:
            car2_finish = self.car2.collide(self.finish_mask, *self.finish_line_position)
            if car2_finish and all(cp.passed for cp in self.checkpoint_group2.sprites()):
                self.car2_finished = True
                self.car2_finish_time = self.remaining_time
                self.car2_score = self.calculate_score(self.remaining_time, 
                                                     len(self.initial_bonuses) - len(self.time_bonus_group))
                self.win_sound.play()

        if (self.car1_finished and not self.car2_active) or \
           (self.car1_finished and self.car2_finished):
            self.handle_music(False)
            self.game_state = "game_complete" if self.current_level >= len(LEVELS) - 1 else "level_complete"
            return True

        return False

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
            self.draw_pause_overlay()
        elif self.game_state == "running":
            self.draw_ui()
        elif self.game_state == "level_complete":
            self.draw_level_complete()
        elif self.game_state == "game_complete":
            self.draw_game_complete()
            
    def draw_pause_overlay(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.surface.blit(overlay, (0, 0))
        
        texts = [
            (font_scale(75).render("GAME PAUSED", True, GREEN), (WIDTH // 2, HEIGHT // 2 - 50)),
            (font_scale(30).render("Press ESC to Resume", True, WHITE), (WIDTH // 2, HEIGHT // 2 + 20)),
            (font_scale(30).render(f"Time Remaining: {self.remaining_time:.1f}", True, WHITE), 
             (WIDTH // 2, HEIGHT // 2 + 70))
        ]
        
        for text, pos in texts:
            rect = text.get_rect(center=pos)
            self.surface.blit(text, rect)

    def draw_ui(self):
        y_offset = 5
        if self.car1_active:
            timer_color = RED if self.car1_time < 1 and not self.car1_finished else GREEN
            timer_text = font_scale(27).render(
                f"P1 Time: {self.car1_time:.1f}" if not self.car1_finished else "P1: Finished!", 
                True, 
                timer_color
            )
            self.surface.blit(timer_text, (10, y_offset))
            y_offset += 30
            
        if self.car2_active:
            timer_color = RED if self.car2_time < 1 and not self.car2_finished else GREEN
            timer_text = font_scale(27).render(
                f"P2 Time: {self.car2_time:.1f}" if not self.car2_finished else "P2: Finished!", 
                True, 
                timer_color
            )
            self.surface.blit(timer_text, (10, y_offset))

    def toggle_pause(self):
        if self.game_state == "paused":
            self.game_state = self.previous_state
            if self.game_state == "running":
                self.handle_music(True)
        elif self.game_state in ["running", "countdown"]:
            self.previous_state = self.game_state
            self.game_state = "paused"
            self.handle_music(False)

    def draw_level_complete(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.surface.blit(overlay, (0, 0))
        
        title = font_scale(60).render("Level Complete!", True, GREEN)
        self.surface.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))
        
        y_offset = HEIGHT // 2 - 20
        if self.car1_active:
            if self.car1_finished:
                time_text = font_scale(40).render(f"Player 1: Finished!", True, DODGERBLUE)
            else:
                time_text = font_scale(40).render(f"Player 1: Time Up!", True, RED)
            self.surface.blit(time_text, time_text.get_rect(center=(WIDTH // 2, y_offset)))
            y_offset += 40
            
        if self.car2_active:
            if self.car2_finished:
                time_text = font_scale(40).render(f"Player 2: Finished!", True, DODGERBLUE)
            else:
                time_text = font_scale(40).render(f"Player 2: Time Up!", True, RED)
            self.surface.blit(time_text, time_text.get_rect(center=(WIDTH // 2, y_offset)))
            y_offset += 40
        
        continue_text = font_scale(30).render("Press SPACE to continue", True, WHITE)
        self.surface.blit(continue_text, continue_text.get_rect(center=(WIDTH // 2, y_offset + 20)))

    def draw_game_complete(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.surface.blit(overlay, (0, 0))
        
        texts = [
            (font_scale(60).render("Game Complete!", True, GREEN), (WIDTH // 2, HEIGHT // 2 - 100))
        ]
        
        if self.car1_active:
            status = "Finished!" if self.car1_finished else "Time Up!"
            texts.append((font_scale(40).render(f"Player 1: {status}", True, DODGERBLUE),
                (WIDTH // 2, HEIGHT // 2)))
        
        if self.car2_active:
            status = "Finished!" if self.car2_finished else "Time Up!"
            texts.append((font_scale(40).render(f"Player 2: {status}", True, RED),
                (WIDTH // 2, HEIGHT // 2 + 50)))
        
        texts.append((font_scale(30).render("Press SPACE to play again", True, WHITE),
            (WIDTH // 2, HEIGHT // 2 + 120)))
        
        for text, pos in texts:
            rect = text.get_rect(center=pos)
            self.surface.blit(text, rect)
            
    def draw_countdown(self, count):
        level_text = font_scale(100).render(self.current_level_data["Level"], True, GOLD)
        level_rect = level_text.get_rect(center=(WIDTH // 2, 75))
        self.surface.blit(level_text, level_rect)

        shadow = font_scale(175, COUNTDOWN_FONT).render(str(count), True, BLACK)
        shadow_surface = pygame.Surface(shadow.get_size(), pygame.SRCALPHA)
        shadow_surface.blit(shadow, (0, 0))
        shadow_surface.set_alpha(200)
        
        shadow_rect = shadow_surface.get_rect(center=(WIDTH // 2 + 5, HEIGHT // 2 + 5))
        text = font_scale(175, COUNTDOWN_FONT).render(str(count), True, RED)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        self.surface.blits((
            (shadow_surface, shadow_rect),
            (text, text_rect)
        ))

    def handle_completion(self):
        if self.remaining_time > 0:
            if self.current_level < len(LEVELS) - 1:
                self.game_state = "level_complete"
                self.current_level += 1
                self.load_level(self.current_level)
            else:
                self.game_state = "game_complete"
                self.handle_music(False)
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
                self.car1_time -= 1/FPS
                if self.car1_time <= 0:
                    self.car1_time = 0
            
            if self.car2_active and not self.car2_finished:
                self.car2_time -= 1/FPS
                if self.car2_time <= 0:
                    self.car2_time = 0
            
            self.remaining_time = max(
                self.car1_time if self.car1_active else 0,
                self.car2_time if self.car2_active else 0
            )
            
            car1_inactive = not self.car1_active or self.car1_finished or self.car1_time <= 0
            car2_inactive = not self.car2_active or self.car2_finished or self.car2_time <= 0

            if car1_inactive and car2_inactive:
                self.game_state = "game_complete" if self.current_level >= len(LEVELS) - 1 else "level_complete"
                self.handle_music(False)
            else:
                self.check_collision()
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

        if self.car1_active and not self.car1_finished and self.car1_time > 0 and action1 is not None:
            self._handle_car_movement(self.car1, action1)

        if self.car2_active and not self.car2_finished and self.car2_time > 0 and action2 is not None:
            self._handle_car_movement(self.car2, action2)

        self.check_collision()
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
    
    def check_collision(self):
        collision1 = False
        collision2 = False
        
        if self.car1_active and self.car1:
            collision1 = self.car1.collide(self.track_border_mask)
            if collision1:
                self.car1.handle_border_collision()
                if self.sound_enabled:
                    self.collide_sound.play()
            
        if self.car2_active and self.car2:
            collision2 = self.car2.collide(self.track_border_mask)
            if collision2:
                self.car2.handle_border_collision()
                if self.sound_enabled:
                    self.collide_sound.play()

        return collision1 or collision2


    def check_finish(self):
        any_finished = False
        
        if self.car1_active and self.car1 and not self.car1_finished:
            car1_finish = self.car1.collide(self.finish_mask, *self.finish_line_position)
            if car1_finish is not None: 
                if car1_finish[1] != 0 and all(cp.passed for cp in self.checkpoint_group1.sprites()):
                    self.car1_finished = True
                    self.car1_finish_time = self.remaining_time
                    if self.car1_time > 0:
                        self.car1_score = self.calculate_score(self.remaining_time, 
                                                            len(self.initial_bonuses) - len(self.time_bonus_group))
                        if self.sound_enabled:
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
                    if self.car2_time > 0:
                        self.car2_score = self.calculate_score(self.remaining_time, 
                                                            len(self.initial_bonuses) - len(self.time_bonus_group))
                        if self.sound_enabled:
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
            self.game_state = "game_complete" if self.current_level >= len(LEVELS) - 1 else "level_complete"
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
        
        self.checkpoint_sound = pygame.mixer.Sound(CHECKPOINT_SOUND)
        self.checkpoint_sound.set_volume(0.3 * volume_multiplier)

        self.time_bonus_sound = pygame.mixer.Sound(TIME_BONUS_SOUND)  
        self.time_bonus_sound.set_volume(0.2 * (1 if self.sound_enabled else 0))

        self.is_music_playing = False

    def handle_music(self, play=True):
        if play and not self.is_music_playing:
            self.background_music.play(-1)
            self.is_music_playing = True
        elif not play:
            self.background_music.stop()
            self.is_music_playing = False

    def state(self):
        """Returns both screen tensor and state parameters for AI training"""
        # Convert the game surface to a 3D array (width, height, color)
        screen = pygame.surfarray.array3d(self.surface)

        # Rearrange dimensions to (color, height, width) for PyTorch
        screen = screen.transpose((2, 0, 1))

        # Convert to PyTorch tensor and normalize colors to range 0-1
        screen_tensor = torch.FloatTensor(screen)  # Convert to tensor
        screen_tensor = screen_tensor / 255.0      # Normalize colors
        
        # Get state parameters as before
        state_list = [
            self.car.x / WIDTH,                    
            self.car.y / HEIGHT,                   
            self.car.velocity / self.car.max_velocity,  
            self.car.angle / 360.0,                
            self.car.drift_momentum / self.car.max_velocity,
            self.finish_line_position[0] / WIDTH,  
            self.finish_line_position[1] / HEIGHT, 
            self.car.acceleration / ACCELERATION,   
        ]
        state_params = torch.tensor(state_list, dtype=torch.float32)
        
        return screen_tensor, state_params