# trainer.py - SIMPLIFIED CLEAN VERSION
import os
import pygame
import sys
import time
import numpy as np
import torch
import wandb
from collections import deque

from scripts.AIEnvironment import AIEnvironment
from scripts.Constants import *
from scripts.dqn_agent import DQNAgent
from scripts.GameManager import game_state_manager

STATE_DIM = 14  # 11 rays + 1 velocity + 2 orientation
ACTION_DIM = 6  # 6 actions (no backward)


def calculate_reward(environment, step_info):
    """Simple reward calculation"""
    reward = 0.0
    
    # 1. Speed reward (encourage moving fast)
    speed_ratio = abs(environment.car.velocity) / environment.car.max_velocity
    if speed_ratio >= 0.8:
        reward += 1.5
    elif speed_ratio >= 0.5:
        reward += 0.5
    else:
        reward -= 0.5
    
    # 2. Edge penalty (stay away from walls)
    if environment.car.ray_distances:
        min_ray = min(environment.car.ray_distances) / environment.car.ray_length
        if min_ray < 0.1:
            reward -= 2.0
        elif min_ray < 0.2:
            reward -= 0.5
    
    # 3. Checkpoint crossed (big reward!)
    if step_info.get("checkpoint_crossed", False):
        reward += 50.0
    
    # 4. Backward crossing (bad!)
    if step_info.get("backward_crossed", False):
        reward -= 30.0
    
    # 5. Hit obstacle
    if step_info.get("hit_obstacle", False):
        reward -= 10.0
    
    # 6. Finished race (huge reward!)
    if step_info.get("finished", False):
        reward += 500.0
        # Time bonus
        time_ratio = environment.time_remaining / environment.max_time
        reward += time_ratio * 200.0
    
    # 7. Crashed (big penalty)
    if step_info.get("collision", False):
        reward -= 200.0
    
    # 8. Timeout
    if step_info.get("timeout", False):
        reward -= 100.0
    
    return float(reward)


class Trainer:
    def __init__(self, display, clock, run_number=1):
        self.display = display
        self.clock = clock
        self.run_number = run_number
        
        # Game components
        self.environment = None
        self.agent = None
        
        # Episode tracking
        self.episode = 0
        self.steps = 0
        self.episode_reward = 0.0
        self.state = None
        
        # Stats (last 100 episodes)
        self.rewards_100 = deque(maxlen=100)
        self.checkpoints_100 = deque(maxlen=100)
        self.finishes_100 = deque(maxlen=100)
        
        # Best tracking
        self.best_finish_time = 0.0
        self.best_finish_episode = 0
        
        # Visualization
        self.show_viz = False
        
        # WandB
        self.wandb_run = None
        
        print("\n" + "="*60)
        print("TRAINING MODE")
        print("V = Toggle visualization | ESC = Return to menu")
        print("="*60)
    
    def initialize(self):
        """Setup everything"""
        # Disable audio
        pygame.mixer.quit()
        
        # Create environment
        self.environment = AIEnvironment(self.display)
        
        # Create agent
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.agent = DQNAgent(STATE_DIM, ACTION_DIM, device=device)
        
        # Load checkpoint if exists
        if os.path.exists(self.agent.model_path):
            self.agent.load_model()
            self.episode = self.agent.episode_count
            self.best_finish_time = self.agent.best_finish_time
            self.best_finish_episode = self.agent.best_finish_episode
            print(f"✓ Loaded checkpoint - Episode {self.episode}")
            print(f"  Best: {25.0 - self.best_finish_time:.2f}s (Ep {self.best_finish_episode})")
        else:
            print("Starting fresh training")
        
        # Initialize WandB
        self._init_wandb()
        
        # Start first episode
        self._reset_episode()
    
    def _init_wandb(self):
        """Initialize WandB tracking"""
        config = {
            "name": f"Racing_DQN_{self.run_number}",
            "state_dim": STATE_DIM,
            "action_dim": ACTION_DIM,
            "architecture": "256->128->64->action_dim",
            "gamma": self.agent.gamma,
            "learning_rate": self.agent.lr,
            "batch_size": self.agent.batch_size,
            "epsilon_decay": self.agent.epsilon_decay,
            "epsilon_min": self.agent.epsilon_min,
            "target_update": self.agent.target_update,
            "device": str(self.agent.device)
        }
        
        self.wandb_run = wandb.init(
            project="Racing-DQN-Training",
            name=f"Run_{self.run_number}",
            config=config,
            resume="allow"
        )
        print(f"✓ WandB initialized: {wandb.run.get_url()}")
    
    def _reset_episode(self):
        """Start new episode"""
        self.environment.reset()
        self.steps = 0
        self.episode_reward = 0.0
        self.state = self.environment.get_state()
    
    def _end_episode(self):
        """Finish episode and log stats"""
        cp_count = self.environment.checkpoint_manager.crossed_count
        finished = self.environment.car_finished
        time_left = self.environment.time_remaining if finished else 0.0
        
        # Update agent
        self.agent.end_episode(self.episode_reward, cp_count, time_left, finished)
        self.episode = self.agent.episode_count
        
        # Update stats
        self.rewards_100.append(self.episode_reward)
        self.checkpoints_100.append(cp_count)
        self.finishes_100.append(finished)
        
        # Track best
        if finished and time_left > self.best_finish_time:
            self.best_finish_time = time_left
            self.best_finish_episode = self.episode
        
        # Log to WandB
        log_dict = {
            "episode": self.episode,
            "reward": self.episode_reward,
            "checkpoints": cp_count,
            "finished": int(finished),
            "epsilon": self.agent.epsilon,
        }
        
        if finished:
            log_dict["finish_time"] = 25.0 - time_left
        
        # Rolling averages (if we have data)
        if len(self.rewards_100) >= 10:
            log_dict["avg_reward_100"] = float(np.mean(self.rewards_100))
            log_dict["avg_checkpoints_100"] = float(np.mean(self.checkpoints_100))
            log_dict["win_rate_100"] = sum(self.finishes_100)
        
        wandb.log(log_dict)
        
        # Print status
        status = "✓ FINISH" if finished else ("💥 CRASH" if self.environment.car_crashed else "⏱️ TIMEOUT")
        print(f"Ep {self.episode:4d} | {status:10s} | CP: {cp_count:2d}/16 | R: {self.episode_reward:7.1f} | ε: {self.agent.epsilon:.3f}")
        
        # Save periodically
        if self.episode % 50 == 0:
            self.agent.save_model()
            print(f"  💾 Saved checkpoint")
        
        # Milestone every 100 episodes
        if self.episode % 100 == 0:
            self._print_milestone()
        
        # Reset for next episode
        self._reset_episode()
    
    def _print_milestone(self):
        """Print 100-episode summary"""
        avg_reward = float(np.mean(self.rewards_100))
        avg_cp = float(np.mean(self.checkpoints_100))
        wins = sum(self.finishes_100)
        
        print("\n" + "="*60)
        print(f"MILESTONE - Episode {self.episode}")
        print(f"  Avg Reward: {avg_reward:.1f}")
        print(f"  Win Rate: {wins}/100")
        print(f"  Avg Checkpoints: {avg_cp:.1f}/16 ({avg_cp/16*100:.1f}%)")
        if self.best_finish_time > 0:
            print(f"  Best Time: {25.0 - self.best_finish_time:.2f}s (Ep {self.best_finish_episode})")
        print("="*60 + "\n")
    
    def run(self, dt):
        """Main training loop"""
        if not self.environment:
            self.initialize()
        
        # Handle input (check every frame for V key)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_v]:
            # Toggle only if not already pressed (debounce)
            if not hasattr(self, '_v_pressed') or not self._v_pressed:
                self.show_viz = not self.show_viz
                print(f"Visualization: {'ON' if self.show_viz else 'OFF'}")
                self._v_pressed = True
        else:
            self._v_pressed = False
        
        # Handle other events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._save_and_exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._return_to_menu()
        
        # Training step
        if not self.environment.episode_ended:
            # Get action
            action = self.agent.get_action(self.state, training=True)
            
            # Execute step
            next_state, step_info, done = self.environment.step(action)
            
            # Calculate reward
            reward = calculate_reward(self.environment, step_info)
            
            # Store experience
            self.agent.store_experience(self.state, action, reward, next_state, done)
            
            # Update network
            self.agent.update()
            
            # Update state
            self.steps += 1
            self.episode_reward += reward
            self.state = next_state
        else:
            # Episode ended
            self._end_episode()
        
        # Draw
        if self.show_viz:
            self.environment.draw()
            self._draw_overlay()
        else:
            self.display.fill((0, 0, 0))
            font = pygame.font.Font(None, 28)
            
            text1 = font.render(f"Training Episode {self.episode}", True, (255, 255, 255))
            self.display.blit(text1, (10, 10))
            
            text2 = font.render(f"Press V for visualization, ESC to quit", True, (200, 200, 200))
            self.display.blit(text2, (10, 45))
            
            if self.best_finish_time > 0:
                text3 = font.render(f"Best: {25.0 - self.best_finish_time:.2f}s (Ep {self.best_finish_episode})", True, (100, 255, 100))
                self.display.blit(text3, (10, 80))
        
        pygame.display.update()
    
    def _draw_overlay(self):
        """Draw training info overlay"""
        panel = pygame.Surface((250, 200), pygame.SRCALPHA)
        panel.fill((20, 20, 30, 230))
        pygame.draw.rect(panel, (80, 80, 100), (0, 0, 250, 200), 2)
        
        font = pygame.font.SysFont('Arial', 16)
        y = 10
        
        # Episode info
        lines = [
            f"Episode: {self.episode}",
            f"Reward: {self.episode_reward:.1f}",
            f"Epsilon: {self.agent.epsilon:.3f}",
            f"Checkpoints: {self.environment.checkpoint_manager.crossed_count}/16",
            "",
        ]
        
        if self.best_finish_time > 0:
            lines.append(f"Best: {25.0 - self.best_finish_time:.2f}s")
        
        for line in lines:
            text = font.render(line, True, (255, 255, 255))
            panel.blit(text, (10, y))
            y += 25
        
        self.display.blit(panel, (self.display.get_width() - 260, 10))
    
    def _return_to_menu(self):
        """Save and return to menu"""
        print("\nSaving and returning to menu...")
        self.agent.save_model()
        wandb.finish()
        game_state_manager.setState('main_menu')
    
    def _save_and_exit(self):
        """Save and quit"""
        print("\nSaving model...")
        self.agent.save_model()
        print(f"Trained for {self.episode} episodes")
        if self.best_finish_time > 0:
            print(f"Best: {25.0 - self.best_finish_time:.2f}s (Ep {self.best_finish_episode})")
        wandb.finish()
        pygame.quit()
        sys.exit(0)