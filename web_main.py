"""
Main entry point for the Caterpillar World Saver game.
Web-compatible version using Pygbag for browser deployment.
"""

import asyncio
import pygame
import sys
import platform

async def main():
    print("Initializing Pygame...")
    pygame.init()
    pygame.display.init()
    
    # Set up display with hardware acceleration and scaling
    flags = pygame.SCALED
    if platform.system() == "Emscripten":
        flags |= pygame.FULLSCREEN
    
    # Create the window with specific flags
    print("Setting up display...")
    screen = pygame.display.set_mode((800, 600), flags)
    pygame.display.set_caption("Caterpillar World Saver")
    
    # Import game after pygame init
    print("Importing game module...")
    from caterpillar_world_saver.game import Game
    game = Game()
    
    # Main game loop
    running = True
    frame_count = 0
    while running:
        try:
            # Process events with asyncio
            await asyncio.sleep(0)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Handle resize events
                    width = max(800, event.w)
                    height = max(600, event.h)
                    screen = pygame.display.set_mode((width, height), flags)
                game.handle_event(event)
            
            # Clear screen with black background
            screen.fill((0, 0, 0))
            
            # Update and draw
            if not game.paused and not game.game_over:
                game.update()
            game.draw()
            
            # Basic rendering to confirm loop execution
            pygame.draw.circle(screen, (255, 0, 0), (400, 300), 50)
            
            # Update display
            pygame.display.flip()
            
            # Cap at 60 FPS
            await asyncio.sleep(1/60)
            
            # Debug frame count
            frame_count += 1
            if frame_count % 60 == 0:
                print(f"Frame: {frame_count}")
            
        except Exception as e:
            print(f"Error in game loop: {e}")
            continue

if __name__ == "__main__":
    print("Starting game...")
    asyncio.run(main())
