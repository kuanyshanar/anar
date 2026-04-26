import pygame
import math
import sys

pygame.init()

# Константы
SCREEN_W  = 980
SCREEN_H  = 660
TOOLBAR_W = 175        # ширина левой панели инструментов

CANVAS_X  = TOOLBAR_W
CANVAS_W  = SCREEN_W - TOOLBAR_W
CANVAS_H  = SCREEN_H

BG_CANVAS  = (255, 255, 255)
BG_PANEL   = (28,  34,  46)
HIGHLIGHT  = (80, 130, 220)
TEXT_COLOR = (210, 215, 230)
DIVIDER    = (50,  58,  76)

ERASER_R   = 22   # радиус ластика

# Все инструменты
TOOLS = [
    "Pencil", "Line",
    "Rectangle", "Square",
    "Circle",
    "Right Triangle", "Equil. Triangle",
    "Rhombus",
    "Eraser",
]

# Иконки инструментов
ICONS = {
    "Pencil":          "✏",
    "Line":            "╱",
    "Rectangle":       "▭",
    "Square":          "■",
    "Circle":          "○",
    "Right Triangle":  "◺",
    "Equil. Triangle": "△",
    "Rhombus":         "◇",
    "Eraser":          "⌫",
}

# Палитра цветов
PALETTE = [
    (0, 0, 0),    (80, 80, 80),   (160, 160, 160), (255, 255, 255),
    (255, 0, 0),  (180, 0, 0),   (255, 100, 0),   (200, 60, 0),
    (255, 200, 0),(180, 140, 0), (0, 200, 0),     (0, 120, 0),
    (0, 200, 200),(0, 100, 160), (0, 0, 255),     (0, 0, 140),
    (180, 0, 180),(100, 0, 120), (255, 150, 200), (150, 80, 40),
]

# Создание окна
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint")
clock  = pygame.time.Clock()

font_tool  = pygame.font.SysFont("Arial", 15, bold=True)
font_label = pygame.font.SysFont("Arial", 12)

# Постоянный холст, сохраняет всё нарисованное
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(BG_CANVAS)


# Геометрические вычисления

def rect_from_points(p1, p2):
    """Возвращает (x, y, w, h) по двум угловым точкам."""
    x = min(p1[0], p2[0])
    y = min(p1[1], p2[1])
    w = abs(p2[0] - p1[0])
    h = abs(p2[1] - p1[1])
    return x, y, w, h


def square_points(p1, p2):
    """
    Квадрат: сторона = min(|dx|, |dy|), знак направления сохраняется.
    Возвращает (x, y, w, h) квадрата.
    """
    dx   = p2[0] - p1[0]
    dy   = p2[1] - p1[1]
    side = min(abs(dx), abs(dy))
    sx   = p1[0] + (side if dx >= 0 else -side)
    sy   = p1[1] + (side if dy >= 0 else -side)
    return rect_from_points(p1, (sx, sy))


def right_triangle_points(p1, p2):
    """
    Прямоугольный треугольник с прямым углом в p1 (левый нижний угол).
    Вершины: p1, (p2.x, p1.y), (p1.x, p2.y).
    """
    return [p1, (p2[0], p1[1]), (p1[0], p2[1])]


def equilateral_triangle_points(p1, p2):
    """
    Равносторонний треугольник.
    Основание — горизонталь от p1 до p2, третья вершина выше по центру.
    Высота считается по формуле h = side * sqrt(3) / 2.
    """
    bx1, by = p1
    bx2     = p2[0]
    side    = abs(bx2 - bx1)
    h       = int(side * math.sqrt(3) / 2)
    mid_x   = (bx1 + bx2) // 2
    top_y   = by - h
    return [(bx1, by), (bx2, by), (mid_x, top_y)]


def rhombus_points(p1, p2):
    """
    Ромб задаётся двумя противоположными угловыми точками.
    Возвращает четыре вершины: верхняя, правая, нижняя, левая.
    """
    cx = (p1[0] + p2[0]) // 2
    cy = (p1[1] + p2[1]) // 2
    return [
        (cx, p1[1]),    # верхняя вершина
        (p2[0], cy),    # правая вершина
        (cx, p2[1]),    # нижняя вершина
        (p1[0], cy),    # левая вершина
    ]


# Отрисовка фигур

def draw_shape(surface, tool, start, end, color, size):
    """
    Рисует выбранную фигуру на поверхности surface.
    Используется и для превью, и для сохранения на холст.
    """
    if tool == "Line":
        pygame.draw.line(surface, color, start, end, size)

    elif tool == "Rectangle":
        x, y, w, h = rect_from_points(start, end)
        if w > 0 and h > 0:
            pygame.draw.rect(surface, color, (x, y, w, h), size)

    elif tool == "Square":
        # Квадрат: берём меньшую сторону
        x, y, w, h = square_points(start, end)
        if w > 0 and h > 0:
            pygame.draw.rect(surface, color, (x, y, w, h), size)

    elif tool == "Circle":
        x, y, w, h = rect_from_points(start, end)
        if w > 0 and h > 0:
            pygame.draw.ellipse(surface, color, (x, y, w, h), size)

    elif tool == "Right Triangle":
        # Прямоугольный треугольник: прямой угол в точке start
        pts = right_triangle_points(start, end)
        pygame.draw.polygon(surface, color, pts, size)

    elif tool == "Equil. Triangle":
        # Равносторонний треугольник: основание по горизонтали
        pts = equilateral_triangle_points(start, end)
        pygame.draw.polygon(surface, color, pts, size)

    elif tool == "Rhombus":
        # Ромб по двум противоположным точкам
        pts = rhombus_points(start, end)
        pygame.draw.polygon(surface, color, pts, size)


# Интерфейс (панель инструментов)

def draw_toolbar(surface, active_tool, draw_color, brush_size):
    """
    Рисует левую панель: кнопки инструментов,
    слайдер размера кисти, палитру и текущий цвет.
    """
    pygame.draw.rect(surface, BG_PANEL, (0, 0, TOOLBAR_W, SCREEN_H))
    pygame.draw.line(surface, DIVIDER, (TOOLBAR_W - 1, 0), (TOOLBAR_W - 1, SCREEN_H), 2)

    y = 10
    # Заголовок
    surface.blit(font_tool.render("Paint", True, HIGHLIGHT), (10, y))
    y += 26
    pygame.draw.line(surface, DIVIDER, (8, y), (TOOLBAR_W - 8, y))
    y += 8

    # Кнопки инструментов
    for tool in TOOLS:
        btn = pygame.Rect(8, y, TOOLBAR_W - 16, 30)
        bg  = HIGHLIGHT if tool == active_tool else (46, 54, 72)
        pygame.draw.rect(surface, bg, btn, border_radius=5)
        lbl = font_tool.render(f"{ICONS[tool]} {tool}", True, TEXT_COLOR)
        surface.blit(lbl, (btn.x + 8, btn.y + 6))
        y += 36

    y += 4
    pygame.draw.line(surface, DIVIDER, (8, y), (TOOLBAR_W - 8, y))
    y += 8

    # Размер кисти
    surface.blit(font_label.render(f"Size: {brush_size}px", True, TEXT_COLOR), (10, y))
    y += 16
    bar_w  = TOOLBAR_W - 20
    filled = int(bar_w * (brush_size - 1) / 29)   # диапазон 1..30
    pygame.draw.rect(surface, (46, 54, 72), (10, y, bar_w, 9), border_radius=4)
    pygame.draw.rect(surface, HIGHLIGHT,   (10, y, filled, 9), border_radius=4)
    y += 14
    surface.blit(font_label.render("[ + ] / [ - ]", True, (120, 130, 150)), (10, y))
    y += 22

    pygame.draw.line(surface, DIVIDER, (8, y), (TOOLBAR_W - 8, y))
    y += 8

    # Палитра цветов
    surface.blit(font_label.render("Colors:", True, TEXT_COLOR), (10, y))
    y += 16
    cols = 4
    csz  = 26
    for i, color in enumerate(PALETTE):
        col = i % cols
        row = i // cols
        rx  = 10 + col * (csz + 3)
        ry  = y  + row * (csz + 3)
        r   = pygame.Rect(rx, ry, csz, csz)
        pygame.draw.rect(surface, color, r, border_radius=4)
        # Белая рамка вокруг активного цвета
        if color == draw_color:
            pygame.draw.rect(surface, (255, 255, 255), r, 2, border_radius=4)

    y += ((len(PALETTE) - 1) // cols + 1) * (csz + 3) + 8
    pygame.draw.line(surface, DIVIDER, (8, y), (TOOLBAR_W - 8, y))
    y += 8

    # Текущий цвет
    surface.blit(font_label.render("Current:", True, TEXT_COLOR), (10, y))
    y += 16
    pygame.draw.rect(surface, draw_color,      (10, y, 50, 24), border_radius=5)
    pygame.draw.rect(surface, (200, 200, 200), (10, y, 50, 24), 2, border_radius=5)

    # Подсказка очистки холста
    surface.blit(font_label.render("[ C ] Clear", True, (180, 80, 80)), (10, SCREEN_H - 22))


def get_tool_at(mx, my):
    """Возвращает инструмент по клику на панели, или None."""
    y = 44   # стартовый Y первой кнопки
    for tool in TOOLS:
        btn = pygame.Rect(8, y, TOOLBAR_W - 16, 30)
        if btn.collidepoint(mx, my):
            return tool
        y += 36
    return None


def get_palette_color(mx, my):
    """Возвращает цвет из палитры по клику, или None."""
    y_start = 44 + len(TOOLS) * 36 + 74   # смещение палитры в панели
    csz     = 26
    cols    = 4
    for i, color in enumerate(PALETTE):
        col = i % cols
        row = i // cols
        rx  = 10 + col * (csz + 3)
        ry  = y_start + row * (csz + 3)
        if pygame.Rect(rx, ry, csz, csz).collidepoint(mx, my):
            return color
    return None


def canvas_pos(mx, my):
    """Переводит экранные координаты мыши в координаты холста."""
    return mx - CANVAS_X, my


# Главный цикл

def main():
    active_tool = "Pencil"
    draw_color  = (0, 0, 0)
    brush_size  = 3

    drawing   = False
    start_pos = None
    prev_pos  = None

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Клавиатура
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                    brush_size = min(brush_size + 1, 30)
                if event.key == pygame.K_MINUS:
                    brush_size = max(brush_size - 1, 1)
                if event.key == pygame.K_c:
                    canvas.fill(BG_CANVAS)   # очистить холст
                # Быстрый выбор инструмента клавишами 1..9
                for i, t in enumerate(TOOLS[:9], start=1):
                    if event.key == getattr(pygame, f"K_{i}", None):
                        active_tool = t

            # Нажатие мыши
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if mx < TOOLBAR_W:
                    # Клик по панели инструментов
                    t = get_tool_at(mx, my)
                    if t:
                        active_tool = t
                    c = get_palette_color(mx, my)
                    if c:
                        draw_color = c
                else:
                    # Начало рисования на холсте
                    drawing   = True
                    cx, cy    = canvas_pos(mx, my)
                    start_pos = (cx, cy)
                    prev_pos  = (cx, cy)

            # Отпускание мыши
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and start_pos:
                    cx, cy  = canvas_pos(mx, my)
                    # Сохраняем фигуру на холст (карандаш и ластик рисуют сразу)
                    if active_tool not in ("Pencil", "Eraser"):
                        draw_shape(canvas, active_tool, start_pos, (cx, cy), draw_color, brush_size)
                drawing   = False
                start_pos = None
                prev_pos  = None

            # Движение мыши с зажатой кнопкой
            if event.type == pygame.MOUSEMOTION and drawing:
                cx, cy = canvas_pos(mx, my)

                if active_tool == "Pencil":
                    # Непрерывная линия от предыдущей точки к текущей
                    if prev_pos:
                        pygame.draw.line(canvas, draw_color, prev_pos, (cx, cy), brush_size)
                    prev_pos = (cx, cy)

                elif active_tool == "Eraser":
                    # Ластик — рисуем белым кружком
                    pygame.draw.circle(canvas, BG_CANVAS, (cx, cy), ERASER_R)

        # Отрисовка кадра
        screen.blit(canvas, (CANVAS_X, 0))

        # Превью фигуры поверх холста пока кнопка зажата
        if drawing and start_pos and active_tool not in ("Pencil", "Eraser"):
            cx, cy  = canvas_pos(mx, my)
            preview = canvas.copy()   # временная копия, чтобы превью не накапливалось
            draw_shape(preview, active_tool, start_pos, (cx, cy), draw_color, brush_size)
            screen.blit(preview, (CANVAS_X, 0))

        # Курсор ластика
        if active_tool == "Eraser" and mx >= CANVAS_X:
            pygame.draw.circle(screen, (180, 180, 180), (mx, my), ERASER_R, 2)

        # Панель инструментов поверх всего
        draw_toolbar(screen, active_tool, draw_color, brush_size)

        pygame.display.flip()


if __name__ == "__main__":
    main()