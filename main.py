"""Main module of snake game."""
from game import Game

def main():
    """Main function."""
    game = Game(window_size=600, title="Snake")
    game.start()

if __name__ == '__main__':
    main()
