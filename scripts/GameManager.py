class GameStateManager:
    """Manages game state transitions"""
    def __init__(self):
        self.state = 'menu'
        self.previous_state = None
        
        # Game settings
        self.player1_selection = None
        self.player2_selection = None
        self.player1_car_color = "Blue"
        self.player2_car_color = "Red"

        # Training mode flag - used to distinguish training from normal gameplay
        self.training_mode = False
        
    def setState(self, new_state):
        """Change to a new game state"""
        self.previous_state = self.state
        self.state = new_state
        
    def getState(self):
        """Get current game state"""
        return self.state
    
    def getPreviousState(self):
        """Get previous game state"""
        return self.previous_state

# Global game state manager instance
game_state_manager = GameStateManager()