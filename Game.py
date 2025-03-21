import pygame
import sys
from Environment import Environment
from Human_Agent import HumanAgentWASD, HumanAgentArrows
from Constants import *
import os
from dqn_agent import DQNAgent

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
    
    # Create agents based on settings
    player1 = None
    if settings['player1'] == "Human":
        player1 = HumanAgentWASD()
    elif settings['player1'] == "DQN":
        # Create DQN agent for player 1
        state_dim = environment.get_state_dim()  # You'll need to add this method to Environment
        action_dim = environment.get_action_dim()  # You'll need to add this method to Environment
        player1 = DQNAgent(state_dim, action_dim)
        # Load the pre-trained model
        player1.load_model("models\dqn_episode_0.pth")  # Path to your model
    
    player2 = None
    if settings['player2'] == "Human":
        player2 = HumanAgentArrows()
    elif settings['player2'] == "DQN":
        # Create DQN agent for player 2
        state_dim = environment.get_state_dim()
        action_dim = environment.get_action_dim()
        player2 = DQNAgent(state_dim, action_dim)
        # Load the pre-trained model
        player2.load_model("models\dqn_episode_0.pth")  # Path to your model
    
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
            # Get actions for each player
            p1_action = None
            p2_action = None
            
            if player1:
                if isinstance(player1, DQNAgent):
                    # Get state for player 1 and select action
                    state1 = environment.get_state_for_player(1)  # You'll need to add this method
                    p1_action = player1.get_action(state1, training=False)
                else:
                    p1_action = player1.get_action()
                    
            if player2:
                if isinstance(player2, DQNAgent):
                    # Get state for player 2 and select action
                    state2 = environment.get_state_for_player(2)  # You'll need to add this method
                    p2_action = player2.get_action(state2, training=False)
                else:
                    p2_action = player2.get_action()
            
            environment.move(p1_action, p2_action)
            
        environment.draw()
        pygame.display.update()

if __name__ == "__main__":
    start_game()