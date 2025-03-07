import pygame
import sys
from Environment import Environment
from Human_Agent import HumanAgentWASD, HumanAgentArrows
from Constants import *
import os

def start_game(settings):
   
    pygame.init()
    pygame.mixer.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Racing Game")
    clock = pygame.time.Clock()
    
    environment = Environment(
        surface, 
        car_color1=settings['car_color1'] if settings['player1'] else None,
        car_color2=settings['car_color2'] if settings['player2'] else None
    )
    
    player1 = HumanAgentWASD() if settings['player1'] == "Human" else None
    player2 = HumanAgentArrows() if settings['player2'] == "Human" else None
    
    game_loop(environment, player1, player2, clock)
    
    pygame.quit()

def game_loop(environment, player1, player2, clock):
    running = True
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    environment.restart_game()
                elif event.key == pygame.K_SPACE:
                    if environment.game_state in ["finished", "failed"]:
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
    start_game()