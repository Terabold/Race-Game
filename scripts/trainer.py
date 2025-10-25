"""
Fast headless trainer.

Run: python -m scripts.trainer or python scripts/trainer.py

This trainer runs headless (no display), does not call clock.tick or flip,
and runs episodes as fast as possible. It saves a single model file
(models/model.pt) after every episode and on interrupt.

Notes:
- Requires your Environment to support ai_train_mode=True (skips countdown/drawing).
- Uses SDL dummy video driver to avoid opening a window (so image loading still works).
"""

import os
# Use SDL dummy driver before pygame.init so no window is opened
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import sys
import time
import numpy as np
import torch

# PyTorch perf tweaks
if torch.cuda.is_available():
    torch.backends.cudnn.benchmark = True

from scripts.Environment import Environment
from scripts.Constants import *
from scripts.dqn_agent import DQNAgent
from scripts.TrainingUtils import (
    calculate_reward,
    process_state,
    map_action_to_game_action,
    save_training_stats
)

def start_training():
    # Settings for training run
    settings = {
        'player1': 'DQN',
        'player2': None,
        'car_color1': 'Red',
        'car_color2': None
    }

    # Initialize pygame in dummy mode (no visible window)
    pygame.init()
    # Do not init mixer (audio) — keep headless and silent
    pygame.mixer.quit()

    # Create an off-screen surface (no window)
    surface = pygame.Surface((WIDTH, HEIGHT))

    # Create environment in AI training mode (skips countdown/drawing heavy code)
    environment = Environment(
        surface,
        ai_train_mode=True,
        car_color1=settings['car_color1'],
        car_color2=settings['car_color2']
    )

    # Determine state and action dims
    state_vec = environment.state()
    state_dim = len(state_vec) if state_vec is not None else environment.get_state_dim()
    action_dim = environment.get_action_dim()

    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Training device: {device}")

    # Agent (single-file model)
    agent = DQNAgent(state_dim, action_dim, device=device)

    # Load existing single model if available (models/model.pt)
    if os.path.exists(agent.model_path):
        ok = agent.load_model(agent.model_path)
        if ok:
            print(f"Loaded model from {agent.model_path}")
        else:
            print("Found model file but failed to load. Training from scratch.")
    else:
        # Ensure directory exists and save an initial model so subsequent runs find it
        os.makedirs(agent.model_dir, exist_ok=True)
        agent.save_model()
        print(f"Saved initial model to {agent.model_path}")

    # Training hyperparams (you can tweak these)
    max_episode_steps = 10000        # safety cap per episode
    save_every_n_episodes = 1        # we save every episode
    episode = 0

    # Minimal stats file
    stats_file = "training_stats.csv"

    print("Starting headless fast training. Press Ctrl+C to stop (will save model).")

    while True:
        # Prepare new episode
        environment.restart_game()
        episode += 1
        steps = 0
        episode_reward = 0.0
        losses = []

        # Make sure episode_ended flag reset
        environment.episode_ended = False

        # Warm-start optional: get initial state
        state = process_state(environment)

        # Run the episode as fast as possible
        while environment.game_state == "running":
            # pump events so SDL internals don't block (no window open)
            pygame.event.pump()

            # Get state
            state = process_state(environment)

            # Agent selects action (training=True => epsilon-greedy)
            action_idx = agent.get_action(state, training=True)
            game_action = map_action_to_game_action(action_idx)

            # Step the environment (this updates physics and may auto-restart if ended)
            pre_failed = environment.car1.failed
            done = environment.move(game_action, None)
            post_failed = environment.car1.failed
            collision = (not pre_failed) and post_failed

            # Next state
            next_state = process_state(environment)

            # Reward (small magnitude)
            reward = calculate_reward(environment, prev_state=state, done=done, collision=collision)

            # Store transition
            agent.replay_buffer.add(state, action_idx, reward, next_state,
                                    environment.car1_finished or environment.car1.failed or done)

            # Update agent (single gradient step)
            loss = agent.update()
            if loss is not None:
                losses.append(loss)

            # Stats
            steps += 1
            episode_reward += reward

            # Safety cap to prevent infinite episodes
            if steps >= max_episode_steps:
                # Force environment to end by marking car failed/time out
                # (Environment will set episode_ended and auto-restart)
                environment.car1.can_move = False
                break

        # Episode ended (Environment auto-restarts when ai_train_mode=True)
        # Save model and stats
        agent.save_model()
        save_training_stats(episode, episode_reward, losses, agent.epsilon, filename=stats_file)
        print(f"[Episode {episode}] steps={steps} reward={episode_reward:.4f} eps={agent.epsilon:.4f} losses={len(losses)}")


if __name__ == "__main__":
    start_training()