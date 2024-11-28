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
        self.width = 50
        self.height = 20
        self.segment_spacing = 3
        self.num_segments = 3
        self.segments = []
        self.speed = 3
        self.base_speed = self.speed
        self.direction = [1, 0]
        self.lives = 3  # Total lives
        self.max_energy = 100  # Maximum energy
        self.energy = self.max_energy  # Current energy
        self.last_movement_time = pygame.time.get_ticks()
        self.stuck_threshold = 5000  # 5 seconds in milliseconds
        self.reset_position()

    def lose_energy(self, amount):
        self.energy -= amount
        if self.energy <= 0:
            self.energy = self.max_energy
            self.lives -= 1
            self.reset_position()
            return True  # Life lost
        return False  # Just energy lost

    def reset_position(self):
        # Start from the left side, middle height
        while True:
            start_x = 100
            start_y = WINDOW_HEIGHT // 2
            self.segments = []
            for i in range(self.num_segments):
                x = start_x - i * (self.width + self.segment_spacing)
                self.segments.append(pygame.Rect(x, start_y, self.width, self.height))
            
            # Check if any segment overlaps with walls
            overlap = False
            if hasattr(self, 'game'):  # If game reference exists
                for wall in self.game.walls:
                    for segment in self.segments:
                        if wall.collides_with(segment):
                            overlap = True
                            break
                    if overlap:
                        break
            
            if not overlap:
                break
            # If overlap, try a different position
            start_y = random.randint(100, WINDOW_HEIGHT - 100)

    def move(self, keys, walls):
        # Store previous head position for stuck detection
        prev_head = self.segments[0].copy()
        
        # Update direction based on keys
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction = [-1, 0]
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction = [1, 0]
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction = [0, -1]
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction = [0, 1]

        # Move head
        new_head = self.segments[0].copy()
        new_head.x += self.direction[0] * self.speed
        new_head.y += self.direction[1] * self.speed

        # Check wall collisions and boundaries
        can_move = True
        for wall in walls:
            if wall.collides_with(new_head):
                can_move = False
                break

        if (new_head.left < 0 or new_head.right > WINDOW_WIDTH or 
            new_head.top < 0 or new_head.bottom > WINDOW_HEIGHT):
            can_move = False

        if can_move:
            # Successfully moved
            self.last_movement_time = pygame.time.get_ticks()
            self.segments[0] = new_head
            self.update_segments(prev_head)
        else:
            # Check if stuck
            current_time = pygame.time.get_ticks()
            if current_time - self.last_movement_time > self.stuck_threshold:
                self.lives -= 1
                if self.lives <= 0:
                    if hasattr(self, 'game'):
                        self.game.game_over = True
                else:
                    self.reset_position()
                self.last_movement_time = current_time

    def update_segments(self, prev_head):
        for i in range(1, len(self.segments)):
            current = self.segments[i]
            target_x = prev_head.x
            target_y = prev_head.y
            
            dx = target_x - current.x
            dy = target_y - current.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > self.width + self.segment_spacing:
                move_distance = self.speed
                if distance > 0:
                    current.x += (dx / distance) * move_distance
                    current.y += (dy / distance) * move_distance
            
            prev_head = current.copy()

    def draw(self, screen):
        segment_radius = 8
        
        for i, (seg_x, seg_y) in enumerate([seg.center for seg in self.segments]):
            color = LIGHT_GREEN
            if i == 0:  
                color = (144, 238, 144)  
            pygame.draw.circle(screen, color, (int(seg_x), int(seg_y)), segment_radius)
        
        head_x, head_y = self.segments[0].center
        eye_offset = -5 if self.direction[0] < 0 else 5
        pygame.draw.circle(screen, (0, 0, 0), 
                         (int(head_x + eye_offset), int(head_y - 3)), 3)
        
        antenna_start = (head_x, head_y)
        if self.direction[0] < 0:
            pygame.draw.line(screen, LIGHT_GREEN, antenna_start,
                           (head_x - 10, head_y - 10), 2)
            pygame.draw.line(screen, LIGHT_GREEN, antenna_start,
                           (head_x - 8, head_y - 12), 2)
        else:
            pygame.draw.line(screen, LIGHT_GREEN, antenna_start,
                           (head_x + 10, head_y - 10), 2)
            pygame.draw.line(screen, LIGHT_GREEN, antenna_start,
                           (head_x + 8, head_y - 12), 2)

    def get_head_rect(self):
        head_x, head_y = self.segments[0].center
        return pygame.Rect(head_x - 8, head_y - 8, 16, 16)

    def get_tail_rect(self):
        tail_x, tail_y = self.segments[-1].center
        return pygame.Rect(tail_x - 8, tail_y - 8, 16, 16)

    def update_speed(self, stage):
        speed_multiplier = min(2.0, 1.0 + (stage // 10) * 0.05)
        self.speed = self.base_speed * speed_multiplier

class Enemy:
    def __init__(self, x, y):
        self.width = 40
        self.height = 40
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.speed = 1.5
        self.base_speed = self.speed
        self.converted = False
        self.target_tail = random.choice([True, False])
        self.stuck_time = 0
        self.last_pos = self.rect.copy()
        self.movement_directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        self.current_direction = random.randint(0, 3)

    def move(self, player_segments, walls):
        if self.converted:
            return

        # Check if we're stuck by comparing current position to last position
        if self.rect.x == self.last_pos.x and self.rect.y == self.last_pos.y:
            self.stuck_time += 1
            if self.stuck_time > 30:  # Stuck for half a second (30 frames)
                # Change direction and target
                self.current_direction = (self.current_direction + 1) % 4
                self.target_tail = not self.target_tail
                self.stuck_time = 0
        else:
            self.stuck_time = 0
            self.last_pos = self.rect.copy()

        target = player_segments[-1] if self.target_tail else player_segments[0]
        
        # Try direct movement first
        dx = target.centerx - self.rect.centerx
        dy = target.centery - self.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            move_x = (dx / distance) * self.speed
            move_y = (dy / distance) * self.speed
            
            # Try direct movement
            new_rect = pygame.Rect(self.rect.x + move_x, self.rect.y + move_y, 
                                 self.width, self.height)
            
            wall_collision = False
            for wall in walls:
                if wall.collides_with(new_rect):
                    wall_collision = True
                    break
            
            if not wall_collision:
                self.rect = new_rect
                return
        
        # If direct movement failed, use alternate movement pattern
        direction = self.movement_directions[self.current_direction]
        new_rect = pygame.Rect(self.rect.x + direction[0] * self.speed,
                             self.rect.y + direction[1] * self.speed,
                             self.width, self.height)
        
        # Check wall collision for alternate movement
        wall_collision = False
        for wall in walls:
            if wall.collides_with(new_rect):
                wall_collision = True
                break
        
        # If wall collision, try next direction
        if wall_collision:
            self.current_direction = (self.current_direction + 1) % 4
        else:
            self.rect = new_rect
        
        # Keep in bounds
        self.rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

    def draw(self, screen):
        if self.converted:
            pupa_color = BROWN
            pygame.draw.ellipse(screen, pupa_color, 
                              (self.rect.x, self.rect.y, self.width, self.height))
            for i in range(4):
                y_offset = i * (self.height / 4)
                pygame.draw.line(screen, (101, 67, 33),
                               (self.rect.x, self.rect.y + y_offset),
                               (self.rect.x + self.width, self.rect.y + y_offset), 2)
        else:
            pygame.draw.rect(screen, SKIN_COLOR, 
                           (self.rect.x + self.width//4, self.rect.y + self.height//4, 
                            self.width//2, self.height//2))
            pygame.draw.circle(screen, SKIN_COLOR, 
                             (self.rect.x + self.width//2, self.rect.y + self.height//4), 
                             self.width//4)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (self.rect.x + self.width//2 - 3, self.rect.y + self.height//4 - 2), 2)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (self.rect.x + self.width//2 + 3, self.rect.y + self.height//4 - 2), 2)
            pygame.draw.line(screen, SKIN_COLOR, 
                           (self.rect.x + self.width//3, self.rect.y + self.height*3//4),
                           (self.rect.x + self.width//4, self.rect.y + self.height), 2)
            pygame.draw.line(screen, SKIN_COLOR, 
                           (self.rect.x + self.width*2//3, self.rect.y + self.height*3//4),
                           (self.rect.x + self.width*3//4, self.rect.y + self.height), 2)
            pygame.draw.line(screen, SKIN_COLOR, 
                           (self.rect.x + self.width//4, self.rect.y + self.height//2),
                           (self.rect.x, self.rect.y + self.height//2 + 10), 2)
            pygame.draw.line(screen, SKIN_COLOR, 
                           (self.rect.x + self.width*3//4, self.rect.y + self.height//2),
                           (self.rect.x + self.width, self.rect.y + self.height//2 + 10), 2)

    def update_speed(self, stage):
        speed_multiplier = min(2.0, 1.0 + (stage // 10) * 0.05)
        self.speed = self.base_speed * speed_multiplier

class Wall:
    def __init__(self, x, y, width, height, is_vertical=True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_vertical = is_vertical
        self.is_l_shaped = random.choice([True, False])
        
        # For L-shaped walls, create two rectangles
        if self.is_l_shaped:
            # Main part
            self.rect1 = pygame.Rect(x, y, width if is_vertical else height//3, 
                                   height if is_vertical else width)
            # The L part
            if is_vertical:
                self.rect2 = pygame.Rect(x, y + height - width, 
                                       height//3, width)
            else:
                self.rect2 = pygame.Rect(x + width - height//3, y, 
                                       height//3, height)
        else:
            self.rect1 = pygame.Rect(x, y, width if is_vertical else height//3, 
                                   height if is_vertical else width)
            self.rect2 = None
        
        self.color = BROWN
        self.outline_color = (101, 67, 33)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect1)
        pygame.draw.rect(screen, self.outline_color, self.rect1, 2)
        
        if self.is_l_shaped and self.rect2:
            pygame.draw.rect(screen, self.color, self.rect2)
            pygame.draw.rect(screen, self.outline_color, self.rect2, 2)

    def collides_with(self, rect):
        if self.rect1.colliderect(rect):
            return True
        if self.is_l_shaped and self.rect2 and self.rect2.colliderect(rect):
            return True
        return False

if __name__ == "__main__":
    game = Game()
    game.run()
