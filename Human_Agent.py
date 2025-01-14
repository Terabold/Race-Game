import pygame

class Human_Agent:
    def __init__(self):
        self.action = 0  # Default action (no movement)

    def get_action(self):
        keys = pygame.key.get_pressed()
        
        forward = keys[pygame.K_w]
        backward = keys[pygame.K_s]
        left = keys[pygame.K_a]
        right = keys[pygame.K_d]
        
        # Update self.action based on key presses
        if forward and left:
            self.action = 5  # forward-left
        elif forward and right:
            self.action = 6  # forward-right
        elif backward and left:
            self.action = 7  # backward-left
        elif backward and right:
            self.action = 8  # backward-right
        elif forward:
            self.action = 1  # forward
        elif backward:
            self.action = 2  # backward
        elif left:
            self.action = 3  # left
        elif right:
            self.action = 4  # right
        else:
            self.action = 0  # no movement

        return self.action

class Human_Agent2:
    def __init__(self):
        self.action = 0  # Default action (no movement)

    def get_action(self):
        keys = pygame.key.get_pressed()
        
        forward = keys[pygame.K_UP]
        backward = keys[pygame.K_DOWN]
        left = keys[pygame.K_LEFT]
        right = keys[pygame.K_RIGHT]
        
        # Update action based on key presses
        if forward and left:
            self.action = 5  # forward-left
        elif forward and right:
            self.action = 6  # forward-right
        elif backward and left:
            self.action = 7  # backward-left
        elif backward and right:
            self.action = 8  # backward-right
        elif forward:
            self.action = 1  # forward
        elif backward:
            self.action = 2  # backward
        elif left:
            self.action = 3  # left
        elif right:
            self.action = 4  # right
        else:
            self.action = 0  # no movement

        return self.action