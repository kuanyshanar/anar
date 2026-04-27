import os

# Размер окна 
WIDTH = 800
HEIGHT = 600
CELL_SIZE = 20
FPS = 60

# Поля
TOP_PANEL = 60
COLS = WIDTH // CELL_SIZE
ROWS = (HEIGHT - TOP_PANEL) // CELL_SIZE

# Скорость, уровни 
BASE_SPEED = 8
LEVEL_UP_EVERY = 5
OBSTACLES_PER_LEVEL = 4

# Пути 
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")


IMAGE_FILES = {
    "food": "food.png",
    "poison": "poison.png",
    "speed": "speed.png",
    "slow": "slow.png",
    "shield": "shield.png",
    "snake_head": "snake_head.png",
    "snake_body": "snake_body.png",
    "obstacle": "obstacle.png",
    "background": "background.png"
}


DB_CONFIG = {
    "host": "localhost",
    "database": "snake_db",
    "user": "postgres",
    "password": "3011",
    "port": 5432,
}