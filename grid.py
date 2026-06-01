import math
import pygame

CELLS = {
    # row 1 (2 cells)
    (1, -4), (2, -4),
    # row 2 (5 cells)
    (0, -3), (1, -3), (2, -3), (3, -3), (4, -3),
    # row 3 (7 cells)
    (-2, -2), (-1, -2), (0, -2), (1, -2), (2, -2), (3, -2), (4, -2),
    # row 4 (7 cells)
    (-3, -1), (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1), (3, -1),
    # row 5 (7 cells)
    (-3, 0), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (3, 0),
    # row 6 (7 cells)
    (-3, 1), (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1), (3, 1),
    # row 7 (7 cells)
    (-4, 2), (-3, 2), (-2, 2), (-1, 2), (0, 2), (1, 2), (2, 2),
    # row 8 (5 cells)
    (-4, 3), (-3, 3), (-2, 3), (-1, 3), (0, 3),
    # row 9 (2 cells)
    (-2, 4), (-1, 4),
}

SIZE = 55  # hex circumradius in pixels

SUBGRIDS = {
    (0, 0):   {(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1)},
    (1, -3):  {(1,-3),(2,-3),(0,-3),(1,-2),(1,-4),(2,-4),(0,-2)},
    (3, -2):  {(3,-2),(4,-2),(2,-2),(3,-1),(3,-3),(4,-3),(2,-1)},
    (2, 1):   {(2,1),(3,1),(1,1),(2,2),(2,0),(3,0),(1,2)},
    (-1, 3):  {(-1,3),(0,3),(-2,3),(-1,4),(-1,2),(0,2),(-2,4)},
    (-3, 2):  {(-3,2),(-2,2),(-4,2),(-3,3),(-3,1),(-2,1),(-4,3)},
    (-2, -1): {(-2,-1),(-1,-1),(-3,-1),(-2,0),(-2,-2),(-1,-2),(-3,0)},
}

CELL_TO_SUBGRID = {cell: center for center, cells in SUBGRIDS.items() for cell in cells}

def hex_to_pixel(q, r, cx, cy):
    x = cx + (q + r / 2) * math.sqrt(3) * SIZE
    y = cy + r * 1.5 * SIZE
    return (x, y)

def pixel_to_hex(x, y, cx, cy):
    fr = (y - cy) / (1.5 * SIZE)
    fq = (x - cx) / (math.sqrt(3) * SIZE) - fr / 2
    fx, fz = fq, fr
    fy = -fx - fz
    rx, ry, rz = round(fx), round(fy), round(fz)
    dx, dy, dz = abs(rx - fx), abs(ry - fy), abs(rz - fz)
    if dx > dy and dx > dz:
        rx = -ry - rz
    elif dy > dz:
        ry = -rx - rz
    else:
        rz = -rx - ry
    return (rx, rz)

def draw_hex(surface, center, radius, color, width=0):
    cx, cy = center
    points = [
        (cx + radius * math.cos(math.radians(a)),
         cy + radius * math.sin(math.radians(a)))
        for a in range(-90, 270, 60)
    ]
    pygame.draw.polygon(surface, color, points, width)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    pygame.display.set_caption("Dunjoku")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 44)

    cx, cy = 500, 500
    selected = None
    selected_subgrid = set()
    error_subgrid = set()
    cell_values = {}

    # Number picker: 7 boxes on the left
    NUM_X, NUM_Y0, NUM_GAP = 80, 330, 55
    num_rects = [pygame.Rect(NUM_X - 22, NUM_Y0 + i * NUM_GAP - 22, 44, 44) for i in range(7)]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check number picker first
                placed = False
                for i, rect in enumerate(num_rects):
                    if rect.collidepoint(event.pos) and selected is not None:
                        value = i + 1
                        cell_values[selected] = value
                        subgrid = SUBGRIDS.get(CELL_TO_SUBGRID.get(selected), set())
                        values_in_subgrid = [cell_values[c] for c in subgrid if c in cell_values]
                        error_subgrid = subgrid if len(values_in_subgrid) != len(set(values_in_subgrid)) else set()
                        placed = True
                        break
                if not placed:
                    clicked = pixel_to_hex(*event.pos, cx, cy)
                    if clicked in CELLS:
                        selected = None if clicked == selected else clicked
                    else:
                        selected = None
                    selected_subgrid = SUBGRIDS.get(CELL_TO_SUBGRID.get(selected), set())

        screen.fill((255, 255, 255))

        # Draw number picker
        for i, rect in enumerate(num_rects):
            pygame.draw.rect(screen, (230, 230, 230), rect, border_radius=6)
            pygame.draw.rect(screen, (0, 0, 0), rect, width=2, border_radius=6)
            label = font.render(str(i + 1), True, (0, 0, 0))
            screen.blit(label, label.get_rect(center=rect.center))

        # Draw grid
        for q, r in CELLS:
            center = hex_to_pixel(q, r, cx, cy)
            if (q, r) == selected:
                fill = (173, 216, 230)
            elif (q, r) in SUBGRIDS:
                fill = (255, 220, 100)
            else:
                fill = (255, 255, 255)
            draw_hex(screen, center, SIZE - 2, fill)
            draw_hex(screen, center, SIZE - 2, (0, 0, 0), width=2)
            if (q, r) in error_subgrid:
                draw_hex(screen, center, SIZE - 2, (220, 50, 50), width=3)
            elif (q, r) in selected_subgrid:
                draw_hex(screen, center, SIZE - 2, (100, 149, 237), width=3)
            if (q, r) in cell_values:
                label = font.render(str(cell_values[(q, r)]), True, (0, 0, 0))
                screen.blit(label, label.get_rect(center=(int(center[0]), int(center[1]))))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
