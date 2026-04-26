import pygame
import random
import sys

pygame.init()

# Константы
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600

# Цвета (R, G, B)
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
BLUE       = (50,  100, 255)
YELLOW     = (255, 220,   0)
GRAY       = (80,   80,  80)
DARK_GRAY  = (50,   50,  50)
ORANGE     = (255, 165,   0)

# Параметры дороги
ROAD_LEFT  = 60
ROAD_RIGHT = 340
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT

# Частота кадров
FPS = 60

# Типы монет: name, color, outline, points, weight
# weight — вероятность появления (больше = чаще)
# points — очки за подбор
COIN_TYPES = [
    {"name": "Bronze",  "color": (180, 100,  40), "outline": (120,  60,  10), "points":  5, "weight": 60},
    {"name": "Silver",  "color": (180, 180, 190), "outline": (120, 120, 130), "points": 15, "weight": 30},
    {"name": "Gold",    "color": (255, 200,   0), "outline": (200, 130,   0), "points": 30, "weight":  8},
    {"name": "Diamond", "color": (150, 230, 255), "outline": ( 60, 160, 220), "points": 60, "weight":  2},
]

# Каждые N подобранных монет враги ускоряются
SPEED_UP_EVERY = 10

# Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")
clock = pygame.time.Clock()

# Шрифты
font_large  = pygame.font.SysFont("Arial", 48, bold=True)
font_medium = pygame.font.SysFont("Arial", 26, bold=True)
font_small  = pygame.font.SysFont("Arial", 20)
font_tiny   = pygame.font.SysFont("Arial", 14, bold=True)


# Классы

class PlayerCar:
    """Машина игрока, управляется стрелками влево и вправо."""

    WIDTH  = 40
    HEIGHT = 70
    SPEED  = 5

    def __init__(self):
        # Стартовая позиция — по центру дороги, внизу экрана
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2 - self.WIDTH // 2,
            SCREEN_HEIGHT - self.HEIGHT - 20,
            self.WIDTH, self.HEIGHT
        )

    def move(self, keys):
        # Двигаем машину, не выходя за границы дороги
        if keys[pygame.K_LEFT]  and self.rect.left  > ROAD_LEFT  + 5:
            self.rect.x -= self.SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < ROAD_RIGHT - 5:
            self.rect.x += self.SPEED

    def draw(self, surface):
        r = self.rect
        # Кузов
        pygame.draw.rect(surface, BLUE, r, border_radius=6)
        # Лобовое стекло
        pygame.draw.rect(surface, (180, 220, 255), (r.x + 5, r.y + 8, r.width - 10, 18), border_radius=3)
        # Заднее стекло
        pygame.draw.rect(surface, (180, 220, 255), (r.x + 5, r.bottom - 26, r.width - 10, 14), border_radius=3)
        # Колёса
        for cx in (r.x - 6, r.right - 2):
            for cy in (r.y + 8, r.bottom - 26):
                pygame.draw.rect(surface, DARK_GRAY, (cx, cy, 8, 18), border_radius=3)


class EnemyCar:
    """Машина-препятствие, едет сверху вниз."""

    WIDTH  = 40
    HEIGHT = 70
    COLORS = [(220, 50, 50), (50, 180, 50), (200, 100, 200), (255, 140, 0)]

    def __init__(self, speed):
        # Случайная полоса: левая, центральная или правая
        lane_x = [
            ROAD_LEFT + 10,
            ROAD_LEFT + ROAD_WIDTH // 2 - self.WIDTH // 2,
            ROAD_RIGHT - self.WIDTH - 10,
        ]
        self.rect  = pygame.Rect(random.choice(lane_x), -self.HEIGHT, self.WIDTH, self.HEIGHT)
        self.speed = speed
        self.color = random.choice(self.COLORS)

    def update(self):
        # Сдвигаем машину вниз
        self.rect.y += self.speed

    def is_offscreen(self):
        return self.rect.top > SCREEN_HEIGHT

    def draw(self, surface):
        r = self.rect
        # Кузов
        pygame.draw.rect(surface, self.color, r, border_radius=6)
        # Лобовое стекло (снизу, т.к. едет к нам)
        pygame.draw.rect(surface, (255, 255, 200), (r.x + 5, r.bottom - 26, r.width - 10, 14), border_radius=3)
        # Фары
        pygame.draw.circle(surface, YELLOW, (r.x + 8,      r.bottom - 10), 5)
        pygame.draw.circle(surface, YELLOW, (r.right - 8,  r.bottom - 10), 5)
        # Колёса
        for cx in (r.x - 6, r.right - 2):
            for cy in (r.y + 8, r.bottom - 26):
                pygame.draw.rect(surface, DARK_GRAY, (cx, cy, 8, 18), border_radius=3)


class Coin:
    """
    Монета с весовой системой.
    Тип выбирается случайно через random.choices по весам:
      Bronze  weight=60 — самая частая
      Silver  weight=30
      Gold    weight=8
      Diamond weight=2  — очень редкая
    """

    RADIUS = 13

    def __init__(self, speed):
        # Выбираем тип монеты по весам
        weights    = [ct["weight"] for ct in COIN_TYPES]
        self.ctype = random.choices(COIN_TYPES, weights=weights, k=1)[0]

        # Случайная позиция по X внутри дороги
        self.x     = random.randint(ROAD_LEFT + self.RADIUS + 10,
                                    ROAD_RIGHT - self.RADIUS - 10)
        self.y     = float(-self.RADIUS)
        self.speed = speed
        self.rect  = pygame.Rect(0, 0, self.RADIUS * 2, self.RADIUS * 2)
        self.rect.center = (self.x, int(self.y))

    def update(self):
        # Сдвигаем монету вниз и обновляем хитбокс
        self.y += self.speed
        self.rect.center = (self.x, int(self.y))

    def is_offscreen(self):
        return self.y - self.RADIUS > SCREEN_HEIGHT

    def draw(self, surface):
        cx, cy = self.x, int(self.y)
        # Основной круг
        pygame.draw.circle(surface, self.ctype["color"],   (cx, cy), self.RADIUS)
        # Ободок
        pygame.draw.circle(surface, self.ctype["outline"], (cx, cy), self.RADIUS, 2)
        # Подпись очков
        lbl = font_tiny.render(f"+{self.ctype['points']}", True, (20, 20, 20))
        surface.blit(lbl, lbl.get_rect(center=(cx, cy)))


class RoadLine:
    """Белая разметка дороги, движется вниз для иллюзии скорости."""

    WIDTH  = 10
    HEIGHT = 40

    def __init__(self, x, y, speed):
        self.rect  = pygame.Rect(x - self.WIDTH // 2, y, self.WIDTH, self.HEIGHT)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

    def is_offscreen(self):
        return self.rect.top > SCREEN_HEIGHT

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=3)


# Вспомогательные функции

def draw_background(surface):
    """Рисует траву, дорогу и белые бордюры."""
    surface.fill((34, 139, 34))
    pygame.draw.rect(surface, GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, SCREEN_HEIGHT))
    pygame.draw.line(surface, WHITE, (ROAD_LEFT,  0), (ROAD_LEFT,  SCREEN_HEIGHT), 3)
    pygame.draw.line(surface, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, SCREEN_HEIGHT), 3)


def draw_hud(surface, score, coins, coin_pts, level, enemy_spd):
    """Рисует счёт, уровень, количество монет и скорость врагов."""
    # Очки и уровень слева
    surface.blit(font_small.render(f"Score: {score}", True, WHITE), (10, 10))
    surface.blit(font_small.render(f"Level: {level}", True, WHITE), (10, 34))

    # Монеты, очки с монет и скорость врагов справа
    info = [
        (f"Coins: {coins}",       YELLOW),
        (f"Pts: {coin_pts}",      (200, 255, 200)),
        (f"Spd: {enemy_spd:.1f}", (255, 160,  80)),
    ]
    for i, (txt, col) in enumerate(info):
        s = font_tiny.render(txt, True, col)
        surface.blit(s, (SCREEN_WIDTH - s.get_width() - 8, 8 + i * 18))

    # Легенда типов монет внизу экрана
    lx = ROAD_LEFT + 4
    for ct in COIN_TYPES:
        lbl = font_tiny.render(f"{ct['name']}+{ct['points']}", True, ct["color"])
        surface.blit(lbl, (lx, SCREEN_HEIGHT - 18))
        lx += lbl.get_width() + 12


def show_message(surface, title, sub):
    """Рисует полупрозрачный оверлей с заголовком и подписью."""
    ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 160))
    surface.blit(ov, (0, 0))
    t1 = font_large.render(title, True, WHITE)
    t2 = font_small.render(sub,   True, (200, 200, 200))
    surface.blit(t1, t1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)))
    surface.blit(t2, t2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)))


# Главный игровой цикл

def game_loop():
    player      = PlayerCar()
    enemies     = []
    coins_list  = []
    road_lines  = []

    score       = 0     # очки за выживание и монеты
    coins_count = 0     # количество подобранных монет
    coin_pts    = 0     # суммарные очки с монет
    level       = 1

    enemy_speed = 4.0   # текущая скорость врагов
    road_speed  = 4.0

    enemy_cd    = 90
    coin_cd     = random.randint(120, 240)
    line_cd     = 30

    speed_flash = 0     # кадры показа сообщения об ускорении

    # Начальная разметка дороги
    center_x = ROAD_LEFT + ROAD_WIDTH // 2
    for y in range(0, SCREEN_HEIGHT, 80):
        road_lines.append(RoadLine(center_x, y, road_speed))

    started = game_over = False

    while True:
        clock.tick(FPS)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not started:
                    started = True
                elif game_over:
                    game_loop()
                    return

        # Стартовый экран
        if not started:
            draw_background(screen)
            show_message(screen, "RACER", "Press SPACE to start")
            pygame.display.flip()
            continue

        # Экран конца игры
        if game_over:
            draw_background(screen)
            for o in road_lines + enemies + coins_list:
                o.draw(screen)
            player.draw(screen)
            draw_hud(screen, score, coins_count, coin_pts, level, enemy_speed)
            show_message(screen, "GAME OVER",
                         f"Score:{score}  Coins:{coins_count}  SPACE=restart")
            pygame.display.flip()
            continue

        # Счётчик очков растёт каждый кадр выживания
        score += 1

        # Повышение уровня каждые 500 очков
        new_level = score // 500 + 1
        if new_level != level:
            level = new_level

        # Движение игрока
        player.move(pygame.key.get_pressed())

        # Спавн разметки дороги
        line_cd -= 1
        if line_cd <= 0:
            road_lines.append(RoadLine(center_x, -RoadLine.HEIGHT, road_speed))
            line_cd = 30

        # Спавн врагов (чаще на высоких уровнях)
        enemy_cd -= 1
        if enemy_cd <= 0:
            enemies.append(EnemyCar(enemy_speed))
            enemy_cd = max(35, 90 - level * 8)

        # Спавн монет со случайным интервалом
        coin_cd -= 1
        if coin_cd <= 0:
            coins_list.append(Coin(road_speed))
            coin_cd = random.randint(100, 220)

        # Обновление всех объектов
        for obj in road_lines + enemies + coins_list:
            obj.update()

        # Удаление объектов за нижним краем экрана
        road_lines = [o for o in road_lines if not o.is_offscreen()]
        enemies    = [o for o in enemies    if not o.is_offscreen()]
        coins_list = [o for o in coins_list if not o.is_offscreen()]

        # Проверка столкновения с врагом
        if any(player.rect.colliderect(e.rect) for e in enemies):
            game_over = True

        # Подбор монет
        collected = [c for c in coins_list if player.rect.colliderect(c.rect)]
        for c in collected:
            coins_count += 1
            coin_pts    += c.ctype["points"]
            score       += c.ctype["points"]
            coins_list.remove(c)

            # Каждые SPEED_UP_EVERY монет ускоряем врагов
            if coins_count % SPEED_UP_EVERY == 0:
                enemy_speed += 0.8
                speed_flash  = FPS * 2

        if speed_flash > 0:
            speed_flash -= 1

        # Отрисовка
        draw_background(screen)
        for o in road_lines + enemies + coins_list:
            o.draw(screen)
        player.draw(screen)
        draw_hud(screen, score, coins_count, coin_pts, level, enemy_speed)

        # Сообщение об ускорении врагов
        if speed_flash > 0:
            msg = font_medium.render(f"Enemies faster! ({enemy_speed:.1f})", True, ORANGE)
            screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

        pygame.display.flip()


if __name__ == "__main__":
    game_loop()