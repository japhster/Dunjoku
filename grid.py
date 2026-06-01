import math
import random
from collections import namedtuple
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

SUBGRID_COLORS = {
    center: color for center, color in zip(SUBGRIDS, [
        (255, 200, 200),  # red
        (200, 220, 255),  # blue
        (200, 245, 210),  # green
        (255, 230, 190),  # orange
        (230, 200, 255),  # purple
        (190, 240, 240),  # teal
        (255, 255, 190),  # yellow
    ])
}

CELL_FILL_COLOR = {cell: SUBGRID_COLORS[CELL_TO_SUBGRID[cell]] for cell in CELLS}

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


class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.complete_grid = generate_complete_grid()
        self.given = generate_puzzle(self.complete_grid)
        self.cell_values = dict(self.given)
        self.selected = None
        self.selected_subgrid = set()
        self.selected_lines = set()
        self.error_cells = set()
        self.hint_cell = None
        self.complete = False

    def new_game(self):
        self.reset()

    def check_complete(self):
        if len(self.cell_values) == len(CELLS):
            self.error_cells = compute_errors(self.cell_values)
            if not self.error_cells:
                self.complete = True


UIRects = namedtuple('UIRects', ['num_rects', 'hint_rect', 'clear_rect', 'overlay_rect', 'again_rect', 'quit_rect'])


def handle_events(state, rects, cx, cy):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return False
        if state.complete:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rects.again_rect.collidepoint(event.pos):
                    state.new_game()
                elif rects.quit_rect.collidepoint(event.pos):
                    return False
            continue
        if event.type == pygame.KEYDOWN and state.selected is not None and state.selected not in state.given:
            if event.unicode in '1234567':
                state.cell_values[state.selected] = int(event.unicode)
                state.error_cells = compute_errors(state.cell_values)
                state.check_complete()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            placed = False
            for i, rect in enumerate(rects.num_rects):
                if rect.collidepoint(event.pos) and state.selected is not None and state.selected not in state.given:
                    state.cell_values[state.selected] = i + 1
                    state.error_cells = compute_errors(state.cell_values)
                    state.check_complete()
                    placed = True
                    break
            if not placed and rects.clear_rect.collidepoint(event.pos):
                if state.selected is not None and state.selected not in state.given:
                    state.cell_values.pop(state.selected, None)
                    state.error_cells = compute_errors(state.cell_values)
                placed = True
            if not placed and rects.hint_rect.collidepoint(event.pos):
                state.hint_cell = next(
                    (c for c in CELLS if c not in state.cell_values
                     and len(get_possible_values(c, state.cell_values)) == 1),
                    None
                )
                placed = True
            if not placed:
                state.hint_cell = None
                clicked = pixel_to_hex(*event.pos, cx, cy)
                if clicked in CELLS:
                    state.selected = None if clicked == state.selected else clicked
                else:
                    state.selected = None
                if state.selected:
                    subgrid, *lines = CELL_GROUPS[state.selected]
                    state.selected_subgrid = set(subgrid)
                    state.selected_lines = set().union(*lines) - state.selected_subgrid
                else:
                    state.selected_subgrid = set()
                    state.selected_lines = set()
    return True


def draw(screen, state, font, big_font, rects, cx, cy):
    screen.fill((255, 255, 255))

    for i, rect in enumerate(rects.num_rects):
        pygame.draw.rect(screen, (230, 230, 230), rect, border_radius=6)
        pygame.draw.rect(screen, (0, 0, 0), rect, width=2, border_radius=6)
        label = font.render(str(i + 1), True, (0, 0, 0))
        screen.blit(label, label.get_rect(center=rect.center))

    pygame.draw.rect(screen, (200, 230, 200), rects.hint_rect, border_radius=6)
    pygame.draw.rect(screen, (0, 0, 0), rects.hint_rect, width=2, border_radius=6)
    screen.blit(font.render("Hint", True, (0, 0, 0)),
                font.render("Hint", True, (0, 0, 0)).get_rect(center=rects.hint_rect.center))

    pygame.draw.rect(screen, (230, 200, 200), rects.clear_rect, border_radius=6)
    pygame.draw.rect(screen, (0, 0, 0), rects.clear_rect, width=2, border_radius=6)
    screen.blit(font.render("Clear", True, (0, 0, 0)),
                font.render("Clear", True, (0, 0, 0)).get_rect(center=rects.clear_rect.center))

    for q, r in CELLS:
        center = hex_to_pixel(q, r, cx, cy)
        fill = (173, 216, 230) if (q, r) == state.selected else CELL_FILL_COLOR[(q, r)]
        draw_hex(screen, center, SIZE - 2, fill)
        draw_hex(screen, center, SIZE - 2, (0, 0, 0), width=2)
        if (q, r) in state.error_cells:
            draw_hex(screen, center, SIZE - 2, (220, 50, 50), width=3)
        elif (q, r) == state.hint_cell:
            draw_hex(screen, center, SIZE - 2, (50, 180, 80), width=3)
        elif (q, r) in state.selected_subgrid:
            draw_hex(screen, center, SIZE - 2, (60, 90, 200), width=3)
        elif (q, r) in state.selected_lines:
            draw_hex(screen, center, SIZE - 2, (140, 180, 240), width=3)
        if (q, r) in state.cell_values:
            color = (0, 0, 0) if (q, r) in state.given else (80, 80, 180)
            label = font.render(str(state.cell_values[(q, r)]), True, color)
            screen.blit(label, label.get_rect(center=(int(center[0]), int(center[1]))))

    if state.complete:
        pygame.draw.rect(screen, (255, 255, 255), rects.overlay_rect, border_radius=12)
        pygame.draw.rect(screen, (0, 0, 0), rects.overlay_rect, width=3, border_radius=12)
        msg = big_font.render("Congratulations!", True, (0, 0, 0))
        screen.blit(msg, msg.get_rect(center=(500, 420)))
        sub = font.render("You completed the Dunjoku grid.", True, (0, 0, 0))
        screen.blit(sub, sub.get_rect(center=(500, 475)))
        pygame.draw.rect(screen, (200, 230, 200), rects.again_rect, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), rects.again_rect, width=2, border_radius=8)
        screen.blit(font.render("Play Again", True, (0, 0, 0)),
                    font.render("Play Again", True, (0, 0, 0)).get_rect(center=rects.again_rect.center))
        pygame.draw.rect(screen, (230, 200, 200), rects.quit_rect, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), rects.quit_rect, width=2, border_radius=8)
        screen.blit(font.render("Quit", True, (0, 0, 0)),
                    font.render("Quit", True, (0, 0, 0)).get_rect(center=rects.quit_rect.center))


def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    pygame.display.set_caption("Dunjoku")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 44)
    big_font = pygame.font.SysFont(None, 56)
    cx, cy = 500, 500

    NUM_X, NUM_Y0, NUM_GAP = 80, 330, 55
    rects = UIRects(
        num_rects=[pygame.Rect(NUM_X - 22, NUM_Y0 + i * NUM_GAP - 22, 44, 44) for i in range(7)],
        hint_rect=pygame.Rect(NUM_X - 35, NUM_Y0 + 7 * NUM_GAP, 70, 34),
        clear_rect=pygame.Rect(NUM_X - 35, NUM_Y0 + 7 * NUM_GAP + 44, 70, 34),
        overlay_rect=pygame.Rect(250, 370, 500, 200),
        again_rect=pygame.Rect(310, 510, 160, 44),
        quit_rect=pygame.Rect(530, 510, 160, 44),
    )
    state = GameState()

    running = True
    while running:
        running = handle_events(state, rects, cx, cy)
        draw(screen, state, font, big_font, rects, cx, cy)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
