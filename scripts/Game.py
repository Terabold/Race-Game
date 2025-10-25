import pygame
import sys
from scripts.Environment import Environment
from scripts.Human_Agent import HumanAgentWASD, HumanAgentArrows
from scripts.Constants import *
from scripts.dqn_agent import DQNAgent
from scripts.GameManager import game_state_manager
from scripts.TrainingUtils import calculate_reward, process_state, map_action_to_game_action
import os

class Game:
    def __init__(self, display, clock):
        self.display = display
        self.clock = clock
        self.environment = None
        self.player1 = None
        self.player2 = None
        # track previous env state for end-of-episode saves (kept for safety)
        self._prev_env_state = None

    def initialize_environment(self, settings=None):
        """Initialize environment with settings and training flag from game_state_manager"""
        if settings is None:
            settings = {
                'player1': game_state_manager.player1_selection,
                'player2': game_state_manager.player2_selection,
                'car_color1': game_state_manager.player1_car_color,
                'car_color2': game_state_manager.player2_car_color
            }

        # Pass ai_train_mode based on the global game_state_manager.training_mode flag
        self.environment = Environment(
            self.display,
            ai_train_mode=game_state_manager.training_mode,
            car_color1=settings['car_color1'] if settings.get('player1') else None,
            car_color2=settings['car_color2'] if settings.get('player2') else None
        )

        # Setup players (DQN / Human). If training_mode True, agents will be created to train inline.
        self._setup_players(settings)
        # initialize previous env state for episode tracking
        self._prev_env_state = self.environment.game_state

    def _setup_players(self, settings):
        """Setup player agents"""
        # Player 1
        player1_type = settings.get('player1')
        if player1_type == "Human":
            self.player1 = HumanAgentWASD()
            print(f"Player 1: Human (WASD) with {settings['car_color1']} car")
        elif player1_type == "DQN":
            state_dim = self.environment.get_state_dim()
            action_dim = self.environment.get_action_dim()
            # Create agent with same device handling as the trainer
            self.player1 = DQNAgent(state_dim, action_dim)
            # Ensure single-file workflow: load existing model or save an initial model
            if os.path.exists(self.player1.model_path):
                ok = self.player1.load_model(self.player1.model_path)
                if ok:
                    # load_model prints diagnostics; repeat here for clarity
                    print(f"Player 1: DQN AI loaded from {self.player1.model_path} with {settings['car_color1']} car")
                else:
                    print("Failed to load model; starting with fresh model.")
            else:
                # Save initial untrained model so subsequent runs always have a model file
                self.player1.save_model()
                print(f"Saved initial model to {self.player1.model_path}")
            # If we are starting a normal game (not training), force inference mode
            if not game_state_manager.training_mode:
                try:
                    self.player1.set_inference_mode()
                    print("Player 1: set to inference (greedy) mode.")
                except Exception:
                    # fall back to manual adjustments (only here because set_inference_mode is simple)
                    self.player1.epsilon = 0.0
                    self.player1.policy_net.eval()
                    self.player1.target_net.eval()
                    print("Player 1: set to inference (greedy) mode (fallback).")
            if game_state_manager.training_mode:
                print(f"Player 1: DQN (training mode) with {settings['car_color1']} car")
            else:
                print(f"Player 1: DQN (inference) with {settings['car_color1']} car")
        else:
            self.player1 = None

        # Player 2
        player2_type = settings.get('player2')
        if player2_type == "Human":
            self.player2 = HumanAgentArrows()
            print(f"Player 2: Human (Arrows) with {settings['car_color2']} car")
        elif player2_type == "DQN":
            state_dim = self.environment.get_state_dim()
            action_dim = self.environment.get_action_dim()
            self.player2 = DQNAgent(state_dim, action_dim)
            if os.path.exists(self.player2.model_path):
                ok = self.player2.load_model(self.player2.model_path)
                if ok:
                    print(f"Player 2: DQN AI loaded from {self.player2.model_path} with {settings['car_color2']} car")
                else:
                    print("Failed to load Player 2 model; starting fresh.")
            else:
                self.player2.save_model()
            if not game_state_manager.training_mode:
                try:
                    self.player2.set_inference_mode()
                except Exception:
                    self.player2.epsilon = 0.0
                    self.player2.policy_net.eval()
                    self.player2.target_net.eval()
        else:
            self.player2 = None

    def run(self, dt):
        """Main game loop - called every frame"""
        if not self.environment:
            self.initialize_environment()

        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                # Save model if in training before exit
                if isinstance(self.player1, DQNAgent) and game_state_manager.training_mode:
                    self.player1.save_model()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.environment.restart_game()
                elif event.key == pygame.K_SPACE:
                    if self.environment.game_state in ["finished", "failed"]:
                        self.environment.restart_game()
                elif event.key == pygame.K_ESCAPE:
                    self.environment.toggle_pause()

        # Update environment (physics, timers)
        self.environment.update()

        # If environment flagged that an episode just ended, save the model now (handles auto-restart case)
        if self.environment.episode_ended:
            if isinstance(self.player1, DQNAgent) and game_state_manager.training_mode:
                self.player1.save_model()
            # Clear the flag so we don't save repeatedly
            self.environment.episode_ended = False

        # Handle gameplay and possible inline training
        if self.environment.game_state == "running":
            self._process_player_actions()

        # Update prev env state for legacy checks
        self._prev_env_state = self.environment.game_state

        # Draw
        self.environment.draw()

    def _process_player_actions(self):
        """Process actions for both players.
        If the DQN agent is present and environment.ai_train_mode is True,
        run the simplified online training step inline (collect transitions, update).
        """
        p1_action = None
        p2_action = None

        # Player 1
        if self.player1:
            if isinstance(self.player1, DQNAgent):
                state1 = self.environment.get_state_for_player(1)
                if state1 is None:
                    p1_action = 0
                else:
                    # If training_mode (ai_train_mode), allow exploration
                    training_flag = self.environment.ai_train_mode and game_state_manager.training_mode
                    action_idx = self.player1.get_action(state1, training=training_flag)
                    p1_action = map_action_to_game_action(action_idx)

                    # If training inline, store transition and update
                    if training_flag:
                        pre_failed = self.environment.car1.failed
                        done = self.environment.move(p1_action, None)
                        post_failed = self.environment.car1.failed
                        collision = (not pre_failed) and post_failed

                        next_state = self.environment.get_state_for_player(1)
                        # Compute small-magnitude reward
                        reward = calculate_reward(self.environment, prev_state=state1, done=done, collision=collision)
                        self.player1.replay_buffer.add(state1, action_idx, reward, next_state,
                                                       self.environment.car1_finished or self.environment.car1.failed or done)
                        loss = self.player1.update()
                        # We already moved the environment in this branch, so return to avoid duplicate move
                        return
                    else:
                        # inference (non-training): just move later
                        pass
            else:
                p1_action = self.player1.get_action()
        else:
            p1_action = 0

        # Player 2
        if self.player2:
            if isinstance(self.player2, DQNAgent):
                state2 = self.environment.get_state_for_player(2)
                if state2 is None:
                    p2_action = 0
                else:
                    p2_action = self.player2.get_action(state2, training=False)
            else:
                p2_action = self.player2.get_action()
        else:
            p2_action = 0

        # Move both cars together for synchronous gameplay.
        self.environment.move(p1_action, p2_action)