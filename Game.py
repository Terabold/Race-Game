import pygame
import sys
from Environment import Environment
from Human_Agent import HumanAgentWASD, HumanAgentArrows
from Constants import *
from GUI import GameMenu

def main():
    menu = GameMenu()
    settings = menu.run()
    
    if settings:
        pygame.init()
        pygame.mixer.init()
        surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Racing Game")
        clock = pygame.time.Clock()
        
        environment = Environment(
            surface, 
            sound_enabled=settings['sound_enabled'],
            auto_respawn=settings['auto_respawn'],
            car_color1=settings['car_color1'] if settings['player1'] else None,
            car_color2=settings['car_color2'] if settings['player2'] else None,
            countdown_enabled=settings['countdown']
        )
        
        player1 = HumanAgentWASD() if settings['player1'] else None
        player2 = HumanAgentArrows() if settings['player2'] == "Human" else None
        
        while True:
            clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        environment.restart_game()
                    elif event.key == pygame.K_SPACE:
                        if environment.game_state == "finished":
                            environment.restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        environment.toggle_pause()
            
            environment.update()
            if environment.game_state == "running":
                environment.move(
                    player1.get_action() if player1 else None,
                    player2.get_action() if player2 else None
                )
            environment.draw()
            pygame.display.update()

if __name__ == "__main__":
    main()