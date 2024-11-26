"""
Main entry point for the Caterpillar World Saver game.
Web-compatible version using Pygbag for browser deployment.
"""

import asyncio
import pygame
from .game import Game

async def main():
    """Start the game with async support for web."""
    game = Game()
    
    # Main game loop with async support
    running = True
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Handle game events
            game.handle_event(event)
            
        # Update game state
        if not game.paused and not game.game_over:
            game.update()
            
        # Draw everything
        game.draw()
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        await asyncio.sleep(0)  # Let the browser breathe

if __name__ == "__main__":
    asyncio.run(main())
