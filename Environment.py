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
        self.grass = pygame.transform.scale(
            pygame.image.load(GRASS).convert(), (WIDTH, HEIGHT)
        )
        self.current_level = 0
        self.auto_respawn = auto_respawn
        self.sound_enabled = sound_enabled
        
        # Game state initialization
        self.paused = False
        self.game_state = "countdown"
        self.previous_state = None
        
        # Player state tracking
        self.car1_active = car_color1 is not None
        self.car2_active = car_color2 is not None
        self.car1_score = 0 if self.car1_active else None
        self.car2_score = 0 if self.car2_active else None
        self.car1_finished = False
        self.car2_finished = False
        self.car1_finish_time = 0
        self.car2_finish_time = 0
        
        # Initialize cars only if they're active
        start_pos = LEVELS[0]["car_start_pos"]
        self.car1 = Car(start_pos[0], start_pos[1], car_color1) if self.car1_active else None
        self.car2 = Car(start_pos[0], start_pos[1], car_color2) if self.car2_active else None
        
        # Checkpoint tracking
        self.checkpoint_group1 = pygame.sprite.Group()
        self.checkpoint_group2 = pygame.sprite.Group()
        self.current_checkpoint_index1 = 0 if self.car1_active else None
        self.current_checkpoint_index2 = 0 if self.car2_active else None
        
        self.time_bonus_group = pygame.sprite.Group()
        self.remaining_time = LEVELS[0]["target_time"]
        self.initial_bonuses = []
        
        self.setup_sound()
        self.load_level(self.current_level)
    
    def calculate_score(self, remaining_time, collected_bonuses):
        base_score = remaining_time * 100  # Time bonus
        bonus_score = collected_bonuses * 50  # Points per bonus collected
        return int(base_score + bonus_score)
    
    def load_level(self, level_index):
        level_data = LEVELS[level_index]
        self.current_level_data = level_data
        
        # Reset cars to their starting positions
        start_pos = level_data["car_start_pos"]
        if self.car1_active:
            self.car1.reset(start_pos[0], start_pos[1])
            self.car1_finished = False
            
        if self.car2_active:
            self.car2.reset(start_pos[0], start_pos[1])
            self.car2_finished = False
            
        # Reset checkpoints
        self.checkpoint_group1.empty()
        self.checkpoint_group2.empty()
        self.current_checkpoint_index1 = 0
        self.current_checkpoint_index2 = 0
        
        # Load track images and masks
        self.track = pygame.image.load(level_data["track_image"]).convert_alpha()
        self.track_border = pygame.image.load(level_data["border_image"]).convert_alpha()
        self.track_border_mask = pygame.mask.from_surface(self.track_border)
        
        # Load finish line
        finish_img = pygame.image.load(FINISHLINE).convert_alpha()
        finishline_width, finishline_height = level_data["finishline_size"]
        self.finish_line = pygame.transform.scale(finish_img, (finishline_width, finishline_height))
        self.finish_line_position = level_data["finishline_pos"]
        self.finish_mask = pygame.mask.from_surface(self.finish_line)
        
        self.remaining_time = level_data["target_time"]
        self.game_state = "countdown"
        
        # Create checkpoints for each active player
        for i, checkpoint_data in enumerate(level_data.get("checkpoints", [])):
            if self.car1_active:
                checkpoint1 = Checkpoint(checkpoint_data["pos"], checkpoint_data["size"], i)
                self.checkpoint_group1.add(checkpoint1)
                
            if self.car2_active:
                # Offset player 2 checkpoints slightly if both players are active
                pos = list(checkpoint_data["pos"])
                if self.car1_active:
                    pos[1] += 10  # Offset Y position slightly down
                checkpoint2 = Checkpoint(pos, checkpoint_data["size"], i)
                self.checkpoint_group2.add(checkpoint2)

        # Reset time bonuses
        self.time_bonus_group.empty()
        track_name = f"track{level_index + 1}"
        time_bonus_generator = TimeBonus(0, 0)
        self.time_bonus_group.add(time_bonus_generator.generate_bonuses(track_name, num_bonuses=10))


    def get_closest_active_checkpoint(self, car_num=1):
        """Get closest active checkpoint for specified car"""
        checkpoint_group = self.checkpoint_group1 if car_num == 1 else self.checkpoint_group2
        current_checkpoint_index = self.current_checkpoint_index1 if car_num == 1 else self.current_checkpoint_index2
        car = self.car1 if car_num == 1 else self.car2
        
        active_checkpoints = [
            cp for cp in checkpoint_group.sprites() 
            if not cp.passed and cp.index >= current_checkpoint_index
        ]
        if not active_checkpoints:
            return None
            
        return min(active_checkpoints, 
                key=lambda cp: (cp.index != current_checkpoint_index,
                                cp.get_distance_to(car.x, car.y)))
    
    def check_finish(self):
        """Updated check_finish to handle scoring and finish states"""
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

        # Determine if level is complete
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
        # Draw base elements
        self.surface.blits((
            (self.grass, (0, 0)),
            (self.track, (0, 0)),
            (self.finish_line, self.finish_line_position),
        ))

        # Draw checkpoints for active players
        if self.car1_active:
            self.checkpoint_group1.draw(self.surface)
        if self.car2_active:
            self.checkpoint_group2.draw(self.surface)
            
        self.time_bonus_group.draw(self.surface)
        self.surface.blit(self.track_border, (0, 0))
        
        # Draw cars if they exist
        if self.car1:
            blit_rotate_center(self.surface, self.car1.image, (self.car1.x, self.car1.y), self.car1.angle)
        if self.car2:
            blit_rotate_center(self.surface, self.car2.image, (self.car2.x, self.car2.y), self.car2.angle)
        
        # Draw UI based on game state
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
        
        # Render all text at once
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
        # Timer
        timer_color = RED if self.remaining_time < 1 else GREEN
        timer_text = font_scale(27).render(f"Time Remaining: {self.remaining_time:.1f}", True, timer_color)
        self.surface.blit(timer_text, (10, 5))
        
        # Draw scores only for active players
        y_offset = 5
        if self.car1_active:
            score1_text = font_scale(27).render(f"P1 Score: {self.car1_score}", True, DODGERBLUE)
            self.surface.blit(score1_text, (WIDTH - 300, y_offset))
            y_offset += 30
            
        if self.car2_active:
            score2_text = font_scale(27).render(f"P2 Score: {self.car2_score}", True, RED)
            self.surface.blit(score2_text, (WIDTH - 300, y_offset))


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
        
        if self.remaining_time > 0:
            # Title
            title = font_scale(60).render("Level Complete!", True, GREEN)
            self.surface.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))
            
            # Time remaining
            time_text = font_scale(40).render(f"Time Remaining: {self.remaining_time:.1f}", True, WHITE)
            self.surface.blit(time_text, time_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
            
            # Score display for active players
            y_offset = HEIGHT // 2 + 40
            if self.car1_active:
                level_score1 = self.calculate_score(self.car1_finish_time, 
                                                len(self.initial_bonuses) - len(self.time_bonus_group))
                score1_text = font_scale(35).render(f"Player 1 Score: {level_score1}", True, DODGERBLUE)
                self.surface.blit(score1_text, score1_text.get_rect(center=(WIDTH // 2, y_offset)))
                y_offset += 40
                
            if self.car2_active:
                level_score2 = self.calculate_score(self.car2_finish_time, 
                                                len(self.initial_bonuses) - len(self.time_bonus_group))
                score2_text = font_scale(35).render(f"Player 2 Score: {level_score2}", True, RED)
                self.surface.blit(score2_text, score2_text.get_rect(center=(WIDTH // 2, y_offset)))
                y_offset += 40
            
            continue_text = font_scale(30).render("Press SPACE to continue", True, WHITE)
            self.surface.blit(continue_text, continue_text.get_rect(center=(WIDTH // 2, y_offset + 20)))
        else:
            # Time's up message
            title = font_scale(60).render("Time's Up!", True, RED)
            self.surface.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
            
            retry_text = font_scale(40).render("Try to complete the track faster!", True, WHITE)
            self.surface.blit(retry_text, retry_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
            
            space_text = font_scale(30).render("Press SPACE to retry", True, WHITE)
            self.surface.blit(space_text, space_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80)))
            
    def draw_game_complete(self):
        """Updated to show final total scores"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.surface.blit(overlay, (0, 0))
        
        texts = [
            (font_scale(60).render("Game Complete!", True, GREEN), (WIDTH // 2, HEIGHT // 2 - 100))
        ]
        
        if self.car1_active:
            texts.append((font_scale(40).render(f"Player 1 Final Score: {self.car1_score}", True, DODGERBLUE),
                        (WIDTH // 2, HEIGHT // 2)))
        
        if self.car2_active:
            texts.append((font_scale(40).render(f"Player 2 Final Score: {self.car2_score}", True, RED),
                        (WIDTH // 2, HEIGHT // 2 + 50)))
        
        texts.append((font_scale(30).render("Press SPACE to play again", True, WHITE),
                    (WIDTH // 2, HEIGHT // 2 + 120)))
        
        for text, pos in texts:
            rect = text.get_rect(center=pos)
            self.surface.blit(text, rect)
            
    def draw_countdown(self, count):
        # Draw level title
        level_text = font_scale(100).render(self.current_level_data["Level"], True, GOLD)
        level_rect = level_text.get_rect(center=(WIDTH // 2, 75))
        self.surface.blit(level_text, level_rect)

        # Create shadow effect for countdown number
        shadow = font_scale(175, COUNTDOWN_FONT).render(str(count), True, BLACK)
        shadow_surface = pygame.Surface(shadow.get_size(), pygame.SRCALPHA)
        shadow_surface.blit(shadow, (0, 0))
        shadow_surface.set_alpha(200)
        
        # Position and draw shadow and main text
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
        elif self.game_state == "running" and self.remaining_time > 0:
            self.remaining_time -= 1/FPS
            if self.remaining_time <= 0:
                if self.auto_respawn:
                    self.restart_level()
                    self.remaining_time = self.current_level_data["target_time"]
                    self.game_state = "countdown"
                else:
                    self.game_state = "level_complete"
                    self.handle_music(False)
            else:
                self.check_collision()
                self.check_checkpoints()
                self.check_time_bonuses()

    def check_checkpoints(self):
        """Updated checkpoint check to handle None cars"""
        # Check checkpoints for car1 if it exists and is active
        if self.car1_active and self.car1:
            for checkpoint in self.checkpoint_group1.sprites():
                if not checkpoint.passed and checkpoint.index == self.current_checkpoint_index1:
                    if self.car1.collide(checkpoint.mask, checkpoint.rect.x, checkpoint.rect.y):
                        checkpoint.passed = True
                        self.current_checkpoint_index1 += 1
                        if self.sound_enabled:
                            self.checkpoint_sound.play()
                        break

        # Check checkpoints for car2 if it exists and is active
        if self.car2_active and self.car2:
            for checkpoint in self.checkpoint_group2.sprites():
                if not checkpoint.passed and checkpoint.index == self.current_checkpoint_index2:
                    if self.car2.collide(checkpoint.mask, checkpoint.rect.x, checkpoint.rect.y):
                        checkpoint.passed = True
                        self.current_checkpoint_index2 += 1
                        if self.sound_enabled:
                            self.checkpoint_sound.play()
                        break

    def move(self, action1, action2):
        """Updated movement handling for single or two players"""
        if self.game_state != "running":
            return False

        # Handle car 1 movement if active
        if self.car1_active and not self.car1_finished and action1 is not None:
            self._handle_car_movement(self.car1, action1)

        # Handle car 2 movement if active
        if self.car2_active and not self.car2_finished and action2 is not None:
            self._handle_car_movement(self.car2, action2)

        self.check_collision()
        return self.check_finish()

    def _handle_car_movement(self, car, action):
        """Helper method to handle individual car movement"""
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
        """Updated collision check to handle None cars"""
        collision1 = False
        collision2 = False
        
        # Only check collision for car1 if it exists and is active
        if self.car1_active and self.car1:
            collision1 = self.car1.collide(self.track_border_mask)
            if collision1:
                self.car1.handle_border_collision()
                if self.sound_enabled:
                    self.collide_sound.play()
            
        # Only check collision for car2 if it exists and is active
        if self.car2_active and self.car2:
            collision2 = self.car2.collide(self.track_border_mask)
            if collision2:
                self.car2.handle_border_collision()
                if self.sound_enabled:
                    self.collide_sound.play()

        return collision1 or collision2


    def check_finish(self):
        any_finished = False
        
        # Check car1 finish only if it exists and is active
        if self.car1_active and self.car1 and not self.car1_finished:
            car1_finish = self.car1.collide(self.finish_mask, *self.finish_line_position)
            if car1_finish and all(cp.passed for cp in self.checkpoint_group1.sprites()):
                self.car1_finished = True
                self.car1_finish_time = self.remaining_time
                if self.remaining_time > 0:
                    self.car1_score = self.calculate_score(self.remaining_time, 
                                                        len(self.initial_bonuses) - len(self.time_bonus_group))
                if self.sound_enabled:
                    self.win_sound.play()
                any_finished = True

        # Check car2 finish only if it exists and is active
        if self.car2_active and self.car2 and not self.car2_finished:
            car2_finish = self.car2.collide(self.finish_mask, *self.finish_line_position)
            if car2_finish and all(cp.passed for cp in self.checkpoint_group2.sprites()):
                self.car2_finished = True
                self.car2_finish_time = self.remaining_time
                if self.remaining_time > 0:
                    self.car2_score = self.calculate_score(self.remaining_time, 
                                                        len(self.initial_bonuses) - len(self.time_bonus_group))
                if self.sound_enabled:
                    self.win_sound.play()
                any_finished = True

        # Level is complete if all active players have finished or time is up
        all_finished = ((self.car1_active and not self.car2_active and self.car1_finished) or
                    (not self.car1_active and self.car2_active and self.car2_finished) or
                    (self.car1_active and self.car2_active and self.car1_finished and self.car2_finished))

        if all_finished or self.remaining_time <= 0:
            self.handle_music(False)
            self.game_state = "game_complete" if self.current_level >= len(LEVELS) - 1 else "level_complete"
            return True

        return any_finished

    
    def check_time_bonuses(self):
        """Updated time bonus check to handle None cars"""
        for bonus in self.time_bonus_group.sprites():
            # Check car1 bonus collection
            if self.car1_active and self.car1 and self.car1.collide(bonus.mask, bonus.rect.x, bonus.rect.y):
                self.remaining_time += 10.0
                self.car1_score += 10
                if self.sound_enabled:
                    self.time_bonus_sound.play()
                bonus.kill()
                
            # Check car2 bonus collection
            elif self.car2_active and self.car2 and self.car2.collide(bonus.mask, bonus.rect.x, bonus.rect.y):
                self.remaining_time += 2.0
                self.car2_score += 10
                if self.sound_enabled:
                    self.time_bonus_sound.play()
                bonus.kill()
                
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
        # Get the game screen as a PyTorch tensor
        screen = pygame.surfarray.array3d(self.surface)
        # Transpose from (width, height, channel) to (channel, height, width)
        screen = screen.transpose((2, 0, 1))
        # Convert to float and normalize to [0,1]
        screen_tensor = torch.FloatTensor(screen) / 255.0
        
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