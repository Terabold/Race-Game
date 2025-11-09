# GameManager.py - COMPLETE FIXED VERSION
class GameStateManager:
    """Manages game state transitions with separate menu states"""
    def __init__(self):
        self.state = 'main_menu'  # Start with main menu
        self.previous_state = None
        # Game settings
        self.player1_selection = None
        self.player2_selection = None
        self.player1_car_color = "Blue"
        self.player2_car_color = "Red"
        
    def setState(self, new_state):
        """Change to a new game state"""
        valid_states = ['main_menu', 'settings_menu', 'game', 'training']
        if new_state not in valid_states:
            print(f"Warning: Invalid state '{new_state}'. Valid states: {valid_states}")
            # Default to main menu if invalid
            new_state = 'main_menu'
            
        self.previous_state = self.state
        self.state = new_state
        
    def getState(self):
        """Get current game state"""
        return self.state
    
    def getPreviousState(self):
        """Get previous game state"""
        return self.previous_state
    
    def resetSelections(self):
        """Reset player selections (when returning to menu)"""
        self.player1_selection = None
        self.player2_selection = None

# Global game state manager instance
game_state_manager = GameStateManager()