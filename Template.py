import pygame
import random
from settings import *


# Initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.dispaly.set_caption("New Game")
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()

# Game loop
running = True
while running:
    # Keep loop running at the right speed
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        # Check for closing window
        if event.type == pygame.QUIT:
            running = False

    # Update
    all_sprites.update()

    # Draw / Render
    screen.fill(BLACK)
    all_sprites.draw(screen)
    # After drawing everything we need to flip for display.
    pygame.dispaly.flip()

pygame.quit()