"""
Main entry point for the Caterpillar World Saver game.
Web-compatible version using Pygbag for browser deployment.
"""

import asyncio
import pygame
import sys

async def main():
    pygame.init()
    pygame.display.init()
    
    # Create the window
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Caterpillar World Saver")
    
    # Create game instance
    from game import Game
    game = Game()
    
    # Main game loop
    running = True
    while running:
        # Process events with asyncio
        await asyncio.sleep(0)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)
        
        # Clear screen
        screen.fill((255, 255, 255))
        
        # Update and draw
        if not game.paused and not game.game_over:
            game.update()
        game.draw()
        
        # Update display
        pygame.display.flip()
        
        # Cap at 60 FPS
        await asyncio.sleep(1/60)

asyncio.run(main())
