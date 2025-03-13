import pygame
import sys
import os
import numpy as np
import torch
from Environment import Environment
from Constants import *
from dqn_agent import DQNAgent
from TrainingUtils import (
    calculate_reward,
    process_state,
    map_action_to_game_action,
    save_training_stats,
    draw_training_info
)

def start_training():
    # Game settings
    settings = {
        'player1': 'DQN',
        'player2': None,
        'car_color1': 'Red',
        'car_color2': None
    }
    
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Racing Game - DQN Training")
    clock = pygame.time.Clock()
    
    # Create environment
    environment = Environment(
        surface,
        ai_train_mode=True,
        car_color1=settings['car_color1'],
        car_color2=settings['car_color2']
    )
    
    # Initialize training components
    state_dim = len(environment.state())  # Size of state representation
    action_dim = 8 # 0 nothing 1 accelerate 2 brake 3 turn left 4 turn right 5 accelerate + turn left 6 accelerate + turn right 7 backward + turn left 8 backward + turn right
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    agent = DQNAgent(state_dim, action_dim, device=device)
    agent.gamma = 0.99  # Same as DDQN
    agent.lr = 0.0005   # Similar to DDQN
    agent.batch_size = 64  # Same as DDQN
    agent.epsilon = 1.0  # Start with more exploration
    agent.epsilon_min = 0.02  # End with slightly more exploration than before
    agent.epsilon_decay = 0.999  # Slower decay to explore more
    agent.target_update = 10  # Update target network every 10 steps (same as REPLACE_TARGET in DDQN)
    
    # Training parameters
    max_episodes = 10000  # More episodes like in DDQN
    save_interval = 100   # Save less frequently
    training_info = {
        'episode': 0,
        'steps': 0,
        'episode_reward': 0,
        'loss': None,
        'epsilon': agent.epsilon
    }
    # Run training loop
    train_loop(environment, agent, max_episodes, save_interval, training_info, clock)
    
    pygame.quit()

def train_loop(environment, agent, max_episodes, save_interval, training_info, clock):
    running = True
    training_stats = []
    episode_losses = []
    
    # Track inactivity for early termination
    counter = 0
    
    # Main training loop
    while running and training_info['episode'] < max_episodes:
        # clock.tick(FPS)
        
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Check if we need to start a new episode
        if environment.game_state != "running":
            if training_info['episode'] > 0:
                # Save training stats
                save_training_stats(
                    training_info['episode'],
                    training_info['episode_reward'],
                    episode_losses,
                    agent.epsilon
                )
                
                # Save model periodically
                if training_info['episode'] % save_interval == 0:
                    agent.save_model(training_info['episode'])
            
            # Reset for new episode
            environment.restart_game()
            training_info['episode'] += 1
            training_info['steps'] = 0
            training_info['episode_reward'] = 0
            episode_losses = []
            prev_state = None
            counter = 0
            
            # Get initial state
            state = process_state(environment)
        
        # Training step
        elif environment.game_state == "running":
            # Get current state
            state = process_state(environment)
            
            # Select action
            action_idx = agent.get_action(state)
            
            # Convert to game action (different mapping for reduced action space)
            if action_idx == 0:
                game_action = 0  # Do nothing
            elif action_idx == 1:
                game_action = 1  # Accelerate
            elif action_idx == 2:
                game_action = 2  # Brake
            elif action_idx == 3:
                game_action = 3  # Turn left
            elif action_idx == 4:
                game_action = 4  # Turn right
            
            # Take action in environment
            pre_collision = environment.car1.failed
            game_over = environment.move(game_action, None)
            post_collision = environment.car1.failed
            collision = not pre_collision and post_collision
            
            # Get new state
            next_state = process_state(environment)
            
            # Calculate reward
            reward = calculate_reward(environment, prev_state=state, 
                                     done=game_over, collision=collision)
            
            # Check for inactivity (similar to DDQN)
            if reward == 0:
                counter += 1
                if counter > 100:  # End episode if stuck
                    game_over = True
            else:
                counter = 0
            
            # Store experience in replay buffer
            agent.replay_buffer.add(state, action_idx, reward, next_state, 
                                   environment.car1_finished or environment.car1.failed or game_over)
            
            # Update agent
            loss = agent.update()
            if loss is not None:
                episode_losses.append(loss)
                training_info['loss'] = loss
            
            # Update tracking info
            training_info['steps'] += 1
            training_info['episode_reward'] += reward
            training_info['epsilon'] = agent.epsilon
            prev_state = state
            
            # End episode if maximum steps reached (similar to TOTAL_GAMETIME in DDQN)
            if training_info['steps'] >= 10000:
                game_over = True
        
        # Update environment and draw
        environment.update()
        environment.draw()
        
        # Draw training information
        draw_training_info(
            environment.surface,
            training_info['episode'],
            training_info['steps'],
            training_info['episode_reward'],
            training_info['epsilon'],
            training_info['loss']
        )
        
        pygame.display.update()
    
    # Final save
    agent.save_model(training_info['episode'])
    print(f"Training completed after {training_info['episode']} episodes")

if __name__ == "__main__":
    start_training()