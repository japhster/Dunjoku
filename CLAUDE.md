# Dunjoku

A hexagonal number-placement puzzle game built with Python and Pygame.

## Running the game

```
python grid.py
```

## Architecture

All code lives in `grid.py`. Top-to-bottom order:

1. **Module-level data** — `CELLS`, `SIZE`, `SUBGRIDS`, `CELL_TO_SUBGRID`, `SUBGRID_COLORS`, `CELL_FILL_COLOR`, `CELL_GROUPS`, `LINES`
2. **Pure logic** — `get_possible_values`, `generate_complete_grid`, `is_logically_solvable`, `generate_puzzle`, `compute_errors`
3. **Rendering helpers** — `hex_to_pixel`, `pixel_to_hex`, `draw_hex`
4. **`GameState` class** — all mutable game state; `reset()` is shared by `__init__` and `new_game()`
5. **`UIRects` namedtuple** — all static pygame.Rect geometry, built once in `main()`
6. **`handle_events(state, rects, cx, cy) -> bool`** — full event loop; returns False to quit
7. **`draw(screen, state, font, big_font, rects, cx, cy)`** — full render pass
8. **`main()`** — pygame init, builds `UIRects`, creates `GameState`, runs the game loop

## Grid coordinate system

Pointy-top hexagons using axial coordinates `(q, r)`:
- `hex_to_pixel`: `x = cx + (q + r/2) * sqrt(3) * SIZE`, `y = cy + r * 1.5 * SIZE`
- Three constraint directions: same `r` (row), same `q` (q-diagonal), same `q+r` (s-diagonal)

## Terminology

- **Cell** — a single hexagon on the board
- **Subgrid** — a 7-cell flower group (center + 6 axial neighbours); there are 7 subgrids
- **Line** — a row or diagonal; lengths vary (2, 5, or 7 cells)

## Puzzle rules

Each subgrid, row, and diagonal must contain no duplicate values 1–7. Puzzle generation strips cells until no single further removal is solvable by naked singles alone.
