import torch
import numpy as np
import pygame
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
    def __init__(self, surface, sound_enabled=True, auto_respawn=False, car_color="Red") -> None:
        self.surface = surface
        # Pre-scale grass texture once during initialization
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
        
        # Initialize game elements
        start_pos = LEVELS[0]["car_start_pos"]
        self.car = Car(start_pos[0], start_pos[1], car_color)
        self.checkpoint_group = pygame.sprite.Group()
        self.time_bonus_group = pygame.sprite.Group()
        self.current_checkpoint_index = 0
        self.remaining_time = LEVELS[0]["target_time"]
        
        # Setup sound before loading level
        self.setup_sound()
        self.load_level(self.current_level)
        
    def load_level(self, level_index):
        level_data = LEVELS[level_index]
        self.current_level_data = level_data
        
        # Load and convert track images
        self.track = pygame.image.load(level_data["track_image"]).convert_alpha()
        self.track_border = pygame.image.load(level_data["border_image"]).convert_alpha()
        self.track_border_mask = pygame.mask.from_surface(self.track_border)
        
        # Load and scale finish line
        finish_img = pygame.image.load(FINISHLINE).convert_alpha()
        finishline_width, finishline_height = level_data["finishline_size"]
        self.finish_line = pygame.transform.scale(finish_img, (finishline_width, finishline_height))
        self.finish_line_position = level_data["finishline_pos"]
        self.finish_mask = pygame.mask.from_surface(self.finish_line)
        
        # Reset game state
        self.car.reset(*level_data["car_start_pos"])
        self.remaining_time = level_data["target_time"]
        self.game_state = "countdown"
        
        # Clear and reload checkpoints
        self.checkpoint_group.empty()
        self.current_checkpoint_index = 0
        
        for i, checkpoint_data in enumerate(level_data.get("checkpoints", [])):
            self.checkpoint_group.add(Checkpoint(
                checkpoint_data["pos"],
                checkpoint_data["size"],
                i
            ))

        # Reset and generate time bonuses
        self.time_bonus_group.empty()
        track_name = f"track{level_index + 1}"
        time_bonus_generator = TimeBonus(0, 0)
        self.time_bonus_group.add(time_bonus_generator.generate_bonuses(track_name, num_bonuses=10))

    def get_closest_active_checkpoint(self):
        active_checkpoints = [
            cp for cp in self.checkpoint_group.sprites() 
            if not cp.passed and cp.index >= self.current_checkpoint_index
        ]
        if not active_checkpoints:
            return None
            
        return min(active_checkpoints, 
                  key=lambda cp: (cp.index != self.current_checkpoint_index,
                                cp.get_distance_to(self.car.x, self.car.y)))
    
    def check_checkpoints(self):
        closest_checkpoint = self.get_closest_active_checkpoint()
        if closest_checkpoint and self.car.collide(closest_checkpoint.mask, *closest_checkpoint.pos):
            closest_checkpoint.passed = True
            self.current_checkpoint_index = closest_checkpoint.index + 1
            self.checkpoint_sound.play()

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
        # Draw base game elements efficiently using blits
        self.surface.blits((
            (self.grass, (0, 0)),
            (self.track, (0, 0)),
            (self.finish_line, self.finish_line_position),
        ))

        # Draw only the closest active checkpoint for efficiency
        closest_checkpoint = self.get_closest_active_checkpoint()
        if closest_checkpoint:
            self.surface.blit(closest_checkpoint.image, closest_checkpoint.rect)

        # Draw time bonuses before border for proper layering
        self.time_bonus_group.draw(self.surface)
        self.surface.blit(self.track_border, (0, 0))
        
        # Draw car and UI
        blit_rotate_center(self.surface, self.car.image, (self.car.x, self.car.y), self.car.angle)
        
        # Draw appropriate UI based on game state
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
        # Render timer with conditional color
        timer_color = RED if self.remaining_time < 1 else GREEN
        timer_text = font_scale(27).render(
            f"Time Remaining: {self.remaining_time:.1f}", True, timer_color)
        
        # Render bonus counter with conditional color
        bonus_color = YELLOW if self.remaining_time == 1 else GREEN
        bonus_text = font_scale(36).render(
            f"Active Bonuses: {len(self.time_bonus_group)}", True, bonus_color)
        
        # Draw UI elements
        self.surface.blits((
            (timer_text, (10, 5)),
            (bonus_text, (10, 40))
        ))

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
        
        texts = []
        if self.remaining_time > 0:
            texts = [
                (font_scale(60).render("Level Complete!", True, GREEN), (WIDTH // 2, HEIGHT // 2 - 50)),
                (font_scale(40).render(f"Time Remaining: {self.remaining_time:.1f}", True, WHITE),
                 (WIDTH // 2, HEIGHT // 2 + 20)),
                (font_scale(30).render("Press SPACE to continue", True, WHITE),
                 (WIDTH // 2, HEIGHT // 2 + 80))
            ]
        else:
            texts = [
                (font_scale(60).render("Time's Up!", True, RED), (WIDTH // 2, HEIGHT // 2 - 50)),
                (font_scale(40).render("Try to complete the track faster!", True, WHITE),
                 (WIDTH // 2, HEIGHT // 2 + 20)),
                (font_scale(30).render("Press SPACE to retry", True, WHITE),
                 (WIDTH // 2, HEIGHT // 2 + 80))
            ]
        
        for text, pos in texts:
            rect = text.get_rect(center=pos)
            self.surface.blit(text, rect)

    def draw_game_complete(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.surface.blit(overlay, (0, 0))
        
        texts = [
            (font_scale(80).render("Congratulations!", True, GOLD),
             (WIDTH // 2, HEIGHT // 2 - 60)),
            (font_scale(40).render("You've completed all levels", True, WHITE),
             (WIDTH // 2, HEIGHT // 2 + 20)),
            (font_scale(40).render(f"You beat this level with {self.remaining_time:.1f} seconds remaining!", True, WHITE),
             (WIDTH // 2, HEIGHT // 2 + 80)),
            (font_scale(30).render("Press SPACE to play all levels again", True, WHITE),
             (WIDTH // 2, HEIGHT // 2 + 140))
        ]
        
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

    def move(self, action):
        if self.game_state != "running":
            return False

        # Handle movement based on action
        moving = action in [1, 2, 5, 6, 7, 8]
        if action in [1, 5, 6]:
            self.car.accelerate(True)
        elif action in [2, 7, 8]:
            self.car.accelerate(False)
        
        if action in [3, 5, 7]:
            self.car.rotate(left=True)
        elif action in [4, 6, 8]:
            self.car.rotate(right=True)

        if not moving:
            self.car.reduce_speed()

        self.check_collision()
        return self.check_finish()

    def check_collision(self):
        if self.car.collide(self.track_border_mask):
            self.car.handle_border_collision()
            self.collide_sound.play()
            return True
        return False

    def check_finish(self):
        finish_pos = self.car.collide(self.finish_mask, *self.finish_line_position)
        if not finish_pos:
            return False
            
        if finish_pos[1] == 0:
            self.car.handle_border_collision()
            return False
            
        if all(cp.passed for cp in self.checkpoint_group.sprites()):
            self.win_sound.play()
            self.handle_music(False)
            self.game_state = "game_complete" if self.current_level >= len(LEVELS) - 1 else "level_complete"
            return True
            
        self.car.handle_border_collision()
        return False
    
    def check_time_bonuses(self):
        for bonus in self.time_bonus_group.sprites():
            if self.car.collide(bonus.mask, bonus.rect.x, bonus.rect.y):
                self.remaining_time += 2.0  # Add 2 seconds
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