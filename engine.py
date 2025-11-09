# engine.py - Updated for simple trainer
import pygame
import sys
from scripts.Constants import *
from scripts.menu import MainMenu, SettingsMenu
from scripts.Game import Game
from scripts.trainer import Trainer  # Use simplified trainer
from scripts.GameManager import game_state_manager

def main():
    pygame.init()
    
    # Setup display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Racing Game with AI")
    clock = pygame.time.Clock()
    
    # Create handlers
    main_menu = MainMenu(screen, clock)
    settings_menu = SettingsMenu(screen, clock)
    game = Game(screen, clock)
    
    # Trainer with run number (change this for different WandB runs)
    trainer = Trainer(screen, clock, run_number=1)
    
    print("Game Engine Started")
    print("Current state:", game_state_manager.getState())
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # 60 FPS for menus/game
        
        current_state = game_state_manager.getState()
        
        if current_state == 'main_menu':
            main_menu.run()
        
        elif current_state == 'settings_menu':
            settings_menu.run()
        
        elif current_state == 'game':
            game.run(dt)
        
        elif current_state == 'training':
            # Training runs uncapped (as fast as possible when viz off)
            trainer.run(dt)
        
        else:
            print(f"Unknown state: {current_state}")
            game_state_manager.setState('main_menu')
        
        pygame.display.flip()
        
        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()