import asyncio
import pygame
import numpy as np
from game import Game

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Caterpillar World Saver")

async def main():
    """Main game loop with async support for web."""
    game = Game()
    
    running = True
    while running:
        # Handle events
        running = game.handle_events()
        
        # Update game state
        game.update()
        
        # Draw everything
        game.draw()
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate and allow other async operations
        await asyncio.sleep(0)

asyncio.run(main())
