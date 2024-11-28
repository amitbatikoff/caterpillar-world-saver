import asyncio
import pygame

async def main():
    print("Starting Hello World game...")
    
    # Initialize Pygame
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Hello World")
    
    # Set up the font
    font = pygame.font.SysFont(None, 48)
    
    # Create the text surface
    text = font.render("Hello World!", True, (255, 255, 255))
    text_rect = text.get_rect(center=(200, 150))
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Fill screen with dark blue
        screen.fill((0, 0, 100))
        
        # Draw the text
        screen.blit(text, text_rect)
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        await asyncio.sleep(0)

asyncio.run(main())
