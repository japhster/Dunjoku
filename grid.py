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

def hex_to_pixel(q, r, cx, cy):
    x = cx + (q + r / 2) * math.sqrt(3) * SIZE
    y = cy + r * 1.5 * SIZE
    return (x, y)

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

    cx, cy = 500, 500

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.fill((255, 255, 255))

        for q, r in CELLS:
            center = hex_to_pixel(q, r, cx, cy)
            draw_hex(screen, center, SIZE - 2, (255, 255, 255))
            draw_hex(screen, center, SIZE - 2, (0, 0, 0), width=2)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
