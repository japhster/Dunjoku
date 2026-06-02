# Dunjoku

A hexagonal number-placement puzzle game built with Python and Pygame.

<img width="866" height="846" alt="image" src="https://github.com/user-attachments/assets/a815f100-dd42-49d3-9bdb-eb3bd31772b2" />

## Rules

Place the numbers 1–7 so that no value repeats within any:
- **Subgrid** — a 7-cell flower (center hex + its 6 neighbours)
- **Row** — cells sharing the same axial `r` coordinate
- **Diagonal** — cells sharing the same `q` or `q+r` coordinate

## How to play

- **Click** a cell to select it, then press **1–7** to place a number
- Duplicate violations are highlighted in red
- **Hint** — highlights a cell where the correct value can be logically deduced
- **Notes** — toggle notes mode; press 1–7 to mark candidate values in empty cells (placing a real number clears notes from affected cells automatically)
- **Clear** — removes the value or notes from the selected cell
- **New Game** — returns to the difficulty selection screen
- A **timer** in the top-left tracks how long the game has lasted; your final time is shown in the completion popup

## Difficulty

| Level  | Cells removed |
|--------|--------------|
| Easy   | up to 20     |
| Medium | up to 30     |
| Hard   | up to 40     |

## Requirements

- Python 3
- [Pygame](https://www.pygame.org/) (`pip install pygame`)

## Running

```
python grid.py
```
