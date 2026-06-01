import math
import random
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

def _build_cell_groups():
    rows, q_diags, s_diags = {}, {}, {}
    for q, r in CELLS:
        rows.setdefault(r, set()).add((q, r))
        q_diags.setdefault(q, set()).add((q, r))
        s_diags.setdefault(q + r, set()).add((q, r))
    return {
        (q, r): [
            SUBGRIDS[CELL_TO_SUBGRID[(q, r)]],
            frozenset(rows[r]),
            frozenset(q_diags[q]),
            frozenset(s_diags[q + r]),
        ]
        for q, r in CELLS
    }

CELL_GROUPS = _build_cell_groups()

def get_possible_values(cell, assignment):
    used = {assignment[c] for group in CELL_GROUPS[cell] for c in group if c in assignment and c != cell}
    return set(range(1, 8)) - used

def generate_complete_grid():
    assignment = {}

    def backtrack():
        if len(assignment) == len(CELLS):
            return True
        unassigned = [c for c in CELLS if c not in assignment]
        options = {c: get_possible_values(c, assignment) for c in unassigned}
        if any(len(v) == 0 for v in options.values()):
            return False
        min_opts = min(len(v) for v in options.values())
        cell = random.choice([c for c, v in options.items() if len(v) == min_opts])
        for value in random.sample(list(options[cell]), len(options[cell])):
            assignment[cell] = value
            if backtrack():
                return True
            del assignment[cell]
        return False

    backtrack()
    return assignment

def is_logically_solvable(given):
    state = dict(given)
    changed = True
    while changed:
        changed = False
        for cell in CELLS:
            if cell in state:
                continue
            possible = get_possible_values(cell, state)
            if len(possible) == 1:
                state[cell] = next(iter(possible))
                changed = True
    return len(state) == len(CELLS)

def generate_puzzle(complete_grid):
    given = dict(complete_grid)
    cells = list(CELLS)
    random.shuffle(cells)
    for cell in cells:
        value = given.pop(cell)
        if not is_logically_solvable(given):
            given[cell] = value  # restore — removal breaks solvability
    return given

def _build_lines():
    buckets = [{}, {}, {}]
    for q, r in CELLS:
        for bucket, key in zip(buckets, [r, q, q + r]):
            bucket.setdefault(key, set()).add((q, r))
    return [frozenset(v) for b in buckets for v in b.values()]

LINES = _build_lines()

def compute_errors(cell_values):
    error_cells = set()
    for group in [*SUBGRIDS.values(), *LINES]:
        vals = [cell_values[c] for c in group if c in cell_values]
        if len(vals) != len(set(vals)):
            error_cells |= group
    return error_cells

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
    selected_lines = set()
    error_cells = set()
    complete_grid = generate_complete_grid()
    given = generate_puzzle(complete_grid)
    cell_values = dict(given)

    # Number picker: 7 boxes on the left
    NUM_X, NUM_Y0, NUM_GAP = 80, 330, 55
    num_rects = [pygame.Rect(NUM_X - 22, NUM_Y0 + i * NUM_GAP - 22, 44, 44) for i in range(7)]
    hint_rect = pygame.Rect(NUM_X - 35, NUM_Y0 + 7 * NUM_GAP, 70, 34)
    hint_cell = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYDOWN and selected is not None and selected not in given:
                if event.unicode in '1234567':
                    cell_values[selected] = int(event.unicode)
                    error_cells = compute_errors(cell_values)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check number picker first
                placed = False
                for i, rect in enumerate(num_rects):
                    if rect.collidepoint(event.pos) and selected is not None and selected not in given:
                        cell_values[selected] = i + 1
                        error_cells = compute_errors(cell_values)
                        placed = True
                        break
                if not placed and hint_rect.collidepoint(event.pos):
                    hint_cell = next(
                        (c for c in CELLS if c not in cell_values
                         and len(get_possible_values(c, cell_values)) == 1),
                        None
                    )
                    placed = True
                if not placed:
                    hint_cell = None
                    clicked = pixel_to_hex(*event.pos, cx, cy)
                    if clicked in CELLS:
                        selected = None if clicked == selected else clicked
                    else:
                        selected = None
                    if selected:
                        subgrid, *lines = CELL_GROUPS[selected]
                        selected_subgrid = set(subgrid)
                        selected_lines = set().union(*lines) - selected_subgrid
                    else:
                        selected_subgrid = set()
                        selected_lines = set()

        screen.fill((255, 255, 255))

        # Draw number picker
        for i, rect in enumerate(num_rects):
            pygame.draw.rect(screen, (230, 230, 230), rect, border_radius=6)
            pygame.draw.rect(screen, (0, 0, 0), rect, width=2, border_radius=6)
            label = font.render(str(i + 1), True, (0, 0, 0))
            screen.blit(label, label.get_rect(center=rect.center))

        # Draw hint button
        pygame.draw.rect(screen, (200, 230, 200), hint_rect, border_radius=6)
        pygame.draw.rect(screen, (0, 0, 0), hint_rect, width=2, border_radius=6)
        hint_label = font.render("Hint", True, (0, 0, 0))
        screen.blit(hint_label, hint_label.get_rect(center=hint_rect.center))

        # Draw grid
        for q, r in CELLS:
            center = hex_to_pixel(q, r, cx, cy)
            if (q, r) == selected:
                fill = (173, 216, 230)
            elif (q, r) in SUBGRIDS:
                fill = (255, 245, 200)
            else:
                fill = (255, 255, 255)
            draw_hex(screen, center, SIZE - 2, fill)
            draw_hex(screen, center, SIZE - 2, (0, 0, 0), width=2)
            if (q, r) in error_cells:
                draw_hex(screen, center, SIZE - 2, (220, 50, 50), width=3)
            elif (q, r) == hint_cell:
                draw_hex(screen, center, SIZE - 2, (50, 180, 80), width=3)
            elif (q, r) in selected_subgrid:
                draw_hex(screen, center, SIZE - 2, (60, 90, 200), width=3)
            elif (q, r) in selected_lines:
                draw_hex(screen, center, SIZE - 2, (140, 180, 240), width=3)
            if (q, r) in cell_values:
                color = (0, 0, 0) if (q, r) in given else (80, 80, 180)
                label = font.render(str(cell_values[(q, r)]), True, color)
                screen.blit(label, label.get_rect(center=(int(center[0]), int(center[1]))))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
