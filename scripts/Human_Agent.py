import pygame

class BaseHumanAgent:
    def __init__(self):
        self.action = 0
        self.controls = {
            'forward': None,
            'backward': None,
            'left': None,
            'right': None
        }

    def get_action(self):
        keys = pygame.key.get_pressed()
        
        forward = keys[self.controls['forward']]
        backward = keys[self.controls['backward']]
        left = keys[self.controls['left']]
        right = keys[self.controls['right']]
        
        if forward and left:
            self.action = 5
        elif forward and right:
            self.action = 6
        elif backward and left:
            self.action = 7
        elif backward and right:
            self.action = 8
        elif forward:
            self.action = 1
        elif backward:
            self.action = 2
        elif left:
            self.action = 3
        elif right:
            self.action = 4
        else:
            self.action = 0
            
        return self.action

class HumanAgentWASD(BaseHumanAgent):
    def __init__(self):
        super().__init__()
        self.controls = {
            'forward': pygame.K_w,
            'backward': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d
        }

class HumanAgentArrows(BaseHumanAgent):
    def __init__(self):
        super().__init__()
        self.controls = {
            'forward': pygame.K_UP,
            'backward': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT
        }