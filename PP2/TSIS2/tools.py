import pygame
import math
from datetime import datetime

def draw_shape(surface, tool, start, end, color, size, fill=False):
    
#Рисует геометрическую фигуру на поверхности.
    
    
    if tool == "rect":
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        if w > 0 and h > 0:
            if fill:
                pygame.draw.rect(surface, color, (x, y, w, h))
            else:
                pygame.draw.rect(surface, color, (x, y, w, h), size)
    
    elif tool == "circle":
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        if w > 0 and h > 0:
            if fill:
                pygame.draw.ellipse(surface, color, (x, y, w, h))
            else:
                pygame.draw.ellipse(surface, color, (x, y, w, h), size)
    
    elif tool == "square":
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        side = min(abs(dx), abs(dy))
        sx = start[0] + (side if dx >= 0 else -side)
        sy = start[1] + (side if dy >= 0 else -side)
        x = min(start[0], sx)
        y = min(start[1], sy)
        w = abs(sx - start[0])
        h = abs(sy - start[1])
        if w > 0 and h > 0:
            if fill:
                pygame.draw.rect(surface, color, (x, y, w, h))
            else:
                pygame.draw.rect(surface, color, (x, y, w, h), size)
    
    elif tool == "right_triangle":
        points = [start, (end[0], start[1]), (start[0], end[1])]
        if fill:
            pygame.draw.polygon(surface, color, points)
        else:
            pygame.draw.polygon(surface, color, points, size)
    
    elif tool == "eq_triangle":
        bx1, by = start
        bx2 = end[0]
        side = abs(bx2 - bx1)
        h = int(side * math.sqrt(3) / 2)
        mid_x = (bx1 + bx2) // 2
# Определяем направление (вверх или вниз)
        if end[1] < start[1]:
            top_y = start[1] - h
        else:
            top_y = start[1] + h
        points = [(bx1, by), (bx2, by), (mid_x, top_y)]
        if fill:
            pygame.draw.polygon(surface, color, points)
        else:
            pygame.draw.polygon(surface, color, points, size)
    
    elif tool == "rhombus":
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        points = [
            (cx, start[1]),    # верхняя
            (end[0], cy),      # правая
            (cx, end[1]),      # нижняя
            (start[0], cy)     # левая
        ]
        if fill:
            pygame.draw.polygon(surface, color, points)
        else:
            pygame.draw.polygon(surface, color, points, size)


def flood_fill(surface, pos, target_color, replacement_color):
    """
    Заливка  цветом 
    """
    if target_color == replacement_color:
        return
    
    width, height = surface.get_size()
    
    if pos[0] < 0 or pos[0] >= width or pos[1] < 0 or pos[1] >= height:
        return
    
    try:
        if surface.get_at(pos)[:3] != target_color:
            return
    except IndexError:
        return
    
    stack = [pos]
    visited = set()
    
    while stack:
        x, y = stack.pop()
        
        if (x, y) in visited:
            continue
        
        if x < 0 or x >= width or y < 0 or y >= height:
            continue
        
        try:
            if surface.get_at((x, y))[:3] != target_color:
                continue
        except IndexError:
            continue
        
        visited.add((x, y))
        surface.set_at((x, y), replacement_color)
        
        stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])


def save_canvas(canvas):
    """Сохраняет холст с временной меткой."""
    filename = datetime.now().strftime("paint_%Y%m%d_%H%M%S.png")
    pygame.image.save(canvas, filename)
    return filename


def get_snapped_position(start, end, tool, snap_mode="square"):
    
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    
    if snap_mode == "square":
        if tool in ["square", "circle"]:
# Квадрат/круг: все стороны равны (по минимальной стороне)
            side = min(abs(dx), abs(dy))
            new_end = (
                start[0] + (side if dx >= 0 else -side),
                start[1] + (side if dy >= 0 else -side)
            )
            return new_end
        
        elif tool == "eq_triangle":
# Равносторонний треугольник: ширина = высоте
            side = abs(dx)
            new_end = (
                end[0],
                start[1] + (side if dy >= 0 else -side)
            )
            return new_end
    
    return end


def get_resize_handle(pos, shape_rect, handle_size=10):
    """
    Определяет, за какой манипулятор изменения размера был клик.
    Возвращает строку с направлением или None.
    """
    handles = {
        "top_left": pygame.Rect(shape_rect.x - handle_size//2, shape_rect.y - handle_size//2, handle_size, handle_size),
        "top_right": pygame.Rect(shape_rect.x + shape_rect.w - handle_size//2, shape_rect.y - handle_size//2, handle_size, handle_size),
        "bottom_left": pygame.Rect(shape_rect.x - handle_size//2, shape_rect.y + shape_rect.h - handle_size//2, handle_size, handle_size),
        "bottom_right": pygame.Rect(shape_rect.x + shape_rect.w - handle_size//2, shape_rect.y + shape_rect.h - handle_size//2, handle_size, handle_size),
        "top": pygame.Rect(shape_rect.x + shape_rect.w//2 - handle_size//2, shape_rect.y - handle_size//2, handle_size, handle_size),
        "bottom": pygame.Rect(shape_rect.x + shape_rect.w//2 - handle_size//2, shape_rect.y + shape_rect.h - handle_size//2, handle_size, handle_size),
        "left": pygame.Rect(shape_rect.x - handle_size//2, shape_rect.y + shape_rect.h//2 - handle_size//2, handle_size, handle_size),
        "right": pygame.Rect(shape_rect.x + shape_rect.w - handle_size//2, shape_rect.y + shape_rect.h//2 - handle_size//2, handle_size, handle_size),
    }
    
    for name, rect in handles.items():
        if rect.collidepoint(pos):
            return name
    return None


def resize_shape(shape_rect, handle, mouse_pos, keep_aspect=True, aspect_ratio=1.0):
    """
    Изменяет размер фигуры 
    """
    new_rect = pygame.Rect(shape_rect)
    dx = mouse_pos[0] - shape_rect.centerx
    dy = mouse_pos[1] - shape_rect.centery
    
    if handle == "top_left":
        new_rect.width = shape_rect.width - dx
        new_rect.height = shape_rect.height - dy
        if keep_aspect:
            new_rect.width = new_rect.height = min(new_rect.width, new_rect.height)
        new_rect.x = shape_rect.x + dx
        new_rect.y = shape_rect.y + dy
    
    elif handle == "top_right":
        new_rect.width = shape_rect.width + dx
        new_rect.height = shape_rect.height - dy
        if keep_aspect:
            new_rect.width = new_rect.height = min(new_rect.width, new_rect.height)
        new_rect.y = shape_rect.y + dy
    
    elif handle == "bottom_left":
        new_rect.width = shape_rect.width - dx
        new_rect.height = shape_rect.height + dy
        if keep_aspect:
            new_rect.width = new_rect.height = min(new_rect.width, new_rect.height)
        new_rect.x = shape_rect.x + dx
    
    elif handle == "bottom_right":
        new_rect.width = shape_rect.width + dx
        new_rect.height = shape_rect.height + dy
        if keep_aspect:
            new_rect.width = new_rect.height = min(new_rect.width, new_rect.height)
    
    elif handle == "top":
        new_rect.height = shape_rect.height - dy
        if keep_aspect:
            new_rect.width = new_rect.height
        new_rect.y = shape_rect.y + dy
    
    elif handle == "bottom":
        new_rect.height = shape_rect.height + dy
        if keep_aspect:
            new_rect.width = new_rect.height
    
    elif handle == "left":
        new_rect.width = shape_rect.width - dx
        if keep_aspect:
            new_rect.height = new_rect.width
        new_rect.x = shape_rect.x + dx
    
    elif handle == "right":
        new_rect.width = shape_rect.width + dx
        if keep_aspect:
            new_rect.height = new_rect.width
    
    # Минимальный размер
    if new_rect.width < 5:
        new_rect.width = 5
        new_rect.height = 5 if keep_aspect else new_rect.height
    if new_rect.height < 5:
        new_rect.height = 5
        new_rect.width = 5 if keep_aspect else new_rect.width
    
    return new_rect