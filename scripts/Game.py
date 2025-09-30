import pygame
import sys
from scripts.Environment import Environment
from scripts.Human_Agent import HumanAgentWASD, HumanAgentArrows
from scripts.Constants import *
from scripts.dqn_agent import DQNAgent
from scripts.GameManager import game_state_manager
import os

class Game:
    def __init__(self, display, clock):
        self.display = display
        self.clock = clock
        self.environment = None
        self.player1 = None
        self.player2 = None
        
    def initialize_environment(self, settings=None):
        """Initialize environment with settings"""
        if settings is None:
            # Get settings from game_state_manager
            settings = {
                'player1': game_state_manager.player1_selection,
                'player2': game_state_manager.player2_selection,
                'car_color1': game_state_manager.player1_car_color,
                'car_color2': game_state_manager.player2_car_color
            }
        
        # Create environment - pass car colors only if player is selected
        self.environment = Environment(
            self.display,
            car_color1=settings['car_color1'] if settings.get('player1') else None,
            car_color2=settings['car_color2'] if settings.get('player2') else None
        )
        
        # Create agents based on settings
        self._setup_players(settings)
    
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
            self.player1 = DQNAgent(state_dim, action_dim)
            
            model_path = self._find_latest_model("models")
            if model_path and self.player1.load_model(model_path):
                print(f"Player 1: DQN AI loaded from {model_path} with {settings['car_color1']} car")
            else:
                print(f"Player 1: DQN AI (untrained) with {settings['car_color1']} car")
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
            
            model_path = self._find_latest_model("models")
            if model_path and self.player2.load_model(model_path):
                print(f"Player 2: DQN AI loaded from {model_path} with {settings['car_color2']} car")
            else:
                print(f"Player 2: DQN AI (untrained) with {settings['car_color2']} car")
        else:
            self.player2 = None
    
    def _find_latest_model(self, models_dir):
        """Find the most recent model file"""
        if not os.path.exists(models_dir):
            return None
        
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.pth')]
        if not model_files:
            return None
        
        try:
            model_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]), reverse=True)
            return os.path.join(models_dir, model_files[0])
        except:
            return os.path.join(models_dir, model_files[0])

    def run(self, dt):
        """Main game loop - called every frame"""
        if not self.environment:
            self.initialize_environment()
        
        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
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
        
        # Update environment
        self.environment.update()
        
        # Handle gameplay
        if self.environment.game_state == "running":
            self._process_player_actions()
        
        # Draw
        self.environment.draw()
    
    def _process_player_actions(self):
        """Process actions for both players"""
        p1_action = None
        p2_action = None
        
        try:
            # Get Player 1 action
            if self.player1:
                if isinstance(self.player1, DQNAgent):
                    state1 = self.environment.get_state_for_player(1)
                    if state1 is not None:
                        p1_action = self.player1.get_action(state1, training=False)
                    else:
                        p1_action = 0
                else:
                    # Human agent
                    p1_action = self.player1.get_action()
            else:
                p1_action = 0
                    
            # Get Player 2 action
            if self.player2:
                if isinstance(self.player2, DQNAgent):
                    state2 = self.environment.get_state_for_player(2)
                    if state2 is not None:
                        p2_action = self.player2.get_action(state2, training=False)
                    else:
                        p2_action = 0
                else:
                    # Human agent
                    p2_action = self.player2.get_action()
            else:
                p2_action = 0
            
            # Move both cars
            self.environment.move(p1_action, p2_action)
            
        except Exception as e:
            print(f"Error during game loop: {e}")
            import traceback
            traceback.print_exc()
            self.environment.move(0, 0)