import pygame
from Constants import *
from Car import Car
from Obstacle import Obstacle
from drawing import draw_finished, draw_failed, draw_ui, draw_countdown, draw_pause_overlay
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
        
        # Position cars side by side in multiplayer, or centered in single player
        if self.car1_active and self.car2_active:
            # Two cars - offset them slightly
            self.car1 = Car(start_x + 20, start_y, car_color1)
            self.car2 = Car(start_x - 20, start_y, car_color2)
        else:
            # Single car - centered
            if self.car1_active:
                self.car1 = Car(start_x, start_y, car_color1)
            if self.car2_active:
                self.car2 = Car(start_x, start_y, car_color2)

        # Add active cars to sprite group
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
        # Use obstacle generator to create random obstacles
        obstacle_generator = Obstacle(0, 0)
        self.obstacle_group.add(
            obstacle_generator.generate_obstacles(self.num_obstacles) 
        )

    def run_countdown(self):
        if self.game_state == "countdown":
            if not self.ai_train_mode:
                # Play countdown sound and show 3-2-1 countdown
                self.countdown_sound.play()
                for i in range(3, 0, -1):
                    # Draw the track and obstacles during countdown
                    self.surface.fill((0, 0, 0))  
                    self.surface.blits((
                        (self.grass, (0, 0)),
                        (self.track, (0, 0)),
                        (self.finish_line, self.finish_line_position),
                    ))
                    self.obstacle_group.draw(self.surface)
                    self.surface.blit(self.track_border, (0, 0))
                    self.all_sprites.draw(self.surface)
                    
                    # Draw the countdown number
                    draw_countdown(self, i)  
                    pygame.display.update()
                    pygame.time.wait(1000)  

                # Start the game and music
                self.game_state = "running"
                self.handle_music(True)
            else:
                # Skip countdown in AI training mode
                self.game_state = "running"
                
    def draw(self):
        # Don't waste time drawing the background in AI training mode
        if not self.ai_train_mode:
            self.surface.blits((
                (self.grass, (0, 0)),
                (self.track, (0, 0)),
                (self.finish_line, self.finish_line_position),
            ))
        else:
            # Just a black background for AI training
            self.surface.fill((0, 0, 0))

        # Draw the obstacles
        self.obstacle_group.draw(self.surface)
        
        # Draw ray sensors in AI mode
        if self.ai_train_mode:
            if self.car1_active and not self.car1_finished and not self.car1.failed:
                self.car1.draw_rays(self.surface)
            if self.car2_active and not self.car2_finished and not self.car2.failed:
                self.car2.draw_rays(self.surface)
        
        # Draw track borders and cars
        self.surface.blit(self.track_border, (0, 0))
        self.all_sprites.draw(self.surface)

        # Draw appropriate UI based on game state
        if self.game_state == "running":
            draw_ui(self)
        elif self.game_state == "finished":
            draw_finished(self)
        elif self.game_state == "failed":
            draw_failed(self)
        elif self.game_state == "paused":
            draw_pause_overlay(self)

    def restart_game(self):
        # Stop the music
        self.handle_music(False)

        # Reset car positions
        start_x, start_y = CAR_START_POS
        
        # Reset first car
        if self.car1_active:
            x_pos = start_x + 20 if self.car2_active else start_x
            self.car1.reset(x_pos, start_y)
            self.car1_finished = False
            self.car1_time = TARGET_TIME
        
        # Reset second car if active
        if self.car2_active:
            x_pos = start_x - 20 if self.car1_active else start_x
            self.car2.reset(x_pos, start_y)
            self.car2_finished = False
            self.car2_time = TARGET_TIME

        # Reset timer
        self.remaining_time = max(self.car1_time, self.car2_time)

        # Reshuffle obstacle positions
        obstacle_generator = Obstacle(0, 0)
        obstacle_generator.reshuffle_obstacles(self.obstacle_group, self.num_obstacles)

        # Reset game state
        self.state_timer = 0
        self.game_state = "running" if self.ai_train_mode else "countdown"
        
        # Handle music
        if not self.ai_train_mode:
            self.handle_music(False)
            
        # Run countdown for non-AI mode
        self.run_countdown()

    def check_game_end_condition(self):
        # Check if any cars are still racing
        car1_racing = self.car1_active and not self.car1_finished and not self.car1.failed and self.car1_time > 0
        car2_racing = self.car2_active and not self.car2_finished and not self.car2.failed and self.car2_time > 0
        
        if not car1_racing and not car2_racing:
            # Game is over - stop music
            self.handle_music(False)
            
            # Check if any car finished the race
            any_finished = (self.car1_active and self.car1_finished) or (self.car2_active and self.car2_finished)
            
            if any_finished:
                # At least one car finished - show victory screen
                self.game_state = "finished"
                if not self.ai_train_mode and any_finished:
                    self.win_sound.play()
            else:
                # No car finished - show failure screen
                self.game_state = "failed"
                
            # Auto-restart in AI training mode
            if self.ai_train_mode:
                self.restart_game()
                
            return True
                
        return False
        
    def update(self):
        if self.game_state == "countdown":
            self.run_countdown()
        
        elif self.game_state == "running":
            # Update car 1 timer
            if self.car1_active and not self.car1_finished and not self.car1.failed:
                self.car1_time = max(0, self.car1_time - 1/FPS)
                if self.car1_time <= 0:
                    self.car1.can_move = False
            
            # Update car 2 timer
            if self.car2_active and not self.car2_finished and not self.car2.failed:
                self.car2_time = max(0, self.car2_time - 1/FPS)
                if self.car2_time <= 0:
                    self.car2.can_move = False
                    
            # Update overall race timer
            self.remaining_time = max(self.car1_time, self.car2_time)
            
            # Check if the game should end
            self.check_game_end_condition()
            
            # Cast ray sensors in AI mode
            if self.ai_train_mode:
                if self.car1_active and not self.car1_finished and not self.car1.failed:
                    self.car1.cast_rays(self.track_border_mask, self.obstacle_group)
                if self.car2_active and not self.car2_finished and not self.car2.failed:
                    self.car2.cast_rays(self.track_border_mask, self.obstacle_group)
            
            # Check for obstacle collisions
            self.check_obstacle()
        
        # Update all sprites
        self.all_sprites.update()

    def move(self, action1, action2):
        # Don't process movement if game isn't running
        if self.game_state != "running":
            return False
        
        # Process car 1 movement
        if self.car1_active and not self.car1_finished and not self.car1.failed and self.car1_time > 0:
            self._handle_car_movement(self.car1, action1)
            self.check_collision(self.car1)

        # Process car 2 movement
        if self.car2_active and not self.car2_finished and not self.car2.failed and self.car2_time > 0:
            self._handle_car_movement(self.car2, action2)
            self.check_collision(self.car2)

        # Check if any car crossed the finish line
        self.check_finish()
        
        # Return whether the game has ended
        return self.check_game_end_condition()

    def check_obstacle(self): 
        # Loop through all obstacles
        for obstacle in self.obstacle_group.sprites(): 
            # Check car 1 obstacle collision
            if (self.car1_active and not self.car1_finished and not self.car1.failed and 
                self.car1_time > 0 and pygame.sprite.collide_mask(self.car1, obstacle)):
                # Slow down the car
                self.car1.velocity *= 0.25  
                if not self.ai_train_mode:
                    self.obstacle_sound.play()
                # Remove the obstacle
                obstacle.kill()
            
            # Check car 2 obstacle collision
            elif (self.car2_active and not self.car2_finished and not self.car2.failed and 
                  self.car2_time > 0 and pygame.sprite.collide_mask(self.car2, obstacle)):
                # Slow down the car
                self.car2.velocity *= 0.25  
                if not self.ai_train_mode:
                    self.obstacle_sound.play()
                # Remove the obstacle
                obstacle.kill()

    def check_collision(self, car):
        # Skip if car already failed
        if car.failed:  
            return False
            
        # Calculate offsets for mask collision detection
        offset = (int(car.rect.left), int(car.rect.top))
        finish_offset = (int(car.rect.left - self.finish_line_position[0]), 
                        int(car.rect.top - self.finish_line_position[1]))
        
        collision_detected = False
        
        # Check for collision with track border
        if self.track_border_mask.overlap(car.mask, offset):
            car.failed = True
            car.can_move = False 
            if not self.ai_train_mode:
                self.collide_sound.play()
            collision_detected = True
        
        # Check for collision with finish line from behind (wrong direction)
        if overlap := self.finish_mask.overlap(car.mask, finish_offset):
            if overlap[1] <= 2:  # Top edge = wrong way
                car.failed = True
                car.can_move = False 
                if not self.ai_train_mode:
                    self.collide_sound.play()
                collision_detected = True
                
        # Check if game should end
        if collision_detected:
            self.check_game_end_condition()
            
        return collision_detected
    
    def _handle_car_movement(self, car, action):
        # Do nothing if no action
        if action is None:  
            return
        
        # Determine if car is moving
        moving = action in [1, 2, 5, 6, 7, 8]
        
        # Handle rotation
        if action in [3, 5, 7]:  # Left rotation actions
            car.rotate(left=True)
        elif action in [4, 6, 8]:  # Right rotation actions
            car.rotate(right=True)

        # Handle acceleration
        if action in [1, 5, 6]:  # Forward acceleration
            car.accelerate(True)
        elif action in [2, 7, 8]:  # Backward acceleration
            car.accelerate(False)
            
        # Apply friction if not moving
        if not moving:
            car.reduce_speed()
    
    def check_finish(self):
        any_finished = False
        
        # Check if car 1 crossed finish line
        if self.car1_active and not self.car1_finished and not self.car1.failed:
            car1_offset = (int(self.car1.rect.left - self.finish_line_position[0]), 
                           int(self.car1.rect.top - self.finish_line_position[1]))
            
            if finish := self.finish_mask.overlap(self.car1.mask, car1_offset):
                if finish[1] > 2:  # Bottom edge = correct direction
                    self.car1_finished = True
                    if not self.ai_train_mode:
                        self.win_sound.play()
                    any_finished = True

        # Check if car 2 crossed finish line
        if self.car2_active and not self.car2_finished and not self.car2.failed:
            car2_offset = (int(self.car2.rect.left - self.finish_line_position[0]), 
                           int(self.car2.rect.top - self.finish_line_position[1]))
            
            if finish := self.finish_mask.overlap(self.car2.mask, car2_offset):
                if finish[1] > 2:  # Bottom edge = correct direction
                    self.car2_finished = True
                    if not self.ai_train_mode:
                        self.win_sound.play()
                    any_finished = True
                    
        # Check if game should end
        if any_finished:
            self.check_game_end_condition()

        return any_finished
                
    def setup_sound(self):
        # Set volume to 0 in AI training mode
        volume_multiplier = 0 if self.ai_train_mode else 1
        
        # Load and configure sound effects
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
        # Toggle between paused and running states
        if self.game_state == "running":
            self.previous_state = self.game_state
            self.game_state = "paused"
            self.handle_music(False)
        elif self.game_state == "paused":
            self.game_state = self.previous_state
            self.handle_music(True)

    def handle_music(self, play=True):
        # Play or stop background music
        if play and not self.is_music_playing and not self.ai_train_mode:
            self.background_music.play(-1)  # Loop indefinitely
            self.is_music_playing = True
        elif not play and self.is_music_playing:
            self.background_music.stop()
            self.is_music_playing = False

    def state(self):
        # Return None if car 1 is not active
        if not self.car1_active:
            return None
            
        # Cast rays to detect surroundings
        self.car1.cast_rays(self.track_border_mask, self.obstacle_group)
        
        # Normalize ray distances
        normalized_border_rays = [dist / self.car1.ray_length for dist in self.car1.ray_distances_border]
        normalized_obstacle_rays = [dist / self.car1.ray_length for dist in self.car1.ray_distances_obstacles]

        # Construct state vector for AI
        state_list = [
            *normalized_border_rays,              # Distance to borders
            *normalized_obstacle_rays,            # Distance to obstacles
            self.car1.velocity / self.car1.max_velocity,  # Normalized velocity
            math.cos(math.radians(self.car1.angle)),      # Direction x
            math.sin(math.radians(self.car1.angle)),      # Direction y
            self.car1.position.x / WIDTH,                 # Normalized x position
            self.car1.position.y / HEIGHT                 # Normalized y position
        ]
        
        return state_list
    
    def get_state_dim(self):
        """Return the dimension of the state space for DQN agent"""
        # Number of rays used for sensing borders and obstacles
        num_rays = len(self.car1.ray_angles) if self.car1_active else 0
        
        # Total state dimensions: border rays + obstacle rays + velocity + angle (cos,sin) + position (x,y)
        return num_rays * 2 + 1 + 2 + 2

    def get_action_dim(self):
        """Return the dimension of the action space for DQN agent"""
        # Match the saved model which has 8 actions
        return 8

    def get_state_for_player(self, player_num):
        """Return the state for a specific player"""
        if player_num == 1 and self.car1_active:
            # Get state for player 1
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
            # Get state for player 2
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