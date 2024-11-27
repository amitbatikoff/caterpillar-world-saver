import asyncio
import pygame

async def main():
    # Initialize Pygame
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Simple Pygame Web Test")
    
    # Main game loop
    running = True
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Fill the screen with a color
        screen.fill((255, 0, 0))  # Bright red screen
        
        # Update the display
        pygame.display.flip()
        
        # Allow browser to update
        await asyncio.sleep(0.1)

    pygame.quit()

# Run the main function
asyncio.run(main())
