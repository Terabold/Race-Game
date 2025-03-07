import sys
from gui import GameMenu

def main():
    menu = GameMenu()
    settings = menu.run()
    
    if not settings:
        sys.exit()
    
    if settings['ai_train_mode']:
        import trainer
        trainer.start_training(settings)
    else:
        import Game
        Game.start_game(settings)

if __name__ == "__main__":
    main()