import pygame
from scripts.Constants import DISPLAY_SIZE, FPS, FONT, MENUBG
from scripts.Game import Game
from scripts.menu import Menu
from scripts.GameManager import game_state_manager
from scripts.utils import scale_font

class Engine:
    def __init__(self):
        pygame.init()
        pygame.joystick.quit()
        pygame.display.set_caption('Ascent')
        self.display = pygame.display.set_mode((1600,900))
        self.clock = pygame.time.Clock()
        
        # Initialize game components
        self.game = Game(self.display, self.clock)
        self.menu = Menu(self.display, self.clock)
        
        self.state = {'game': self.game, 'menu': self.menu}
        
    def run(self):
        previous_state = None

        while True:
            current_state = game_state_manager.getState()

            if previous_state == 'menu' and current_state == 'game':
                self.game.initialize_environment()

            dt = self.clock.tick(FPS) / 1000.0

            if current_state == 'game':
                self.state[current_state].run(dt)
            elif current_state == 'menu':
                self.menu.run()

            previous_state = current_state
            pygame.display.flip()


if __name__ == '__main__':
    Engine().run()