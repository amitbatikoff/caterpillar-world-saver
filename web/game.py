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
BLACK = (0, 0, 0)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Caterpillar World Saver")
        self.clock = pygame.time.Clock()
        self.reset_game()
        self.paused = False
        self.game_over = False
        
    def reset_game(self):
        self.player = Player()
        self.player.game = self  # Give player a reference to game
        self.walls = []
        self.enemies = []
        self.stage = 1
        self.particles = []
        self.generate_walls()
        self.spawn_enemies()
        
    def generate_walls(self):
        self.walls = []
        num_walls = 3 + self.stage  # More walls as stages progress
        for _ in range(num_walls):
            while True:
                x = random.randint(100, WINDOW_WIDTH - 100)
                y = random.randint(100, WINDOW_HEIGHT - 100)
                wall = Wall(x, y, 20, 100, random.choice([True, False]))
                
                # Check if wall overlaps with other walls
                overlap = False
                for other_wall in self.walls:
                    if (abs(wall.x - other_wall.x) < 100 and 
                        abs(wall.y - other_wall.y) < 100):
                        overlap = True
                        break
                
                if not overlap:
                    self.walls.append(wall)
                    break
    
    def spawn_enemies(self):
        self.enemies = []
        num_enemies = 2 + self.stage  # More enemies as stages progress
        for _ in range(num_enemies):
            while True:
                x = random.randint(100, WINDOW_WIDTH - 100)
                y = random.randint(100, WINDOW_HEIGHT - 100)
                enemy = Enemy(x, y)
                
                # Check if enemy overlaps with walls or other enemies
                overlap = False
                for wall in self.walls:
                    if wall.collides_with(enemy.rect):
                        overlap = True
                        break
                        
                for other_enemy in self.enemies:
                    if enemy.rect.colliderect(other_enemy.rect):
                        overlap = True
                        break
                
                if not overlap:
                    enemy.update_speed(self.stage)
                    self.enemies.append(enemy)
                    break
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over:
                    mouse_pos = pygame.mouse.get_pos()
                    self.handle_game_over_click(mouse_pos)
                elif self.paused:
                    mouse_pos = pygame.mouse.get_pos()
                    self.handle_menu_click(mouse_pos)
        return True

    def update(self):
        if self.paused or self.game_over:
            return
            
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Move player
        self.player.move(keys, self.walls)
        
        # Move enemies
        for enemy in self.enemies:
            enemy.move(self.player.segments, self.walls)
            
        # Handle collisions
        self.handle_collisions()
        
        # Update particles
        self.update_particles()
        
        # Check if stage is complete
        if all(enemy.converted for enemy in self.enemies):
            self.stage += 1
            self.reset_stage()
            
        # Check game over
        if self.player.lives <= 0:
            self.game_over = True
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw walls
        for wall in self.walls:
            wall.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw UI
        self.draw_energy_bar()
        self.draw_lives()
        
        # Draw pause screen if paused
        if self.paused:
            self.draw_pause_screen()
            
        # Draw game over screen if game over
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
        self.clock.tick(FPS)
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()
        sys.exit()

class Player:
    def __init__(self):
        self.width = 20
        self.height = 20
        self.segments = [pygame.Rect(100, WINDOW_HEIGHT//2, self.width, self.height)]
        self.speed = 5
        self.direction = [1, 0]
        self.lives = 3
        self.energy = 100
        self.max_energy = 100
        
    def move(self, keys, walls):
        # Update direction based on keys
        if keys[pygame.K_LEFT]:
            self.direction = [-1, 0]
        if keys[pygame.K_RIGHT]:
            self.direction = [1, 0]
        if keys[pygame.K_UP]:
            self.direction = [0, -1]
        if keys[pygame.K_DOWN]:
            self.direction = [0, 1]
            
        # Move head
        head = self.segments[0].copy()
        head.x += self.direction[0] * self.speed
        head.y += self.direction[1] * self.speed
        
        # Check wall collisions
        for wall in walls:
            if wall.collides_with(head):
                return
                
        # Check boundaries
        if (head.left < 0 or head.right > WINDOW_WIDTH or 
            head.top < 0 or head.bottom > WINDOW_HEIGHT):
            return
            
        self.segments[0] = head
        
    def draw(self, screen):
        for segment in self.segments:
            pygame.draw.rect(screen, GREEN, segment)
            pygame.draw.rect(screen, LIGHT_GREEN, segment, 2)

class Enemy:
    def __init__(self, x, y):
        self.width = 20
        self.height = 20
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.speed = 2
        self.converted = False
        
    def move(self, player_segments, walls):
        if self.converted:
            return
            
        # Move towards player head
        head = player_segments[0]
        dx = head.centerx - self.rect.centerx
        dy = head.centery - self.rect.centery
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            dx = dx/dist * self.speed
            dy = dy/dist * self.speed
            
            new_rect = self.rect.copy()
            new_rect.x += dx
            new_rect.y += dy
            
            # Check wall collisions
            can_move = True
            for wall in walls:
                if wall.collides_with(new_rect):
                    can_move = False
                    break
                    
            if can_move:
                self.rect = new_rect
    
    def draw(self, screen):
        color = BLUE if not self.converted else GREEN
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)

class Wall:
    def __init__(self, x, y, width, height, vertical=True):
        self.x = x
        self.y = y
        self.width = width if vertical else height
        self.height = height if vertical else width
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
    def collides_with(self, rect):
        return self.rect.colliderect(rect)
        
    def draw(self, screen):
        pygame.draw.rect(screen, BROWN, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)

if __name__ == "__main__":
    game = Game()
    game.run()
