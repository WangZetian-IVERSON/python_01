import pygame
import math
import sys

# Placeholder tidal data: list of (time, amplitude)
tidal_data = [(i, 50 + 40 * math.sin(i * 0.1)) for i in range(500)]

WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH // 2, HEIGHT // 2)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

frame = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((10, 10, 30))

    # Draw spiral using tidal data
    for i in range(frame, min(frame + 200, len(tidal_data))):
        t, amp = tidal_data[i]
        angle = t * 0.15
        radius = 100 + amp
        x = CENTER[0] + int(radius * math.cos(angle))
        y = CENTER[1] + int(radius * math.sin(angle))
        color = (int(100 + amp), int(100 + amp/2), 200)
        pygame.draw.circle(screen, color, (x, y), 4)

    frame = (frame + 2) % len(tidal_data)
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
