from db import Database
from game import SnakeGame


if __name__ == "__main__":
    db = Database()
    game = SnakeGame(db)
    game.run()