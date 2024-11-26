"""
Main entry point for the Caterpillar World Saver game.
Web-compatible version using Pygbag for browser deployment.
"""

import asyncio
import pygame
import platform
import sys
import os

# Set SDL environment variables for web
os.environ['SDL_VIDEODRIVER'] = 'webgl'

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Import game after pygame init
from game import Game

async def main():
    """Start the game with async support for web."""
    # Create game instance
    game = Game()
    
    # Main game loop with async support
    running = True
    while running:
        # Process events with asyncio
        await asyncio.sleep(0)  # Let the browser breathe
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Handle game events
            game.handle_event(event)
        
        # Update game state
        if not game.paused and not game.game_over:
            if not game.update():
                running = False
        
        # Draw everything
        game.draw()
        pygame.display.flip()
        
        # Control frame rate
        game.clock.tick(60)

    # Clean up
    pygame.quit()
    if platform.system() != "Emscripten":
        sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
