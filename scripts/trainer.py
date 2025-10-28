import os
import pygame
import sys
import time
import numpy as np
import torch

if torch.cuda.is_available():
    torch.backends.cudnn.benchmark = True

from scripts.AIEnvironment import AIEnvironment
from scripts.Constants import *
from scripts.dqn_agent import DQNAgent
from scripts.TrainingUtils import calculate_reward, save_training_stats, draw_reward_overlay
from scripts.GameManager import game_state_manager

# Constants
STATE_DIM = 16
ACTION_DIM = 8


class Trainer:
    """Training state module that runs inside the main game loop"""
    
    def __init__(self, display, clock):
        self.display = display
        self.clock = clock
        self.environment = None
        self.agent = None
        self.initialized = False
        
        # Training state
        self.steps = 0
        self.episode_reward = 0.0
        self.losses = []
        self.episode_breakdown = {
            'speed': 0.0,
            'edge': 0.0,
            'time': 0.0,
            'obstacle': 0.0,
            'finish': 0.0,
            'collision': 0.0,
            'timeout': 0.0,
            'total': 0.0
        }
        self.state = None
        
        # Timing
        self.start_time = None
        self.fps_counter = 0
        self.fps_timer = None
        self.current_fps = 0
        
        # Episode limits
        self.max_episode_steps = 100000
        
    def initialize(self):
        """Initialize training environment and agent"""
        if self.initialized:
            return
            
        print("\n" + "="*80)
        print("INITIALIZING TRAINING MODE")
        print("="*80)
        
        # Quit mixer for performance
        pygame.mixer.quit()
        
        # Create AI environment
        self.environment = AIEnvironment(self.display)
        
        # Setup agent
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Training on: {device}")
        
        self.agent = DQNAgent(STATE_DIM, ACTION_DIM, device=device)
        
        # Load existing model if available
        if os.path.exists(self.agent.model_path):
            if self.agent.load_model(self.agent.model_path):
                print(f"Resuming training from episode {self.agent.episode_count}")
            else:
                print("Starting fresh training")
        else:
            os.makedirs(self.agent.model_dir, exist_ok=True)
            self.agent.save_model()
            print(f"Created new model at {self.agent.model_path}")
        
        # Initialize timing
        self.start_time = time.time()
        self.fps_timer = time.time()
        
        print("\n" + "="*80)
        print("Epsilon Decay: Step-based")
        print(f"  Start: {self.agent.epsilon:.4f}")
        print(f"  Min: {self.agent.epsilon_min}")
        print(f"  Decay rate: {self.agent.epsilon_decay} per step")
        print(f"  Current episode: {self.agent.episode_count}")
        print("="*80 + "\n")
        print("Training started. Press ESC to return to menu.\n")
        
        # Start first episode
        self._start_new_episode()
        
        self.initialized = True
    
    def _start_new_episode(self):
        """Start a new training episode"""
        self.environment.reset()
        self.steps = 0
        self.episode_reward = 0.0
        self.losses = []
        
        # Reset breakdown
        for key in self.episode_breakdown:
            self.episode_breakdown[key] = 0.0
        
        self.state = self.environment.get_state()
    
    def _end_episode(self):
        """End current episode and save stats"""
        self.agent.end_episode(self.episode_reward)  # Pass reward for tracking
        
        # Determine status
        if self.environment.car_finished:
            status = "FINISH"
        elif self.environment.car_crashed:
            status = "CRASH"
        elif self.environment.car_timeout:
            status = "TIMEOUT"
        else:
            status = "UNKNOWN"
        
        # Save every 10 episodes
        if self.agent.episode_count % 10 == 0:
            self.agent.save_model()
            save_training_stats(
                self.agent.episode_count, 
                self.episode_reward, 
                self.losses, 
                self.agent.epsilon
            )
        
        # Calculate stats
        avg_loss = np.mean(self.losses) if self.losses else 0.0
        
        # Print episode summary
        print(f"Ep {self.agent.episode_count:4d} | {status:7s} | Steps: {self.steps:4d} | "
              f"R: {self.episode_breakdown['total']:7.1f} | "
              f"Spd: {self.episode_breakdown['speed']:+6.1f} | "
              f"Edge: {self.episode_breakdown['edge']:+6.1f} | "
              f"Obst: {self.episode_breakdown['obstacle']:+5.1f} | "
              f"Fin: {self.episode_breakdown['finish']:+6.1f} | "
              f"Col: {self.episode_breakdown['collision']:+6.1f} | "
              f"Tout: {self.episode_breakdown['timeout']:+6.1f} | "
              f"Loss: {avg_loss:.3f} | ε: {self.agent.epsilon:.3f} | "
              f"FPS: {self.current_fps:.0f}")
        
        # Milestone every 100 episodes
        if self.agent.episode_count % 100 == 0:
            elapsed = time.time() - self.start_time
            print("\n" + "="*80)
            print(f"MILESTONE - Episode {self.agent.episode_count}")
            print(f"  Epsilon: {self.agent.epsilon:.4f} → {self.agent.epsilon_min}")
            print(f"  Buffer: {len(self.agent.replay_buffer)}/{self.agent.replay_buffer.capacity}")
            print(f"  Time: {elapsed/60:.1f} minutes")
            print(f"  FPS: {self.current_fps:.0f}")
            print("="*80 + "\n")
        
        # Start next episode
        self._start_new_episode()
    
    def run(self, dt):
        """Main training loop - called every frame"""
        if not self.initialized:
            self.initialize()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._save_and_exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Return to menu
                    print("\n\nReturning to menu...")
                    self.agent.save_model()
                    print(f"Saved at episode {self.agent.episode_count}")
                    game_state_manager.setState('menu')
                    return
        
        # Training step
        if not self.environment.episode_ended and self.steps < self.max_episode_steps:
            # Get action
            action = self.agent.get_action(self.state, training=True)
            
            # Execute step
            next_state, step_info, done = self.environment.step(action)
            
            # Calculate reward
            reward_breakdown = calculate_reward(
                self.environment, 
                collision=step_info['collision'],
                just_finished=step_info['finished'],
                action=action, 
                hit_obstacle=step_info['hit_obstacle'],
                timeout=step_info['timeout'],
                episode=self.agent.episode_count
            )
            
            reward = reward_breakdown['total']
            
            # Accumulate breakdown
            for key in self.episode_breakdown:
                self.episode_breakdown[key] += reward_breakdown.get(key, 0.0)
            
            # Store experience and update
            self.agent.replay_buffer.add(self.state, action, reward, next_state, done)
            
            loss = self.agent.update()
            if loss is not None:
                self.losses.append(loss)
            
            self.steps += 1
            self.episode_reward += reward
            self.state = next_state
            self.fps_counter += 1
            
            # Update FPS counter
            current_time = time.time()
            if current_time - self.fps_timer >= 1.0:
                self.current_fps = self.fps_counter / (current_time - self.fps_timer)
                self.fps_counter = 0
                self.fps_timer = current_time
        else:
            # Episode ended
            self._end_episode()
        
        # Draw environment
        self.environment.draw()
        
        # Draw speed info (top right)
        self._draw_speed_info()
        
        # Draw training overlay
        draw_reward_overlay(self.display, self.episode_breakdown, self.agent.episode_count)
    
    def _draw_speed_info(self):
        """Draw speed percentage at top right (below time)"""
        y_offset = 60  # Below the time display
        
        # Get speed ratio
        speed_ratio = self.environment.car.velocity / self.environment.car.max_velocity
        speed_text = f"Speed: {speed_ratio:.1%}"
        
        # Color based on speed
        if speed_ratio > 0.7:
            speed_color = GREEN
        elif speed_ratio > 0.3:
            speed_color = YELLOW
        else:
            speed_color = RED
        
        # Create shadowed text
        from scripts.TrainingUtils import create_shadowed_text, font_scale
        speed_font = font_scale(28, FONT)
        speed_surface = create_shadowed_text(speed_text, speed_font, speed_color)
        
        # Position at top right
        self.display.blit(
            speed_surface, 
            (WIDTH - speed_surface.get_width() - 20, y_offset)
        )
    
    def _save_and_exit(self):
        """Save model and exit"""
        print("\n\nWindow closed - saving model...")
        if self.agent:
            self.agent.save_model()
            print(f"Saved at episode {self.agent.episode_count}")
            
            elapsed = time.time() - self.start_time
            print("\n" + "="*80)
            print("Training Summary:")
            print(f"  Episodes: {self.agent.episode_count}")
            print(f"  Time: {elapsed/60:.1f} minutes")
            print(f"  Final ε: {self.agent.epsilon:.4f}")
            print(f"  Buffer: {len(self.agent.replay_buffer)}")
            print("="*80)
            print("\nModel saved. Exiting.")
        
        pygame.quit()
        sys.exit(0)