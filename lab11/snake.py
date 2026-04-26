import pygame
import random
import sys

pygame.init()

# Константы
CELL         = 20
COLS         = 25
ROWS         = 25
PANEL_H      = 60      # высота HUD-панели сверху

SCREEN_W     = CELL * COLS
SCREEN_H     = CELL * ROWS + PANEL_H

FPS_START    = 8       # начальная скорость (кадров/сек)
FPS_STEP     = 2       # прибавка скорости за уровень
FOOD_PER_LVL = 3       # сколько еды нужно до следующего уровня

# Время жизни еды в ходах змеи.
# После истечения таймера еда исчезает и появляется новая.
FOOD_LIFETIME_TICKS = 25

# Типы еды с весами
# weight — вероятность появления (больше = чаще)
# points — очки за поедание
FOOD_TYPES = [
    {"name": "Apple",   "color": (220,  50,  50), "outline": (150,  10,  10), "points":  10, "weight": 50},
    {"name": "Banana",  "color": (255, 220,   0), "outline": (180, 140,   0), "points":  20, "weight": 30},
    {"name": "Cherry",  "color": (180,   0, 100), "outline": (100,   0,  60), "points":  40, "weight": 15},
    {"name": "Diamond", "color": (100, 220, 255), "outline": ( 30, 140, 200), "points":  80, "weight":  5},
]

# Цвета интерфейса
BG_COLOR    = (15,  20,  30)
GRID_COLOR  = (25,  32,  45)
PANEL_COLOR = (10,  14,  22)
SNAKE_HEAD  = (50,  220,  80)
SNAKE_BODY  = (30,  160,  55)
SNAKE_OUT   = (20,  100,  35)
WALL_COLOR  = (80,   90, 110)
WALL_OUT    = (50,   60,  80)
WHITE       = (255, 255, 255)
GOLD        = (255, 210,   0)
TEXT_COLOR  = (200, 210, 230)
LEVEL_COLOR = (100, 200, 255)
TIMER_OK    = (80,  200, 100)   # цвет таймер-бара когда времени много
TIMER_WARN  = (255, 100,  50)   # цвет когда времени мало

# Создание окна
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Snake")
clock  = pygame.time.Clock()

font_big   = pygame.font.SysFont("Arial", 42, bold=True)
font_med   = pygame.font.SysFont("Arial", 24, bold=True)
font_small = pygame.font.SysFont("Arial", 17)
font_tiny  = pygame.font.SysFont("Arial", 13)


# Классы

class Food:
    """
    Еда с типом (весовая система) и таймером исчезновения.
    Тип выбирается случайно через random.choices с учётом весов.
    Таймер отсчитывается в ходах змеи: tick_left уменьшается
    на 1 при каждом шаге змеи, а не каждом кадре.
    """

    def __init__(self, col, row):
        # Выбираем тип еды по весам
        weights    = [ft["weight"] for ft in FOOD_TYPES]
        self.ftype = random.choices(FOOD_TYPES, weights=weights, k=1)[0]
        self.col   = col
        self.row   = row
        self.tick_left = FOOD_LIFETIME_TICKS   # оставшихся ходов

    def tick(self):
        """Уменьшает таймер на 1 ход. Возвращает True если время вышло."""
        self.tick_left -= 1
        return self.tick_left <= 0

    @property
    def fraction(self):
        """Доля оставшегося времени от 0.0 до 1.0 для прогресс-бара."""
        return self.tick_left / FOOD_LIFETIME_TICKS

    def draw(self, surface):
        r   = cell_rect(self.col, self.row).inflate(-3, -3)
        # Кружок цвета типа еды
        pygame.draw.ellipse(surface, self.ftype["color"],   r)
        pygame.draw.ellipse(surface, self.ftype["outline"], r, 2)

        # Подпись очков
        lbl = font_tiny.render(f"+{self.ftype['points']}", True, (30, 30, 30))
        surface.blit(lbl, lbl.get_rect(center=r.center))

        # Таймер-бар под ячейкой (зелёный, потом становится красным)
        bar_r = pygame.Rect(self.col * CELL, self.row * CELL + PANEL_H + CELL - 4, CELL, 4)
        pygame.draw.rect(surface, (40, 50, 70), bar_r)
        filled    = int(bar_r.width * self.fraction)
        bar_color = TIMER_OK if self.fraction > 0.35 else TIMER_WARN
        if filled > 0:
            pygame.draw.rect(surface, bar_color, (bar_r.x, bar_r.y, filled, bar_r.height))


# Вспомогательные функции

def cell_rect(col, row):
    """Возвращает прямоугольник клетки с учётом панели сверху."""
    return pygame.Rect(col * CELL, row * CELL + PANEL_H, CELL, CELL)


def draw_cell(surface, col, row, color, outline=None, radius=4):
    """Рисует закруглённый прямоугольник в клетке."""
    r = cell_rect(col, row).inflate(-2, -2)
    pygame.draw.rect(surface, color, r, border_radius=radius)
    if outline:
        pygame.draw.rect(surface, outline, r, width=2, border_radius=radius)


def draw_grid(surface):
    """Рисует тёмный фон поля и тонкую сетку."""
    pygame.draw.rect(surface, BG_COLOR, pygame.Rect(0, PANEL_H, SCREEN_W, SCREEN_H - PANEL_H))
    for r in range(ROWS + 1):
        pygame.draw.line(surface, GRID_COLOR, (0, r * CELL + PANEL_H), (SCREEN_W, r * CELL + PANEL_H))
    for c in range(COLS + 1):
        pygame.draw.line(surface, GRID_COLOR, (c * CELL, PANEL_H), (c * CELL, SCREEN_H))


def draw_hud(surface, score, level, food_eaten, fps):
    """Рисует панель HUD: счёт, уровень, прогресс-бар до следующего уровня."""
    pygame.draw.rect(surface, PANEL_COLOR, (0, 0, SCREEN_W, PANEL_H))
    pygame.draw.line(surface, WALL_COLOR, (0, PANEL_H), (SCREEN_W, PANEL_H), 2)

    surface.blit(font_med.render(f"Score: {score}", True, TEXT_COLOR), (12, 10))
    surface.blit(font_med.render(f"Level: {level}", True, LEVEL_COLOR), (12, 34))

    # Прогресс-бар до следующего уровня
    bar_w  = 160
    bar_h  = 14
    bar_x  = SCREEN_W - bar_w - 12
    bar_y  = 12
    filled = int(bar_w * (food_eaten % FOOD_PER_LVL) / FOOD_PER_LVL)
    pygame.draw.rect(surface, (40, 50, 70), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
    if filled > 0:
        pygame.draw.rect(surface, GOLD, (bar_x, bar_y, filled, bar_h), border_radius=6)
    pygame.draw.rect(surface, WALL_COLOR, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=6)
    surface.blit(font_tiny.render("Next level", True, TEXT_COLOR), (bar_x, bar_y + bar_h + 3))
    surface.blit(font_tiny.render(f"Speed:{fps}", True, (150, 160, 180)), (SCREEN_W - 80, bar_y + bar_h + 3))


def show_overlay(surface, title, lines):
    """Рисует полупрозрачный оверлей с заголовком и строками текста."""
    ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 170))
    surface.blit(ov, (0, 0))
    t = font_big.render(title, True, WHITE)
    surface.blit(t, t.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 50)))
    for i, line in enumerate(lines):
        s = font_small.render(line, True, (200, 210, 230))
        surface.blit(s, s.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 10 + i * 26)))


def random_free_pos(snake_body, walls, food_list):
    """
    Возвращает случайную клетку, свободную от змеи, стен и еды.
    Гарантирует, что еда не появится на занятой позиции.
    """
    occupied = set(snake_body) | walls | {(f.col, f.row) for f in food_list}
    while True:
        col = random.randint(1, COLS - 2)
        row = random.randint(1, ROWS - 2)
        if (col, row) not in occupied:
            return col, row


def generate_walls(level):
    """
    Генерирует внутренние стены в зависимости от уровня.
    Уровень 1 — без стен, с уровня 2 появляются препятствия.
    """
    walls = set()
    if level < 2:
        return walls
    # Горизонтальный барьер посередине
    mid_r  = ROWS // 2
    length = min(4 + level * 2, COLS - 6)
    start  = (COLS - length) // 2
    for c in range(start, start + length):
        walls.add((c, mid_r))
    if level >= 3:
        # Вертикальные столбики по бокам
        mid_c = COLS // 2
        for r in range(4, ROWS - 4, 3):
            walls.add((mid_c - 6, r))
            walls.add((mid_c + 6, r))
    if level >= 4:
        # Дополнительные блоки по углам
        for c in range(3, 7):
            walls.add((c, 5))
            walls.add((COLS - c - 1, ROWS - 6))
    return walls


# Главный игровой цикл

def game_loop():
    level       = 1
    score       = 0
    food_eaten  = 0        # всего съедено (для расчёта уровня)
    current_fps = FPS_START

    # Змея — список клеток (col, row), голова первая
    snake     = [(COLS // 2, ROWS // 2),
                 (COLS // 2 - 1, ROWS // 2),
                 (COLS // 2 - 2, ROWS // 2)]
    direction = (1, 0)
    next_dir  = direction

    walls     = generate_walls(level)

    # На поле одновременно одна единица еды
    food_list = [Food(*random_free_pos(snake, walls, []))]

    started      = False
    game_over    = False
    level_up_msg = 0   # кадры показа сообщения о новом уровне

    while True:
        clock.tick(current_fps)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not started:
                        started = True
                    elif game_over:
                        game_loop()
                        return
                # Управление змеёй (нельзя развернуться на 180°)
                if event.key == pygame.K_UP    and direction != (0,  1): next_dir = (0, -1)
                if event.key == pygame.K_DOWN  and direction != (0, -1): next_dir = (0,  1)
                if event.key == pygame.K_LEFT  and direction != (1,  0): next_dir = (-1, 0)
                if event.key == pygame.K_RIGHT and direction != (-1, 0): next_dir = (1,  0)

        # Стартовый экран
        if not started:
            draw_grid(screen)
            draw_hud(screen, score, level, food_eaten, current_fps)
            show_overlay(screen, "SNAKE", ["Arrow keys — move", "SPACE — start"])
            pygame.display.flip()
            continue

        # Экран конца игры
        if game_over:
            draw_grid(screen)
            for w in walls:
                draw_cell(screen, *w, WALL_COLOR, WALL_OUT)
            for f in food_list:
                f.draw(screen)
            for i, seg in enumerate(snake):
                draw_cell(screen, *seg, SNAKE_HEAD if i == 0 else SNAKE_BODY, SNAKE_OUT)
            draw_hud(screen, score, level, food_eaten, current_fps)
            show_overlay(screen, "GAME OVER",
                         [f"Score: {score}   Level: {level}", "SPACE — restart"])
            pygame.display.flip()
            continue

        # Шаг змеи
        direction = next_dir
        hc, hr    = snake[0]
        new_head  = (hc + direction[0], hr + direction[1])

        # Проверка выхода за границу поля
        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            game_over = True
            continue

        # Проверка столкновения с телом
        if new_head in snake[1:]:
            game_over = True
            continue

        # Проверка столкновения с внутренней стеной
        if new_head in walls:
            game_over = True
            continue

        # Проверяем, съела ли змея еду
        eaten_food = next((f for f in food_list if (f.col, f.row) == new_head), None)

        snake.insert(0, new_head)

        if eaten_food:
            # Змея растёт (хвост не убираем), добавляем очки
            score      += eaten_food.ftype["points"] * level
            food_eaten += 1
            food_list.remove(eaten_food)

            # Проверка повышения уровня
            if food_eaten % FOOD_PER_LVL == 0:
                level        += 1
                current_fps   = FPS_START + (level - 1) * FPS_STEP
                walls         = generate_walls(level)
                level_up_msg  = current_fps * 2

            # Спавним новую еду
            food_list.append(Food(*random_free_pos(snake, walls, food_list)))
        else:
            snake.pop()   # обычный шаг — убираем хвост

        # Тик таймера для каждой еды (один раз за ход змеи)
        expired = [f for f in food_list if f.tick()]
        for f in expired:
            food_list.remove(f)
            # Заменяем исчезнувшую еду новой
            food_list.append(Food(*random_free_pos(snake, walls, food_list)))

        if level_up_msg > 0:
            level_up_msg -= 1

        # Отрисовка
        draw_grid(screen)

        for w in walls:
            draw_cell(screen, *w, WALL_COLOR, WALL_OUT, radius=2)

        # Рисуем еду с таймер-баром
        for f in food_list:
            f.draw(screen)

        for i, seg in enumerate(snake):
            draw_cell(screen, *seg, SNAKE_HEAD if i == 0 else SNAKE_BODY, SNAKE_OUT)

        draw_hud(screen, score, level, food_eaten, current_fps)

        # Сообщение о повышении уровня
        if level_up_msg > 0:
            msg = font_med.render(f"LEVEL {level}!", True, GOLD)
            screen.blit(msg, msg.get_rect(center=(SCREEN_W // 2, PANEL_H + 40)))

        pygame.display.flip()


if __name__ == "__main__":
    game_loop()