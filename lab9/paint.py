import pygame
import sys
pygame.init()
SCREEN_W    = 900
SCREEN_H    = 650
TOOLBAR_W   = 160          

CANVAS_X    = TOOLBAR_W    
CANVAS_W    = SCREEN_W - TOOLBAR_W
CANVAS_H    = SCREEN_H

BG_CANVAS   = (255, 255, 255)   # белый фон 
BG_PANEL    = (30,  35,  45)    # тёмный фон 
HIGHLIGHT   = (90, 140, 220)    # выделение активного инструмента
TEXT_COLOR  = (210, 215, 230)
DIVIDER     = (55,  62,  78)

ERASER_SIZE = 24    # размер ластика в пикселях


TOOLS = ["Pencil", "Line", "Rectangle", "Circle", "Eraser"]

# Палитра 
PALETTE = [
    (0,   0,   0),    (80,  80,  80),   (160, 160, 160),  (255, 255, 255),
    (255,   0,   0),  (180,   0,   0),  (255, 100,   0),  (200,  60,   0),
    (255, 200,   0),  (180, 140,   0),  (0,  200,   0),   (0,  120,   0),
    (0,  200, 200),   (0,  100, 160),   (0,    0, 255),   (0,    0, 140),
    (180,   0, 180),  (100,   0, 120),  (255, 150, 200),  (150,  80,  40),
]

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint 🎨")
clock  = pygame.time.Clock()

# Шрифтар
font_tool  = pygame.font.SysFont("Arial", 16, bold=True)
font_label = pygame.font.SysFont("Arial", 13)

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(BG_CANVAS)


def canvas_pos(mx, my):
    """Переводит экранные координаты мыши в координаты холста."""
    return mx - CANVAS_X, my


def draw_toolbar(surface, active_tool, draw_color, brush_size):
    """
    Рисует левую панель:
    кнопки инструментов, палитру, слайдер размера кисти.
    """
    pygame.draw.rect(surface, BG_PANEL, (0, 0, TOOLBAR_W, SCREEN_H))
    pygame.draw.line(surface, DIVIDER, (TOOLBAR_W - 1, 0), (TOOLBAR_W - 1, SCREEN_H), 2)

    y = 12

    
    title = font_tool.render("🎨  Paint", True, HIGHLIGHT)
    surface.blit(title, (10, y))
    y += 30
    pygame.draw.line(surface, DIVIDER, (8, y), (TOOLBAR_W - 8, y))
    y += 10

    # Кнопки
    icons = {"Pencil": "✏", "Line": "╱", "Rectangle": "▭",
             "Circle": "○", "Eraser": "⌫"}

    for tool in TOOLS:
        btn_rect = pygame.Rect(8, y, TOOLBAR_W - 16, 34)

        
        if tool == active_tool:
            pygame.draw.rect(surface, HIGHLIGHT, btn_rect, border_radius=6)
        else:
            pygame.draw.rect(surface, (50, 58, 75), btn_rect, border_radius=6)

        label = font_tool.render(f"{icons[tool]}  {tool}", True, TEXT_COLOR)
        surface.blit(label, (btn_rect.x + 10, btn_rect.y + 8))
        y += 42

    y += 6
    pygame.draw.line(surface, DIVIDER, (8, y), (TOOLBAR_W - 8, y))
    y += 10

    # Размер кисти 
    sz_label = font_label.render(f"Size: {brush_size}px", True, TEXT_COLOR)
    surface.blit(sz_label, (10, y))
    y += 20

    
    bar_w = TOOLBAR_W - 20
    filled = int(bar_w * (brush_size - 1) / 29)   # диапазон 1–30
    pygame.draw.rect(surface, (50, 58, 75), (10, y, bar_w, 10), border_radius=5)
    pygame.draw.rect(surface, HIGHLIGHT,    (10, y, filled, 10), border_radius=5)
    y += 20

    hint = font_label.render("[ + ] / [ - ]", True, (120, 130, 150))
    surface.blit(hint, (10, y))
    y += 28

    pygame.draw.line(surface, DIVIDER, (8, y), (TOOLBAR_W - 8, y))
    y += 10

    # Палитра цветов 
    pal_label = font_label.render("Colors:", True, TEXT_COLOR)
    surface.blit(pal_label, (10, y))
    y += 18

    cell_size = 28
    cols = 4
    for i, color in enumerate(PALETTE):
        col = i % cols
        row = i // cols
        cx  = 10 + col * (cell_size + 3)
        cy  = y  + row * (cell_size + 3)
        r   = pygame.Rect(cx, cy, cell_size, cell_size)
        pygame.draw.rect(surface, color, r, border_radius=4)
        
        if color == draw_color:
            pygame.draw.rect(surface, WHITE := (255, 255, 255), r, 2, border_radius=4)

    y += ((len(PALETTE) - 1) // cols + 1) * (cell_size + 3) + 8
    pygame.draw.line(surface, DIVIDER, (8, y), (TOOLBAR_W - 8, y))
    y += 10

    #Текущий цвет 
    cur_label = font_label.render("Current:", True, TEXT_COLOR)
    surface.blit(cur_label, (10, y))
    y += 18
    pygame.draw.rect(surface, draw_color,       (10, y, 50, 26), border_radius=5)
    pygame.draw.rect(surface, (200, 200, 200),  (10, y, 50, 26), 2, border_radius=5)

    # очистить
    clr = font_label.render("[ C ] Clear", True, (160, 100, 100))
    surface.blit(clr, (10, SCREEN_H - 24))


def get_tool_at(mx, my):
    """Возвращает инструмент, на кнопку которого кликнули, или None."""
    y = 62   
    for tool in TOOLS:
        btn_rect = pygame.Rect(8, y, TOOLBAR_W - 16, 34)
        if btn_rect.collidepoint(mx, my):
            return tool
        y += 42
    return None


def get_palette_color(mx, my):
    """Возвращает цвет из палитры, на который кликнули, или None."""
    y_start  = 62 + len(TOOLS) * 42 + 80   
    
    cell_size = 28
    cols      = 4

    for i, color in enumerate(PALETTE):
        col = i % cols
        row = i // cols
        cx  = 10 + col * (cell_size + 3)
        cy  = y_start + row * (cell_size + 3)
        r   = pygame.Rect(cx, cy, cell_size, cell_size)
        if r.collidepoint(mx, my):
            return color
    return None


def draw_preview(surface, tool, start, end, color, size):
    """
    Рисует превью фигуры поверх холста пока кнопка мыши зажата.
    Не сохраняется на canvas — только визуал.
    """
    if tool == "Line":
        pygame.draw.line(surface, color, start, end, size)

    elif tool == "Rectangle":
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        if w > 0 and h > 0:
            pygame.draw.rect(surface, color, (x, y, w, h), size)

    elif tool == "Circle":
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        rx = abs(end[0] - start[0]) // 2
        ry = abs(end[1] - start[1]) // 2
        if rx > 0 and ry > 0:
            r = pygame.Rect(min(start[0], end[0]),
                            min(start[1], end[1]),
                            rx * 2, ry * 2)
            pygame.draw.ellipse(surface, color, r, size)


def commit_shape(canvas_surf, tool, start, end, color, size):
    """Сохраняет нарисованную фигуру на постоянный холст canvas."""
    if tool == "Line":
        pygame.draw.line(canvas_surf, color, start, end, size)

    elif tool == "Rectangle":
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        if w > 0 and h > 0:
            pygame.draw.rect(canvas_surf, color, (x, y, w, h), size)

    elif tool == "Circle":
        rx = abs(end[0] - start[0]) // 2
        ry = abs(end[1] - start[1]) // 2
        if rx > 0 and ry > 0:
            r = pygame.Rect(min(start[0], end[0]),
                            min(start[1], end[1]),
                            rx * 2, ry * 2)
            pygame.draw.ellipse(canvas_surf, color, r, size)


def main():
    active_tool  = "Pencil"
    draw_color   = (0, 0, 0)
    brush_size   = 4

    drawing      = False   
    start_pos    = None     
    prev_pos     = None     

    while True:
        clock.tick(60)

        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            
            if event.type == pygame.KEYDOWN:
                # Размер кисти
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    brush_size = min(brush_size + 1, 30)
                if event.key == pygame.K_MINUS:
                    brush_size = max(brush_size - 1, 1)
                # Очистить холст
                if event.key == pygame.K_c:
                    canvas.fill(BG_CANVAS)
                
                for i, t in enumerate(TOOLS, start=1):
                    if event.key == getattr(pygame, f"K_{i}"):
                        active_tool = t


            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                if mx < TOOLBAR_W:
                    tool = get_tool_at(mx, my)
                    if tool:
                        active_tool = tool
                    color = get_palette_color(mx, my)
                    if color:
                        draw_color = color
                else:

                    drawing   = True
                    cx, cy    = canvas_pos(mx, my)
                    start_pos = (cx, cy)
                    prev_pos  = (cx, cy)


            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and start_pos is not None:
                    cx, cy  = canvas_pos(mx, my)
                    end_pos = (cx, cy)

   
                    if active_tool in ("Rectangle", "Circle", "Line"):
                        commit_shape(canvas, active_tool,
                                     start_pos, end_pos, draw_color, brush_size)

                drawing   = False
                start_pos = None
                prev_pos  = None


            if event.type == pygame.MOUSEMOTION and drawing:
                cx, cy = canvas_pos(mx, my)

                if active_tool == "Pencil":
                    
                    if prev_pos:
                        pygame.draw.line(canvas, draw_color,
                                         prev_pos, (cx, cy), brush_size)
                    prev_pos = (cx, cy)

                elif active_tool == "Eraser":
                    # Ластик
                    pygame.draw.circle(canvas, BG_CANVAS,
                                       (cx, cy), ERASER_SIZE)
        screen.blit(canvas, (CANVAS_X, 0))


        if drawing and start_pos and active_tool in ("Line", "Rectangle", "Circle"):
            cx, cy   = canvas_pos(mx, my)

            preview = canvas.copy()
            draw_preview(preview, active_tool,
                         start_pos, (cx, cy), draw_color, brush_size)
            screen.blit(preview, (CANVAS_X, 0))

        # ластик
        if active_tool == "Eraser" and mx >= CANVAS_X:
            pygame.draw.circle(screen, (180, 180, 180), (mx, my), ERASER_SIZE, 2)

        draw_toolbar(screen, active_tool, draw_color, brush_size)

        pygame.display.flip()
if __name__ == "__main__":
    main()