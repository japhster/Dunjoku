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

# difficulty levels
EASY = 20
MEDIUM = 30
HARD = 40

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

def generate_puzzle(complete_grid, max_remove):
    given = dict(complete_grid)
    cells = list(CELLS)
    random.shuffle(cells)
    removed = 0
    for cell in cells:
        if removed >= max_remove:
            break
        value = given.pop(cell)
        if not is_logically_solvable(given):
            given[cell] = value
        else:
            removed += 1
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

def format_time(ms):
    s = ms // 1000
    m, s = divmod(s, 60)
    return f"{m:02d}:{s:02d}"


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

def draw_button(screen, font, rect, label, color, border_radius=6):
    pygame.draw.rect(screen, color, rect, border_radius=border_radius)
    pygame.draw.rect(screen, (0, 0, 0), rect, width=2, border_radius=border_radius)
    lbl = font.render(label, True, (0, 0, 0))
    screen.blit(lbl, lbl.get_rect(center=rect.center))


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
        self.choosing_difficulty = True
        self.complete_grid = None
        self.given = {}
        self.cell_values = {}
        self.cell_notes = {}
        self.notes_mode = False
        self.selected = None
        self.selected_subgrid = set()
        self.selected_lines = set()
        self.error_cells = set()
        self.hint_cell = None
        self.complete = False
        self.start_ticks = 0
        self.finish_ticks = None

    def start(self, difficulty):
        self.complete_grid = generate_complete_grid()
        self.given = generate_puzzle(self.complete_grid, difficulty)
        self.cell_values = dict(self.given)
        self.cell_notes = {}
        self.notes_mode = False
        self.selected = None
        self.selected_subgrid = set()
        self.selected_lines = set()
        self.error_cells = set()
        self.hint_cell = None
        self.complete = False
        self.start_ticks = pygame.time.get_ticks()
        self.finish_ticks = None
        self.choosing_difficulty = False

    def new_game(self):
        self.choosing_difficulty = True

    def place_value(self, cell, v):
        self.cell_values[cell] = v
        self.cell_notes.pop(cell, None)
        for group in CELL_GROUPS[cell]:
            for c in group:
                if c in self.cell_notes:
                    self.cell_notes[c].discard(v)
        self.error_cells = compute_errors(self.cell_values)
        self.check_complete()

    def check_complete(self):
        if len(self.cell_values) == len(CELLS):
            self.error_cells = compute_errors(self.cell_values)
            if not self.error_cells:
                self.complete = True
                self.finish_ticks = pygame.time.get_ticks()


UIRects = namedtuple('UIRects', ['num_rects', 'hint_rect', 'clear_rect', 'notes_rect', 'overlay_rect', 'again_rect', 'quit_rect', 'easy_rect', 'medium_rect', 'hard_rect'])


def handle_events(state, rects, cx, cy):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return False
        if state.choosing_difficulty:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rects.easy_rect.collidepoint(event.pos):
                    state.start(EASY)
                elif rects.medium_rect.collidepoint(event.pos):
                    state.start(MEDIUM)
                elif rects.hard_rect.collidepoint(event.pos):
                    state.start(HARD)
            continue
        if state.complete:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rects.again_rect.collidepoint(event.pos):
                    state.new_game()
                elif rects.quit_rect.collidepoint(event.pos):
                    return False
            continue
        if event.type == pygame.KEYDOWN and state.selected is not None and state.selected not in state.given:
            if event.unicode in '1234567':
                v = int(event.unicode)
                if state.notes_mode and state.selected not in state.cell_values:
                    notes = state.cell_notes.setdefault(state.selected, set())
                    if v in notes:
                        notes.discard(v)
                    else:
                        notes.add(v)
                elif not state.notes_mode:
                    state.place_value(state.selected, v)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            placed = False
            for i, rect in enumerate(rects.num_rects):
                if rect.collidepoint(event.pos) and state.selected is not None and state.selected not in state.given:
                    v = i + 1
                    if state.notes_mode and state.selected not in state.cell_values:
                        notes = state.cell_notes.setdefault(state.selected, set())
                        if v in notes:
                            notes.discard(v)
                        else:
                            notes.add(v)
                    elif not state.notes_mode:
                        state.place_value(state.selected, v)
                    placed = True
                    break
            if not placed and rects.notes_rect.collidepoint(event.pos):
                state.notes_mode = not state.notes_mode
                placed = True
            if not placed and rects.clear_rect.collidepoint(event.pos):
                if state.selected is not None and state.selected not in state.given:
                    if state.notes_mode:
                        state.cell_notes.pop(state.selected, None)
                    else:
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


NOTE_OFFSETS = {
    1: (-16, -18), 2: (0, -18), 3: (16, -18),
    4: (-16,   0), 5: (0,   0), 6: (16,   0),
    7: (  0,  18),
}


def draw_difficulty_screen(screen, font, big_font, rects):
    title = big_font.render("Choose Difficulty", True, (0, 0, 0))
    screen.blit(title, title.get_rect(center=(500, 350)))
    for rect, label, color in [
        (rects.easy_rect, "Easy", (200, 230, 200)),
        (rects.medium_rect, "Medium", (255, 230, 190)),
        (rects.hard_rect, "Hard", (230, 200, 200)),
    ]:
        draw_button(screen, font, rect, label, color, border_radius=8)


def draw_cell(screen, font, notes_font, cell, center, state):
    fill = (173, 216, 230) if cell == state.selected else CELL_FILL_COLOR[cell]
    draw_hex(screen, center, SIZE - 2, fill)
    draw_hex(screen, center, SIZE - 2, (0, 0, 0), width=2)
    if cell in state.error_cells:
        draw_hex(screen, center, SIZE - 2, (220, 50, 50), width=3)
    elif cell == state.hint_cell:
        draw_hex(screen, center, SIZE - 2, (50, 180, 80), width=3)
    elif cell in state.selected_subgrid:
        draw_hex(screen, center, SIZE - 2, (60, 90, 200), width=3)
    elif cell in state.selected_lines:
        draw_hex(screen, center, SIZE - 2, (140, 180, 240), width=3)
    cx, cy = int(center[0]), int(center[1])
    if cell in state.cell_values:
        color = (0, 0, 0) if cell in state.given else (80, 80, 180)
        lbl = font.render(str(state.cell_values[cell]), True, color)
        screen.blit(lbl, lbl.get_rect(center=(cx, cy)))
    elif cell in state.cell_notes:
        for v in state.cell_notes[cell]:
            dx, dy = NOTE_OFFSETS[v]
            lbl = notes_font.render(str(v), True, (100, 100, 180))
            screen.blit(lbl, lbl.get_rect(center=(cx + dx, cy + dy)))


def draw_completion_overlay(screen, font, big_font, rects, elapsed):
    pygame.draw.rect(screen, (255, 255, 255), rects.overlay_rect, border_radius=12)
    pygame.draw.rect(screen, (0, 0, 0), rects.overlay_rect, width=3, border_radius=12)
    msg = big_font.render("Congratulations!", True, (0, 0, 0))
    screen.blit(msg, msg.get_rect(center=(500, 415)))
    sub = font.render("You completed the Dunjoku grid.", True, (0, 0, 0))
    screen.blit(sub, sub.get_rect(center=(500, 460)))
    time_label = font.render(f"Time: {format_time(elapsed)}", True, (80, 80, 180))
    screen.blit(time_label, time_label.get_rect(center=(500, 500)))
    draw_button(screen, font, rects.again_rect, "Play Again", (200, 230, 200), border_radius=8)
    draw_button(screen, font, rects.quit_rect, "Quit", (230, 200, 200), border_radius=8)


def draw(screen, state, font, big_font, notes_font, rects, cx, cy):
    screen.fill((255, 255, 255))

    if state.choosing_difficulty:
        draw_difficulty_screen(screen, font, big_font, rects)
        return

    elapsed = (state.finish_ticks if state.finish_ticks else pygame.time.get_ticks()) - state.start_ticks
    timer_label = font.render(format_time(elapsed), True, (0, 0, 0))
    screen.blit(timer_label, (20, 20))

    for i, rect in enumerate(rects.num_rects):
        draw_button(screen, font, rect, str(i + 1), (230, 230, 230))
    draw_button(screen, font, rects.hint_rect, "Hint", (200, 230, 200))
    draw_button(screen, font, rects.clear_rect, "Clear", (230, 200, 200))
    draw_button(screen, font, rects.notes_rect, "Notes", (160, 210, 160) if state.notes_mode else (230, 230, 230))

    for cell in CELLS:
        draw_cell(screen, font, notes_font, cell, hex_to_pixel(*cell, cx, cy), state)

    if state.complete:
        draw_completion_overlay(screen, font, big_font, rects, elapsed)


def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    pygame.display.set_caption("Dunjoku")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 44)
    big_font = pygame.font.SysFont(None, 56)
    notes_font = pygame.font.SysFont(None, 20)
    cx, cy = 500, 500

    NUM_X, NUM_Y0, NUM_GAP = 80, 330, 55
    rects = UIRects(
        num_rects=[pygame.Rect(NUM_X - 22, NUM_Y0 + i * NUM_GAP - 22, 44, 44) for i in range(7)],
        hint_rect=pygame.Rect(NUM_X - 45, NUM_Y0 + 7 * NUM_GAP, 90, 38),
        clear_rect=pygame.Rect(NUM_X - 45, NUM_Y0 + 7 * NUM_GAP + 44, 90, 38),
        notes_rect=pygame.Rect(NUM_X - 45, NUM_Y0 + 7 * NUM_GAP + 88, 90, 38),
        overlay_rect=pygame.Rect(250, 370, 500, 230),
        again_rect=pygame.Rect(310, 540, 160, 44),
        quit_rect=pygame.Rect(530, 540, 160, 44),
        easy_rect=pygame.Rect(400, 420, 200, 50),
        medium_rect=pygame.Rect(400, 490, 200, 50),
        hard_rect=pygame.Rect(400, 560, 200, 50),
    )
    state = GameState()

    running = True
    while running:
        running = handle_events(state, rects, cx, cy)
        draw(screen, state, font, big_font, notes_font, rects, cx, cy)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
