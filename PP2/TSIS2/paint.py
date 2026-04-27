import pygame
import math
import sys
from tools import draw_shape, flood_fill, save_canvas, get_snapped_position, get_resize_handle, resize_shape

pygame.init()

# Константы
SCREEN_W = 1200
SCREEN_H = 800
TOOLBAR_W = 200

CANVAS_X = TOOLBAR_W
CANVAS_W = SCREEN_W - TOOLBAR_W
CANVAS_H = SCREEN_H

BG_CANVAS = (255, 255, 255)
BG_PANEL = (30, 30, 35)
HIGHLIGHT = (52, 152, 219)
HOVER = (41, 128, 185)
TEXT_COLOR = (236, 240, 241)
DIVIDER = (50, 50, 60)

# Все инструменты
TOOLS = [
    "Pencil", "Line",
    "Rectangle", "Square",
    "Circle",
    "Right Triangle", "Equil. Triangle",
    "Rhombus",
    "Eraser", "Fill", "Text"
]

# Палитра цветов
PALETTE = [
    (0, 0, 0), (44, 62, 80), (52, 73, 94), (255, 255, 255),
    (231, 76, 60), (230, 126, 34), (241, 196, 15), (46, 204, 113),
    (26, 188, 156), (52, 152, 219), (155, 89, 182), (236, 240, 241),
]

# Создание окна
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint Pro - Snap & Resize")
clock = pygame.time.Clock()

font_tool = pygame.font.SysFont("Segoe UI", 15, bold=True)
font_label = pygame.font.SysFont("Segoe UI", 12)
font_text = pygame.font.SysFont("Segoe UI", 28)

# Холст
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(BG_CANVAS)

# Состояние
active_tool = "Pencil"
draw_color = (0, 0, 0)
brush_size = 3
fill_shape = False
snap_mode = "square"  
selected_shape = None
resizing = False
resize_handle = None
original_rect = None

text_mode = False
text_pos = None
text_input = ""
text_cursor_visible = True
text_cursor_timer = 0

drawing = False
start_pos = None
last_pos = None

# Кнопки
snap_button = pygame.Rect(TOOLBAR_W - 45, SCREEN_H - 80, 40, 30)
clear_button = pygame.Rect(TOOLBAR_W - 45, SCREEN_H - 35, 40, 30)

def draw_toolbar():
    """Рисует левую панель инструментов."""
    pygame.draw.rect(screen, BG_PANEL, (0, 0, TOOLBAR_W, SCREEN_H))
    pygame.draw.line(screen, DIVIDER, (TOOLBAR_W - 1, 0), (TOOLBAR_W - 1, SCREEN_H), 2)
    
    y = 15
    title = font_tool.render("PAINT PRO", True, HIGHLIGHT)
    screen.blit(title, (TOOLBAR_W // 2 - title.get_width() // 2, y))
    y += 35
    pygame.draw.line(screen, DIVIDER, (10, y), (TOOLBAR_W - 10, y), 1)
    y += 12
    
    # Инструменты
    for tool in TOOLS:
        btn = pygame.Rect(10, y, TOOLBAR_W - 20, 32)
        bg = HIGHLIGHT if tool == active_tool else (45, 45, 50)
        pygame.draw.rect(screen, bg, btn, border_radius=6)
        text = font_tool.render(tool[:12], True, TEXT_COLOR)
        screen.blit(text, (btn.x + 10, btn.y + 8))
        y += 36
    
    y += 5
    pygame.draw.line(screen, DIVIDER, (10, y), (TOOLBAR_W - 10, y), 1)
    y += 12
    
    # Размер кисти
    screen.blit(font_label.render(f"Size: {brush_size}px", True, TEXT_COLOR), (10, y))
    y += 18
    bar_w = TOOLBAR_W - 30
    filled = int(bar_w * (brush_size - 1) / 29)
    pygame.draw.rect(screen, (60, 60, 70), (10, y, bar_w, 6), border_radius=3)
    pygame.draw.rect(screen, HIGHLIGHT, (10, y, filled, 6), border_radius=3)
    y += 20
    
    # Кнопки размера
    for i, size in enumerate([2, 5, 10]):
        btn = pygame.Rect(10 + i * 45, y, 35, 25)
        bg = HIGHLIGHT if brush_size == size else (45, 45, 50)
        pygame.draw.rect(screen, bg, btn, border_radius=4)
        text = font_label.render(str(size), True, TEXT_COLOR)
        screen.blit(text, (btn.centerx - text.get_width() // 2, btn.centery - text.get_height() // 2))
    
    y += 35
    pygame.draw.line(screen, DIVIDER, (10, y), (TOOLBAR_W - 10, y), 1)
    y += 12
    
    # Цвета
    screen.blit(font_label.render("COLORS", True, TEXT_COLOR), (10, y))
    y += 20
    cols = 4
    csz = 30
    for i, color in enumerate(PALETTE):
        col = i % cols
        row = i // cols
        x = 10 + col * (csz + 5)
        y_pos = y + row * (csz + 5)
        pygame.draw.rect(screen, color, (x, y_pos, csz, csz), border_radius=4)
        if color == draw_color:
            pygame.draw.rect(screen, (255, 255, 255), (x, y_pos, csz, csz), 2, border_radius=4)
    
    y += ((len(PALETTE) - 1) // cols + 1) * (csz + 5) + 10
    pygame.draw.line(screen, DIVIDER, (10, y), (TOOLBAR_W - 10, y), 1)
    y += 12
    
    # Опции
    fill_btn = pygame.Rect(10, y, TOOLBAR_W - 80, 28)
    fill_bg = HIGHLIGHT if fill_shape else (45, 45, 50)
    pygame.draw.rect(screen, fill_bg, fill_btn, border_radius=5)
    fill_text = font_label.render("Fill Mode", True, TEXT_COLOR)
    screen.blit(fill_text, (fill_btn.x + 8, fill_btn.y + 7))
    
    snap_btn = pygame.Rect(TOOLBAR_W - 60, y, 50, 28)
    snap_bg = HIGHLIGHT if snap_mode == "square" else (45, 45, 50)
    pygame.draw.rect(screen, snap_bg, snap_btn, border_radius=5)
    snap_text = font_label.render("⬚", True, TEXT_COLOR)
    screen.blit(snap_text, (snap_btn.centerx - 8, snap_btn.y + 6))
    
    y += 35
    
    # Кнопка Clear
    pygame.draw.rect(screen, (192, 57, 43), clear_button, border_radius=5)
    clear_text = font_label.render("CLEAR", True, TEXT_COLOR)
    screen.blit(clear_text, (clear_button.centerx - clear_text.get_width() // 2, clear_button.centery - clear_text.get_height() // 2))
    
    
    info_y = SCREEN_H - 22
    info_text = font_label.render("Ctrl+S Save | Snap ON", True, (100, 100, 110))
    screen.blit(info_text, (10, info_y))

def canvas_pos(mx, my):
    return mx - CANVAS_X, my

def main():
    global active_tool, draw_color, brush_size, fill_shape, snap_mode
    global drawing, start_pos, last_pos, text_mode, text_pos, text_input
    global text_cursor_visible, text_cursor_timer, selected_shape, resizing, resize_handle, original_rect
    
    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
        
        if text_mode:
            text_cursor_timer += 1
            if text_cursor_timer >= 30:
                text_cursor_timer = 0
                text_cursor_visible = not text_cursor_visible
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and (pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]):
                    save_canvas(canvas)
                
                if event.key == pygame.K_1:
                    brush_size = 2
                if event.key == pygame.K_2:
                    brush_size = 5
                if event.key == pygame.K_3:
                    brush_size = 10
                
                if event.key == pygame.K_c and not text_mode:
                    canvas.fill(BG_CANVAS)
                
                if text_mode:
                    if event.key == pygame.K_RETURN:
                        if text_input:
                            text_surface = font_text.render(text_input, True, draw_color)
                            canvas.blit(text_surface, text_pos)
                        text_mode = False
                        text_pos = None
                        text_input = ""
                    elif event.key == pygame.K_ESCAPE:
                        text_mode = False
                        text_pos = None
                        text_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text_input = text_input[:-1]
                    elif event.unicode and event.unicode.isprintable():
                        text_input += event.unicode
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
# Проверка клика по панели
                if mx < TOOLBAR_W:
# Проверка кнопок
                    if clear_button.collidepoint(mx, my):
                        canvas.fill(BG_CANVAS)
                        continue
                    
# Проверка кнопок размера
                    y_offset = 44 + len(TOOLS) * 36 + 47
                    for i, size in enumerate([2, 5, 10]):
                        btn = pygame.Rect(10 + i * 45, y_offset, 35, 25)
                        if btn.collidepoint(mx, my):
                            brush_size = size
                            continue
                    
# Проверка кнопок опций
                    options_y = y_offset + 50
                    fill_btn = pygame.Rect(10, options_y, TOOLBAR_W - 80, 28)
                    if fill_btn.collidepoint(mx, my):
                        fill_shape = not fill_shape
                        continue
                    
                    snap_btn = pygame.Rect(TOOLBAR_W - 60, options_y, 50, 28)
                    if snap_btn.collidepoint(mx, my):
                        snap_mode = "free" if snap_mode == "square" else "square"
                        continue
                    
# Проверка инструментов
                    y = 44
                    for tool in TOOLS:
                        btn = pygame.Rect(10, y, TOOLBAR_W - 20, 32)
                        if btn.collidepoint(mx, my):
                            active_tool = tool
                            text_mode = False
                            break
                        y += 36
                    
# Проверка цветов
                    colors_y = options_y + 50
                    cols = 4
                    csz = 30
                    for i, color in enumerate(PALETTE):
                        col = i % cols
                        row = i // cols
                        x = 10 + col * (csz + 5)
                        y_pos = colors_y + row * (csz + 5)
                        if pygame.Rect(x, y_pos, csz, csz).collidepoint(mx, my):
                            draw_color = color
                            break
                
                else:
                    cx, cy = canvas_pos(mx, my)
                    if 0 <= cx < CANVAS_W and 0 <= cy < CANVAS_H:
                        
                        if active_tool == "Fill":
                            target_color = canvas.get_at((cx, cy))[:3]
                            if target_color != draw_color:
                                flood_fill(canvas, (cx, cy), target_color, draw_color)
                        
                        elif active_tool == "Text":
                            text_mode = True
                            text_pos = (cx, cy)
                            text_input = ""
                            text_cursor_visible = True
                            text_cursor_timer = 0
                        
                        else:
                            drawing = True
                            start_pos = (cx, cy)
                            last_pos = (cx, cy)
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and start_pos:
                    cx, cy = canvas_pos(mx, my)
                    if 0 <= cx < CANVAS_W and 0 <= cy < CANVAS_H:
                        end_pos = (cx, cy)
                        
# Применяем Snap для ровных фигур
                        if snap_mode == "square" and active_tool in ["Square", "Circle", "Equil. Triangle"]:
                            end_pos = get_snapped_position(start_pos, end_pos, active_tool.lower(), snap_mode)
                        
                        tool_map = {
                            "Rectangle": "rect",
                            "Circle": "circle",
                            "Square": "square",
                            "Right Triangle": "right_triangle",
                            "Equil. Triangle": "eq_triangle",
                            "Rhombus": "rhombus"
                        }
                        
                        if active_tool in tool_map:
                            draw_shape(canvas, tool_map[active_tool], start_pos, end_pos, draw_color, brush_size, fill_shape)
                        elif active_tool == "Line":
                            pygame.draw.line(canvas, draw_color, start_pos, end_pos, brush_size)
                
                drawing = False
                start_pos = None
                last_pos = None
                resizing = False
            
            if event.type == pygame.MOUSEMOTION and drawing and not resizing:
                cx, cy = canvas_pos(mx, my)
                if 0 <= cx < CANVAS_W and 0 <= cy < CANVAS_H:
                    if active_tool == "Pencil":
                        if last_pos:
                            pygame.draw.line(canvas, draw_color, last_pos, (cx, cy), brush_size)
                        last_pos = (cx, cy)
                    elif active_tool == "Eraser":
                        pygame.draw.circle(canvas, BG_CANVAS, (cx, cy), brush_size + 4)
        
# Отрисовка
        screen.fill(BG_PANEL)
        screen.blit(canvas, (CANVAS_X, 0))
        
# Превью фигуры с Snap
        if drawing and start_pos and active_tool not in ["Pencil", "Eraser", "Fill", "Text"]:
            cx, cy = canvas_pos(mx, my)
            if 0 <= cx < CANVAS_W and 0 <= cy < CANVAS_H:
                preview = canvas.copy()
                end_pos = (cx, cy)
                
                if snap_mode == "square" and active_tool in ["Square", "Circle", "Equil. Triangle"]:
                    end_pos = get_snapped_position(start_pos, end_pos, active_tool.lower(), snap_mode)
                
                tool_map = {
                    "Rectangle": "rect",
                    "Circle": "circle",
                    "Square": "square",
                    "Right Triangle": "right_triangle",
                    "Equil. Triangle": "eq_triangle",
                    "Rhombus": "rhombus"
                }
                
                if active_tool in tool_map:
                    draw_shape(preview, tool_map[active_tool], start_pos, end_pos, draw_color, brush_size, fill_shape)
                elif active_tool == "Line":
                    pygame.draw.line(preview, draw_color, start_pos, end_pos, brush_size)
                
                screen.blit(preview, (CANVAS_X, 0))
        
# Превью текста
        if text_mode and text_pos:
            preview_text = text_input + ("|" if text_cursor_visible else "")
            text_surface = font_text.render(preview_text, True, draw_color)
            screen.blit(text_surface, (text_pos[0] + CANVAS_X, text_pos[1]))
        
        # Курсор
        if mx >= CANVAS_X:
            if active_tool == "Eraser":
                pygame.draw.circle(screen, (180, 180, 180), (mx, my), brush_size + 4, 2)
            elif active_tool == "Pencil":
                pygame.draw.circle(screen, draw_color, (mx, my), max(3, brush_size // 2 + 2))
        
        draw_toolbar()
        pygame.display.flip()

if __name__ == "__main__":
    main()