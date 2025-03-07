import pygame
import sys
from Environment import Environment
from Human_Agent import HumanAgentWASD, HumanAgentArrows
from Constants import *
from Options import GameMenu
import os
def start_training():
    settings = {
        'player1': 'DQN', 
        'player2': None,   
        'car_color1': 'Red',
        'car_color2': None
    }
    
    pygame.init()
    pygame.mixer.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Racing Game - AI Training")
    clock = pygame.time.Clock()
    
    environment = Environment(
        surface, 
        ai_train_mode=True,
        car_color1=settings['car_color1'],
        car_color2=settings['car_color2']
    )
    
    player1 = None 
    player2 = None
    
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
    start_training()