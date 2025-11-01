import pygame
import sys
from scripts.Environment import Environment
from scripts.Human_Agent import HumanAgentWASD, HumanAgentArrows
from scripts.dqn_agent import DQNAgent
from scripts.GameManager import game_state_manager
import os

STATE_DIM = 22
ACTION_DIM = 8

class Game:
    def __init__(self, display, clock):
        self.display = display
        self.clock = clock
        self.environment = None
        self.player1 = None
        self.player2 = None

    def initialize_environment(self, settings=None):
        """Initialize the game environment and players"""
        if settings is None:
            settings = {
                'player1': game_state_manager.player1_selection,
                'player2': game_state_manager.player2_selection,
                'car_color1': game_state_manager.player1_car_color,
                'car_color2': game_state_manager.player2_car_color
            }

        # Create normal gameplay environment
        self.environment = Environment(
            self.display,
            car_color1=settings['car_color1'] if settings.get('player1') else None,
            car_color2=settings['car_color2'] if settings.get('player2') else None
        )
        
        self._setup_players(settings)
        print("Game initialized - Ready to play!")

    def _setup_players(self, settings):
        """Set up Player 1 and Player 2"""
        
        # ========== PLAYER 1 ==========
        player1_type = settings.get('player1')
        
        if player1_type == "Human":
            self.player1 = HumanAgentWASD()
            print(f"Player 1: Human (WASD) - {settings['car_color1']} car")
            
        elif player1_type == "DQN":
            self.player1 = DQNAgent(STATE_DIM, ACTION_DIM)
            
            # Load trained model
            if os.path.exists(self.player1.model_path):
                self.player1.load_model(self.player1.model_path)
                print(f"Player 1: AI loaded from {self.player1.model_path}")
            else:
                print("Warning: No trained model found for Player 1!")
            
            # INFERENCE MODE - No training during gameplay
            self.player1.epsilon = 0.02  # 2% randomness for variety
            self.player1.policy_net.eval()
            self.player1.target_net.eval()
            print(f"Player 1: AI in inference mode (ε={self.player1.epsilon})")
            
        else:
            self.player1 = None

        # ========== PLAYER 2 ==========
        player2_type = settings.get('player2')
        
        if player2_type == "Human":
            self.player2 = HumanAgentArrows()
            print(f"Player 2: Human (Arrows) - {settings['car_color2']} car")
            
        elif player2_type == "DQN":
            self.player2 = DQNAgent(STATE_DIM, ACTION_DIM)
            
            # Load trained model
            if os.path.exists(self.player2.model_path):
                self.player2.load_model(self.player2.model_path)
                print(f"Player 2: AI loaded from {self.player2.model_path}")
            else:
                print("Warning: No trained model found for Player 2!")
            
            # INFERENCE MODE - No training during gameplay
            self.player2.epsilon = 0.02  # 2% randomness for variety
            self.player2.policy_net.eval()
            self.player2.target_net.eval()
            print(f"Player 2: AI in inference mode (ε={self.player2.epsilon})")
            
        else:
            self.player2 = None

    def run(self, dt):
        """Main game loop - called every frame"""
        if not self.environment:
            self.initialize_environment()

        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                # Restart after game ends
                if event.key == pygame.K_SPACE:
                    if self.environment.game_state in ["finished", "failed"]:
                        self.environment.restart_game()
                        
                # Pause/unpause
                elif event.key == pygame.K_ESCAPE:
                    self.environment.toggle_pause()

        # Update environment (timers, physics, etc.)
        self.environment.update()

        # Get actions from both players
        p1_action = self._get_player_action(self.player1, car_num=1)
        p2_action = self._get_player_action(self.player2, car_num=2)

        # Execute actions in the environment
        self.environment.move(p1_action, p2_action)

        # Draw everything
        self.environment.draw()

    def _get_player_action(self, player, car_num):
        """Get action from a player (Human or AI)"""
        if player is None:
            return None
            
        # AI Player
        if isinstance(player, DQNAgent):
            state = self.environment.get_state(car_num=car_num)
            if state is None:
                return 0  # No action if no state
            
            # Get action in inference mode (no training)
            return player.get_action(state, training=False)
        
        # Human Player
        else:
            return player.get_action()