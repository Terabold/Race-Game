# trainer.py - OPTIMIZED
import os
import pygame
import sys
import time
import numpy as np
import torch

if torch.cuda.is_available():
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False  # Faster but less deterministic

from scripts.AIEnvironment import AIEnvironment
from scripts.Constants import *
from scripts.dqn_agent import DQNAgent
from scripts.TrainingUtils import calculate_reward, save_training_stats, draw_reward_overlay
from scripts.GameManager import game_state_manager

# Constants
STATE_DIM = 20  # 17 rays + 1 velocity + 2 orientation (sin/cos)
ACTION_DIM = 8


class Trainer:
    """OPTIMIZED training module with better performance"""
    
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
            'speed': 0.0, 'edge': 0.0, 'checkpoint': 0.0,
            'finish': 0.0, 'fast_finish': 0.0, 'collision': 0.0,
            'timeout': 0.0, 'obstacle': 0.0, 'backward': 0.0, 'total': 0.0
        }
        self.state = None
        
        # Timing
        self.start_time = None
        self.fps_counter = 0
        self.fps_timer = None
        self.current_fps = 0
        
        # Episode limits
        self.max_episode_steps = 150000
        
        # Statistics (using deque for efficiency)
        from collections import deque
        self.last_100_rewards = deque(maxlen=100)
        self.last_100_checkpoints = deque(maxlen=100)
        self.last_100_finishes = deque(maxlen=100)
        
        # Visualization toggle (for speed)
        self.show_visualization = False  # Set to True to see training
        
    def initialize(self):
        """Initialize training environment and agent"""
        if self.initialized:
            return
            
        print("\n" + "="*80)
        print("INITIALIZING OPTIMIZED TRAINING MODE")
        print("="*80)
        
        # Disable mixer for performance
        pygame.mixer.quit()
        
        # Create AI environment
        self.environment = AIEnvironment(self.display)
        
        # Setup agent with CUDA if available
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Training device: {device}")
        
        if device.type == 'cuda':
            print(f"GPU: {torch.cuda.get_device_name(0)}")
        
        self.agent = DQNAgent(STATE_DIM, ACTION_DIM, device=device)
        
        # Load existing model if available
        if os.path.exists(self.agent.model_path):
            if self.agent.load_model(self.agent.model_path):
                print(f"Resuming from episode {self.agent.episode_count}")
        else:
            os.makedirs(self.agent.model_dir, exist_ok=True)
            self.agent.save_model()
            print(f"Created new model")
        
        # Initialize timing
        self.start_time = time.time()
        self.fps_timer = time.time()
        
        print("\nOPTIMIZATIONS ENABLED:")
        print("  ✓ Spatial filtering for obstacles")
        print("  ✓ Optimized ray casting (step=15)")
        print("  ✓ Checkpoint checks limited to current+previous")
        print("  ✓ Fixed speed reward calculation")
        print("  ✓ Batch rendering disabled for speed")
        print("  ✓ CUDA/cuDNN optimizations enabled")
        
        print("\nSTATE SPACE (20 dims):")
        print("  - 17 ray sensors (normalized)")
        print("  - 1 velocity (normalized)")
        print("  - 2 orientation (sin/cos of angle)")
        
        print("\nREWARD STRUCTURE (FIXED):")
        print("  Speed: 0.0 to +2.0 (exponential)")
        print("  Checkpoint: +15.0 per crossing")
        print("  Finish: +300.0 (+10-100 time bonus)")
        print("  Collision: -150.0")
        print("  Timeout: -300.0")
        print("  Backward: -30.0")
        print("="*80 + "\n")
        
        print(f"Episode: {self.agent.episode_count}")
        print(f"Best checkpoints: {self.agent.best_checkpoints:.1f}/16")
        print("Press ESC to return to menu.\n")
        
        # Start first episode
        self._start_new_episode()
        self.initialized = True
    
    def _start_new_episode(self):
        """Start a new training episode"""
        self.environment.reset()
        self.steps = 0
        self.episode_reward = 0.0
        self.losses.clear()
        
        # Reset breakdown
        for key in self.episode_breakdown:
            self.episode_breakdown[key] = 0.0
        
        self.state = self.environment.get_state()
    
    def _end_episode(self):
        """End episode and update stats"""
        checkpoints_crossed = self.environment.checkpoint_manager.crossed_count
        
        # Update agent
        self.agent.end_episode(self.episode_reward, checkpoints_crossed)
        
        # Calculate stats
        avg_loss = float(np.mean(self.losses)) if self.losses else 0.0
        finished = self.environment.car_finished
        
        # Track performance
        self.last_100_rewards.append(self.episode_reward)
        self.last_100_checkpoints.append(checkpoints_crossed)
        self.last_100_finishes.append(finished)
        
        # Determine status
        if self.environment.car_finished:
            status = "🏁 FINISH"
        elif self.environment.car_crashed:
            status = "💥 CRASH"
        elif self.environment.car_timeout:
            status = "⏱️  TIMEOUT"
        else:
            status = "UNKNOWN"
        
        # Console output
        print(f"Ep {self.agent.episode_count:4d} | {status:12s} | "
              f"Steps: {self.steps:5d} | CP: {checkpoints_crossed:2d}/16 | "
              f"R: {self.episode_breakdown['total']:8.1f} | "
              f"Speed: {self.episode_breakdown['speed']:+6.1f} | "
              f"Loss: {avg_loss:.4f} | ε: {self.agent.epsilon:.4f} | "
              f"FPS: {self.current_fps:.0f}")
        
        # Periodic saves
        if self.agent.episode_count % 50 == 0:
            self.agent.save_model()
            
            # Calculate 100-episode stats
            avg_reward_100 = float(np.mean(self.last_100_rewards))
            avg_checkpoints_100 = float(np.mean(self.last_100_checkpoints))
            win_rate_100 = sum(self.last_100_finishes)
            
            save_training_stats(
                self.agent.episode_count, 
                avg_reward_100,
                self.losses, 
                self.agent.epsilon,
                win_count=win_rate_100,
                avg_checkpoints=avg_checkpoints_100,
                total_checkpoints=16
            )
            
            # Milestone output
            elapsed = time.time() - self.start_time
            print("\n" + "="*80)
            print(f"MILESTONE - Episode {self.agent.episode_count}")
            print(f"  Time: {elapsed/60:.1f} min ({elapsed/3600:.2f} hrs)")
            print(f"  Avg Reward (100): {avg_reward_100:.1f}")
            print(f"  Win Rate (100): {win_rate_100}/100 ({win_rate_100}%)")
            print(f"  Avg CP (100): {avg_checkpoints_100:.1f}/16 ({avg_checkpoints_100/16*100:.1f}%)")
            print(f"  Best CP Ever: {self.agent.best_checkpoints:.1f}/16")
            print(f"  Training FPS: {self.current_fps:.0f}")
            print(f"  Epsilon: {self.agent.epsilon:.4f}")
            print(f"  Learning Rate: {self.agent.optimizer.param_groups[0]['lr']:.6f}")
            print("="*80 + "\n")
        
        # Start next episode
        self._start_new_episode()
    
    def run(self, dt):
        """OPTIMIZED main training loop"""
        if not self.initialized:
            self.initialize()
        
        # Handle events (minimal processing)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._save_and_exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._return_to_menu()
                elif event.key == pygame.K_v:
                    # Toggle visualization
                    self.show_visualization = not self.show_visualization
                    print(f"Visualization: {'ON' if self.show_visualization else 'OFF'}")
        
        # Training step
        if not self.environment.episode_ended and self.steps < self.max_episode_steps:
            # Get action
            action = self.agent.get_action(self.state, training=True)
            
            # Execute step
            next_state, step_info, done = self.environment.step(action)
            
            # Calculate reward
            reward, reward_breakdown = calculate_reward(
                environment=self.environment,
                action=action,
                step_info=step_info,
                prev_state=self.state
            )
            
            # Accumulate breakdown
            for key, value in reward_breakdown.items():
                self.episode_breakdown[key] += value
            
            # Store experience
            self.agent.replay_buffer.add(self.state, action, reward, next_state, done)
            
            # Update network
            loss = self.agent.update()
            if loss is not None:
                self.losses.append(loss)
            
            # Update state
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
        
        # Optional visualization (slows training)
        if self.show_visualization:
            self.environment.draw()
            draw_reward_overlay(self.display, self.episode_breakdown, self.agent.episode_count)
    
    def _return_to_menu(self):
        """Return to menu"""
        print("\nReturning to menu...")
        self.agent.save_model()
        print("Model saved")
        game_state_manager.setState('menu')
    
    def _save_and_exit(self):
        """Save and exit"""
        print("\nSaving model...")
        if self.agent:
            self.agent.save_model()
            print("Model saved")
            
            elapsed = time.time() - self.start_time
            print("\n" + "="*80)
            print("TRAINING SUMMARY:")
            print(f"  Episodes: {self.agent.episode_count}")
            print(f"  Duration: {elapsed/60:.1f} min ({elapsed/3600:.2f} hrs)")
            print(f"  Best CP: {self.agent.best_checkpoints:.1f}/16")
            print("="*80)
        
        pygame.quit()
        sys.exit(0)