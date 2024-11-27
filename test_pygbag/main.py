import asyncio
import pygame

async def main():
    pygame.init()
    screen = pygame.display.set_mode((320, 240))
    clock = pygame.time.Clock()
    
    # Create a font
    try:
        font = pygame.font.SysFont(None, 24)
    except:
        font = None
    
    # Animation variables
    x = 0
    dx = 2

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        # Update
        x = (x + dx) % 320  # Move across screen and wrap around
        
        # Draw
        screen.fill('red')
        
        # Draw a moving white rectangle
        pygame.draw.rect(screen, 'white', (x, 100, 40, 40))
        
        # Draw some text
        if font:
            text = font.render('Hello Pygame Web!', True, 'yellow')
            screen.blit(text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

asyncio.run(main())
