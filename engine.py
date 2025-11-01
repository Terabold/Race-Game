import pygame
from scripts.Constants import DISPLAY_SIZE, FPS, FONT, MENUBG
from scripts.Game import Game
from scripts.menu import Menu
from scripts.GameManager import game_state_manager
from scripts.trainer import Trainer

class Engine:
    def __init__(self):
        pygame.init()
        pygame.joystick.quit()
        pygame.display.set_caption('AI Racing Game')
        self.display = pygame.display.set_mode((1600,900))
        self.clock = pygame.time.Clock()
        
        # Initialize game components
        self.game = Game(self.display, self.clock)
        self.menu = Menu(self.display, self.clock)
        
        # Import trainer module for training state
        self.trainer = Trainer(self.display, self.clock)
        
        self.state = {
            'game': self.game, 
            'menu': self.menu,
            'training': self.trainer
        }
        
    def run(self):
        previous_state = None

        while True:
            current_state = game_state_manager.getState()

            # Initialize environment when transitioning to game
            if previous_state == 'menu' and current_state == 'game':
                self.game.initialize_environment()
            
            # Initialize training when transitioning to training
            if previous_state == 'menu' and current_state == 'training':
                self.trainer.initialize()

            # Handle FPS cap based on state
            if current_state == 'training':
                dt = self.clock.tick() / 1000.0  # No FPS limit for training
            else:
                dt = self.clock.tick(FPS) / 1000.0  # Normal 60 FPS

            # Run appropriate state
            if current_state == 'game':
                self.state[current_state].run(dt)
            elif current_state == 'menu':
                self.menu.run()
            elif current_state == 'training':
                self.trainer.run(dt)

            previous_state = current_state
            
            # Always update display
            pygame.display.flip()


if __name__ == '__main__':
    Engine().run()