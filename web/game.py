import pygame
import random
import sys
import math
import os
import numpy

# Initialize Pygame and its sound system
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
LIGHT_GREEN = (144, 238, 144)
SKIN_COLOR = (255, 218, 185)
YELLOW = (255, 255, 0)

# Create sounds directory if it doesn't exist
if not os.path.exists('sounds'):
    os.makedirs('sounds')

class CaterpillarGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Caterpillar Game')
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.caterpillar = Caterpillar()
        self.apple = Apple()
        self.score = 0

    def draw_text(self, text, font_size, color, x, y):
        font = pygame.font.SysFont('arial', font_size)
        img = font.render(text, True, color)
        self.screen.blit(img, (x, y))

    def draw_score(self):
        self.draw_text(f'Score: {self.score}', 30, WHITE, 10, 10)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.caterpillar.turn_up()
                elif event.key == pygame.K_DOWN:
                    self.caterpillar.turn_down()
                elif event.key == pygame.K_LEFT:
                    self.caterpillar.turn_left()
                elif event.key == pygame.K_RIGHT:
                    self.caterpillar.turn_right()

    def update(self):
        self.caterpillar.move()
        if self.caterpillar.eat(self.apple):
            self.score += 1
            self.apple = Apple()
        if self.caterpillar.is_out_of_bounds() or self.caterpillar.is_eating_itself():
            self.reset_game()

    def draw(self):
        self.screen.fill(BLACK)
        self.caterpillar.draw(self.screen)
        self.apple.draw(self.screen)
        self.draw_score()
        pygame.display.update()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

class Caterpillar:
    def __init__(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.speed = 10
        self.direction = 'right'
        self.body = [(self.x, self.y)]

    def turn_up(self):
        if self.direction != 'down':
            self.direction = 'up'

    def turn_down(self):
        if self.direction != 'up':
            self.direction = 'down'

    def turn_left(self):
        if self.direction != 'right':
            self.direction = 'left'

    def turn_right(self):
        if self.direction != 'left':
            self.direction = 'right'

    def move(self):
        if self.direction == 'up':
            self.y -= self.speed
        elif self.direction == 'down':
            self.y += self.speed
        elif self.direction == 'left':
            self.x -= self.speed
        elif self.direction == 'right':
            self.x += self.speed
        self.body.append((self.x, self.y))
        if len(self.body) > self.speed:
            self.body.pop(0)

    def eat(self, apple):
        if self.x == apple.x and self.y == apple.y:
            return True
        return False

    def is_out_of_bounds(self):
        if self.x < 0 or self.x > WINDOW_WIDTH or self.y < 0 or self.y > WINDOW_HEIGHT:
            return True
        return False

    def is_eating_itself(self):
        if (self.x, self.y) in self.body[:-1]:
            return True
        return False

    def draw(self, screen):
        for x, y in self.body:
            pygame.draw.rect(screen, GREEN, (x, y, self.speed, self.speed))

class Apple:
    def __init__(self):
        self.x = random.randint(0, WINDOW_WIDTH - 10) // 10 * 10
        self.y = random.randint(0, WINDOW_HEIGHT - 10) // 10 * 10

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, 10, 10))

if __name__ == "__main__":
    game = CaterpillarGame()
    game.run()
