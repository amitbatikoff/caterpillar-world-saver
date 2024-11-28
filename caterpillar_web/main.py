import asyncio
import pygame
import random
import math
import os
import numpy

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BASE_SPEED = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
LIGHT_GREEN = (144, 238, 144)
SKIN_COLOR = (255, 218, 185)

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
        dx = target[0] - self.rect.centerx
        dy = target[1] - self.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Try direct movement
            move_x = (dx / distance) * self.speed
            move_y = (dy / distance) * self.speed
            
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
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def draw(self, screen):
        if self.converted:
            # Draw pupa form
            pupa_color = BROWN
            pygame.draw.ellipse(screen, pupa_color, 
                              (self.rect.x, self.rect.y, self.width, self.height))
            for i in range(4):
                y_offset = i * (self.height / 4)
                pygame.draw.line(screen, (101, 67, 33),
                               (self.rect.x, self.rect.y + y_offset),
                               (self.rect.x + self.width, self.rect.y + y_offset), 2)
        else:
            # Draw human form
            # Draw body
            pygame.draw.rect(screen, SKIN_COLOR, 
                           (self.rect.x + self.width//4, self.rect.y + self.height//4, 
                            self.width//2, self.height//2))
            # Draw head
            pygame.draw.circle(screen, SKIN_COLOR, 
                             (self.rect.x + self.width//2, self.rect.y + self.height//4), 
                             self.width//4)
            # Draw eyes
            pygame.draw.circle(screen, (0, 0, 0), 
                             (self.rect.x + self.width//2 - 3, self.rect.y + self.height//4 - 2), 2)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (self.rect.x + self.width//2 + 3, self.rect.y + self.height//4 - 2), 2)
            # Draw legs
            pygame.draw.line(screen, SKIN_COLOR, 
                           (self.rect.x + self.width//3, self.rect.y + self.height*3//4),
                           (self.rect.x + self.width//4, self.rect.y + self.height), 2)
            pygame.draw.line(screen, SKIN_COLOR, 
                           (self.rect.x + self.width*2//3, self.rect.y + self.height*3//4),
                           (self.rect.x + self.width*3//4, self.rect.y + self.height), 2)
            # Draw arms
            pygame.draw.line(screen, SKIN_COLOR, 
                           (self.rect.x + self.width//4, self.rect.y + self.height//2),
                           (self.rect.x, self.rect.y + self.height//2 + 10), 2)
            pygame.draw.line(screen, SKIN_COLOR, 
                           (self.rect.x + self.width*3//4, self.rect.y + self.height//2),
                           (self.rect.x + self.width, self.rect.y + self.height//2 + 10), 2)

class Player:
    def __init__(self):
        self.width = 30
        self.height = 15
        self.segment_spacing = 2
        self.num_segments = 3
        self.segments = []
        self.speed = 3
        self.base_speed = self.speed
        self.direction = [1, 0]
        self.lives = 3
        self.max_energy = 100
        self.energy = self.max_energy
        self.last_movement_time = pygame.time.get_ticks()
        self.stuck_threshold = 5000
        self.reset_position()

    def lose_energy(self, amount):
        self.energy -= amount
        if self.energy <= 0:
            self.energy = self.max_energy
            self.lives -= 1
            self.reset_position()
            return True
        return False

    def reset_position(self):
        if hasattr(self, 'game'):
            safe_pos = self.find_safe_spawn_position()
            x, y = safe_pos
        else:
            x = SCREEN_WIDTH // 4
            y = SCREEN_HEIGHT // 2

        self.segments = []
        for i in range(self.num_segments):
            segment = pygame.Rect(x - i * (self.width + self.segment_spacing),
                                y, self.width, self.height)
            self.segments.append(segment)
        self.direction = [1, 0]

    def find_safe_spawn_position(self):
        safe_distance = 100
        margin = 50
        
        min_x = margin + safe_distance
        max_x = SCREEN_WIDTH - margin - safe_distance
        min_y = margin + safe_distance
        max_y = SCREEN_HEIGHT - margin - safe_distance
        
        max_attempts = 50
        attempt = 0
        
        while attempt < max_attempts:
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)
            
            is_safe = True
            for wall in self.game.walls:
                wall_center = (wall.rect1.centerx, wall.rect1.centery)
                distance = ((x - wall_center[0]) ** 2 + (y - wall_center[1]) ** 2) ** 0.5
                if distance < safe_distance:
                    is_safe = False
                    break
            
            if is_safe:
                return (x, y)
            
            attempt += 1
        
        return (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)

    def move(self, keys, walls):
        prev_head = self.segments[0].copy()
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction = [-1, 0]
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction = [1, 0]
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction = [0, -1]
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction = [0, 1]

        new_head = self.segments[0].copy()
        new_head.x += self.direction[0] * self.speed
        new_head.y += self.direction[1] * self.speed

        can_move = True
        for wall in walls:
            if wall.collides_with(new_head):
                can_move = False
                break

        if (new_head.left < 0 or new_head.right > SCREEN_WIDTH or 
            new_head.top < 0 or new_head.bottom > SCREEN_HEIGHT):
            can_move = False

        if can_move:
            self.last_movement_time = pygame.time.get_ticks()
            self.segments[0] = new_head
            self.update_segments(prev_head)
        else:
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
        
        for i, segment in enumerate(self.segments):
            color = LIGHT_GREEN
            if i == 0:  
                color = (144, 238, 144)  
            pygame.draw.circle(screen, color, (int(segment.centerx), int(segment.centery)), segment_radius)
        
        head_x = self.segments[0].centerx
        head_y = self.segments[0].centery
        
        eye_offset = 3
        pygame.draw.circle(screen, BLACK, (int(head_x - eye_offset), int(head_y)), 2)
        pygame.draw.circle(screen, BLACK, (int(head_x + eye_offset), int(head_y)), 2)
        
        antenna_start = (head_x, head_y - 5)
        pygame.draw.line(screen, LIGHT_GREEN, antenna_start,
                        (head_x - 10, head_y - 10), 2)
        pygame.draw.line(screen, LIGHT_GREEN, antenna_start,
                        (head_x - 8, head_y - 12), 2)
        pygame.draw.line(screen, LIGHT_GREEN, antenna_start,
                        (head_x + 10, head_y - 10), 2)
        pygame.draw.line(screen, LIGHT_GREEN, antenna_start,
                        (head_x + 8, head_y - 12), 2)

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = random.randint(30, 60)
        self.color = random.choice([YELLOW, GREEN, BLUE, RED])
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Caterpillar World Saver")
        self.clock = pygame.time.Clock()
        
        self.score = 0
        self.high_score = 0
        self.stage_requirements = {
            'enemies': lambda stage: min(2 + stage // 2, 10),
            'walls': lambda stage: min(3 + stage // 10, 8),
            'speed_multiplier': lambda stage: 1 + (stage * 0.2),
            'energy_cost': lambda stage: min(20 + stage * 2, 40),
            'bonus_points': lambda stage: stage * 100
        }
        
        self.touch_start = None
        self.touch_current = None
        self.min_swipe_distance = 30
        
        self.sprite_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.particle_group = pygame.sprite.Group()
        
        self.background = pygame.Surface((self.screen_width, self.screen_height))
        self.background.fill(BLACK)
        
        self.last_damage_time = 0
        self.damage_cooldown = 500
        
        self.sounds = {}
        self.load_sounds()
        self.create_victory_sound()
        self.create_game_over_sound()
        
        self.reset_game()
        self.paused = False
        self.game_over = False
        self.game_over_sound_played = False
        self.victory_sound_played = False
        self.celebrating = False
        self.celebration_timer = 0

    def create_victory_sound(self):
        try:
            sample_rate = 44100
            duration = 0.6
            num_samples = int(sample_rate * duration)
            buffer = []
            
            frequencies = [440, 550, 660]
            samples_per_note = num_samples // len(frequencies)
            
            for freq in frequencies:
                t = [i/sample_rate for i in range(samples_per_note)]
                wave = [int(32767 * math.sin(2 * math.pi * freq * x)) for x in t]
                buffer.extend(wave)
            
            stereo = []
            for sample in buffer:
                stereo.extend([sample, sample])
            
            sound_array = bytes([max(min(x, 32767), -32768) & 0xFF for x in stereo])
            self.victory_sound = pygame.mixer.Sound(buffer=sound_array)
            self.victory_sound.set_volume(0.4)
        except Exception as e:
            print(f"Warning: Could not create victory sound: {e}")
            self.victory_sound = None

    def create_game_over_sound(self):
        sample_rate = 44100
        duration = 12.0
        t = numpy.linspace(0, duration, int(sample_rate * duration), False)
        
        base_freqs = [140, 100, 70]
        melody = numpy.zeros_like(t)
        quoaa_times = [0.0, 3.5, 7.0]
        quoaa_durations = [1.5, 2.5, 3.5]
        
        for i, (start_time, base_freq) in enumerate(zip(quoaa_times, base_freqs)):
            quoaa_duration = quoaa_durations[i]
            idx_from = int(start_time * sample_rate)
            idx_to = int((start_time + quoaa_duration) * sample_rate)
            t_quoaa = numpy.linspace(0, quoaa_duration, idx_to - idx_from, False)
            
            decay_rate = 2.0 / (i + 1)
            freq_mod = base_freq + (90 - i * 20) * numpy.exp(-decay_rate * t_quoaa)
            phase = 2 * numpy.pi * numpy.cumsum(freq_mod) / sample_rate
            
            quoaa = numpy.sin(phase)
            
            sub_harmonic = 1.5 - (i * 0.1)
            quoaa += (0.4 + i * 0.1) * numpy.sin(sub_harmonic * phase)
            quoaa += (0.3 - i * 0.05) * numpy.sin(2 * phase)
            quoaa += (0.15 - i * 0.03) * numpy.sin(3 * phase)
            
            decay_env = 1.5 - (i * 0.3)
            envelope = numpy.exp(-decay_env * t_quoaa / quoaa_duration)
            envelope = envelope * (1 - numpy.exp(-(10 - i * 2) * t_quoaa))
            
            melody[idx_from:idx_to] += quoaa * envelope
        
        melody = melody / numpy.max(numpy.abs(melody))
        melody = melody * 0.9
        
        reverb_delay = int(0.2 * sample_rate)
        reverb = numpy.zeros_like(melody)
        reverb[reverb_delay:] = melody[:-reverb_delay] * 0.5
        
        melody = melody + reverb
        
        reverb_delay2 = int(0.4 * sample_rate)
        reverb2 = numpy.zeros_like(melody)
        reverb2[reverb_delay2:] = melody[:-reverb_delay2] * 0.3
        
        melody = melody + reverb2
        
        melody = melody / numpy.max(numpy.abs(melody))
        
        waveform = (melody * 32767).astype(numpy.int16)
        
        stereo = numpy.column_stack([waveform, waveform])
        
        self.game_over_sound = pygame.mixer.Sound(buffer=stereo.tobytes())
        self.game_over_sound.set_volume(0.4)

    def load_sounds(self):
        sound_files = {
            'collision': './assets/collision.wav',
            'convert': './assets/convert.wav',
            'stage_complete': './assets/stage_complete.wav',
            'game_over': './assets/game_over.wav'
        }
        
        for name, path in sound_files.items():
            try:
                sound = pygame.mixer.Sound(path)
                sound.set_volume(0.3)
                self.sounds[name] = sound
            except Exception as e:
                print(f"Warning: Could not load sound {path}: {e}")
                self.sounds[name] = None

    def play_sound(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except:
                pass

    def handle_input(self):
        keys = pygame.key.get_pressed()
        touch_dir_x = 0
        touch_dir_y = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            touch_dir_x = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            touch_dir_x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            touch_dir_y = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            touch_dir_y = 1
            
        if self.touch_start and self.touch_current:
            dx = self.touch_current[0] - self.touch_start[0]
            dy = self.touch_current[1] - self.touch_start[1]
            
            if abs(dx) > self.min_swipe_distance:
                touch_dir_x = 1 if dx > 0 else -1
            if abs(dy) > self.min_swipe_distance:
                touch_dir_y = 1 if dy > 0 else -1
        
        return touch_dir_x, touch_dir_y

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
            elif event.key == pygame.K_r and (self.paused or self.game_over):
                self.reset_game()
                self.paused = False
                self.game_over = False
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  
                if self.paused:
                    self.handle_menu_click(event.pos)
                elif self.game_over:
                    self.handle_game_over_click(event.pos)
                else:
                    self.touch_start = event.pos
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.touch_start = None
                self.touch_current = None
                
        elif event.type == pygame.MOUSEMOTION:
            if self.touch_start:
                self.touch_current = event.pos
                
        elif event.type == pygame.FINGERDOWN:
            x = int(event.x * self.screen_width)
            y = int(event.y * self.screen_height)
            self.touch_start = (x, y)
            
        elif event.type == pygame.FINGERUP:
            self.touch_start = None
            self.touch_current = None
            
        elif event.type == pygame.FINGERMOTION:
            if self.touch_start:
                x = int(event.x * self.screen_width)
                y = int(event.y * self.screen_height)
                self.touch_current = (x, y)
        
        return True

    def reset_game(self):
        self.stage = 1
        self.walls = []
        self.generate_walls()
        self.player = Player()
        self.player.game = self
        self.enemies = []
        self.particles = []
        self.celebrating = False
        self.celebration_timer = 0
        self.game_over = False
        self.game_over_sound_played = False
        self.victory_sound_played = False
        self.spawn_enemies()

    def generate_walls(self):
        self.walls = []
        num_walls = self.stage_requirements['walls'](self.stage)
        
        min_length = 120
        max_length = 200
        wall_thickness = 20
        
        spawn_area = pygame.Rect(50, SCREEN_HEIGHT//2 - 100, 200, 200)
        
        attempts = 0
        while len(self.walls) < num_walls and attempts < 100:
            is_vertical = random.choice([True, False])
            
            if is_vertical:
                height = random.randint(min_length, max_length)
                width = wall_thickness
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(50, SCREEN_HEIGHT - height)
            else:
                width = random.randint(min_length, max_length)
                height = wall_thickness
                x = random.randint(50, SCREEN_WIDTH - width)
                y = random.randint(100, SCREEN_HEIGHT - 100)
            
            new_wall = Wall(x, y, width, height, is_vertical)
            
            overlap = False
            if new_wall.collides_with(spawn_area):
                overlap = True
            
            for wall in self.walls:
                if (new_wall.rect1.colliderect(wall.rect1) or 
                    (new_wall.rect2 and wall.rect2 and 
                     new_wall.rect2.colliderect(wall.rect2))):
                    overlap = True
                    break
            
            if not overlap:
                self.walls.append(new_wall)
            
            attempts += 1

    def spawn_enemies(self):
        self.enemies.clear()
        num_enemies = self.stage_requirements['enemies'](self.stage)
        
        attempts = 0
        while len(self.enemies) < num_enemies and attempts < 100:
            x = random.randint(50, self.screen_width - 50)
            y = random.randint(50, self.screen_height - 50)
            
            valid_position = True
            temp_rect = pygame.Rect(x, y, 40, 40)
            
            for wall in self.walls:
                if wall.collides_with(temp_rect):
                    valid_position = False
                    break
            
            if valid_position:
                player_head = self.player.segments[0]
                dx = x - player_head.x
                dy = y - player_head.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                too_close_to_enemy = False
                for enemy in self.enemies:
                    ex = x - enemy.rect.x
                    ey = y - enemy.rect.y
                    enemy_distance = math.sqrt(ex * ex + ey * ey)
                    if enemy_distance < 100:
                        too_close_to_enemy = True
                        break
                
                if distance > 200 and not too_close_to_enemy:
                    enemy = Enemy(x, y)
                    speed_mult = self.stage_requirements['speed_multiplier'](self.stage)
                    enemy.speed = enemy.base_speed * speed_mult
                    self.enemies.append(enemy)
            
            attempts += 1

    def reset_stage(self):
        self.generate_walls()
        self.spawn_enemies()
        self.player.energy = self.player.max_energy
        
        self.player.speed = self.player.base_speed + (self.stage * 0.2)

    def create_celebration_particles(self):
        for _ in range(100):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            self.particles.append(Particle(x, y))
            
        for enemy in self.enemies:
            if enemy.converted:
                for _ in range(20):
                    x = enemy.rect.centerx + random.randint(-50, 50)
                    y = enemy.rect.centery + random.randint(-50, 50)
                    particle = Particle(x, y)
                    particle.color = random.choice([GREEN, YELLOW])
                    self.particles.append(particle)

    def draw_celebration(self):
        if self.celebrating:
            alpha = int(128 + 64 * math.sin(pygame.time.get_ticks() * 0.01))
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.fill(BLACK)
            overlay.set_alpha(alpha)
            self.screen.blit(overlay, (0, 0))
            
            font = pygame.font.Font(None, 74)
            text = f"Stage {self.stage} Complete!"
            
            glow_colors = [(255, 255, 0, i) for i in range(0, 192, 64)]
            for color in glow_colors:
                text_surface = font.render(text, True, color)
                text_rect = text_surface.get_rect(center=(self.screen_width//2, self.screen_height//2))
                offset = len(glow_colors) - glow_colors.index(color)
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    self.screen.blit(text_surface, 
                                   (text_rect.x + dx * offset, text_rect.y + dy * offset))
            
            text_surface = font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(text_surface, text_rect)
            
            bonus_font = pygame.font.Font(None, 48)
            bonus_text = f"+{self.stage_requirements['bonus_points'](self.stage)} Points!"
            bonus_surface = bonus_font.render(bonus_text, True, YELLOW)
            bonus_rect = bonus_surface.get_rect(center=(self.screen_width//2, 
                                                      self.screen_height//2 + 60))
            self.screen.blit(bonus_surface, bonus_rect)

    def update_particles(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw_energy_bar(self):
        bar_width = 300
        bar_height = 20
        x = (self.screen_width - bar_width) // 2
        y = self.screen_height - bar_height - 10
        
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (x, y, bar_width, bar_height))
        
        energy_width = int((self.player.energy / self.player.max_energy) * bar_width)
        energy_color = (0, 255, 0)
        if self.player.energy < self.player.max_energy * 0.3:
            energy_color = (255, 0, 0)
        elif self.player.energy < self.player.max_energy * 0.6:
            energy_color = (255, 255, 0)
        
        pygame.draw.rect(self.screen, energy_color, 
                        (x, y, energy_width, bar_height))
        
        pygame.draw.rect(self.screen, BLUE, 
                        (x, y, bar_width, bar_height), 2)
        
        font = pygame.font.Font(None, 24)
        energy_text = font.render(f"Energy: {int(self.player.energy)}%", True, BLUE)
        text_rect = energy_text.get_rect()
        text_rect.centerx = x + bar_width // 2
        text_rect.bottom = y - 5
        self.screen.blit(energy_text, text_rect)

    def draw_lives(self):
        heart_width = 20
        heart_spacing = 5
        total_width = (heart_width + heart_spacing) * self.player.lives
        start_x = 10
        y = 70
        
        for i in range(self.player.lives):
            x = start_x + i * (heart_width + heart_spacing)
            pygame.draw.circle(self.screen, RED, (x + 6, y + 6), 6)
            pygame.draw.circle(self.screen, RED, (x + 14, y + 6), 6)
            points = [(x + 10, y + 18), (x, y + 8), (x + 10, y + 2), 
                     (x + 20, y + 8)]
            pygame.draw.polygon(self.screen, RED, points)

    def draw_score(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        high_score_text = font.render(f"High Score: {self.high_score}", True, WHITE)
        stage_text = font.render(f"Stage: {self.stage}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 40))
        self.screen.blit(stage_text, (self.screen_width - 200, 10))

    def handle_collisions(self):
        current_time = pygame.time.get_ticks()
        if not self.celebrating:
            for enemy in self.enemies:
                if not enemy.converted:
                    head_rect = self.player.segments[0]
                    enemy_rect = pygame.Rect(enemy.rect.x, enemy.rect.y, enemy.width, enemy.height)
                    
                    tail_hit = False
                    for segment in self.player.segments[1:]:
                        segment_rect = pygame.Rect(segment.x, segment.y, segment.width, segment.height)
                        if segment_rect.colliderect(enemy_rect):
                            tail_hit = True
                            if current_time - self.last_damage_time >= self.damage_cooldown:
                                if self.player.lose_energy(10):
                                    if self.player.lives <= 0:
                                        self.game_over = True
                                        self.play_sound('game_over')
                                    else:
                                        self.player.reset_position()
                                        self.reset_positions()
                                self.last_damage_time = current_time
                                self.play_sound('collision')
                            break

                    if not tail_hit and head_rect.colliderect(enemy_rect):
                        enemy.converted = True
                        self.play_sound('convert')
                        self.score += 50
                        self.high_score = max(self.score, self.high_score)
                        
                        dx = enemy.rect.centerx - head_rect.centerx
                        dy = enemy.rect.centery - head_rect.centery
                        magnitude = 15
                        angle = math.atan2(dy, dx)
                        enemy.rect.x += math.cos(angle) * magnitude
                        enemy.rect.y += math.sin(angle) * magnitude

            if all(enemy.converted for enemy in self.enemies):
                self.score += self.stage_requirements['bonus_points'](self.stage)
                self.high_score = max(self.score, self.high_score)
                self.stage += 1
                self.celebrating = True
                self.celebration_timer = 60
                self.create_celebration_particles()
                self.play_sound('stage_complete')

    def reset_positions(self):
        self.player.reset_position()
        for enemy in self.enemies:
            enemy.converted = False
            enemy.rect.x = random.randint(50, SCREEN_WIDTH - 50)
            enemy.rect.y = random.randint(50, SCREEN_HEIGHT - 50)

    def handle_menu_click(self, pos):
        if self.paused:
            resume_rect = pygame.Rect(SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2, 100, 40)
            restart_rect = pygame.Rect(SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2 + 60, 100, 40)
            
            if resume_rect.collidepoint(pos):
                self.paused = False
            elif restart_rect.collidepoint(pos):
                self.reset_game()
                self.paused = False

    def handle_game_over_click(self, pos):
        if self.game_over:
            restart_rect = pygame.Rect(SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT*2//3, 100, 40)
            if restart_rect.collidepoint(pos):
                self.reset_game()
                self.game_over = False

async def main():
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if not game.handle_event(event):
                running = False

        if not game.paused and not game.game_over:
            keys = pygame.key.get_pressed()
            touch_dir_x, touch_dir_y = game.handle_input()
            game.player.move(keys, game.walls)
            
            for enemy in game.enemies:
                enemy.move(game.player.segments, game.walls)
            
            game.handle_collisions()
            
            if game.celebrating:
                game.celebration_timer -= 1
                if game.celebration_timer <= 0:
                    game.celebrating = False
                    if game.victory_sound and not game.victory_sound_played:
                        game.victory_sound.play()
                        game.victory_sound_played = True
                    game.reset_stage()

        game.screen.blit(game.background, (0, 0))
        
        for wall in game.walls:
            wall.draw(game.screen)
        
        for enemy in game.enemies:
            enemy.draw(game.screen)
        
        game.player.draw(game.screen)
        
        game.draw_energy_bar()
        game.draw_lives()
        game.draw_score()

        for particle in game.particles:
            particle.draw(game.screen)
        game.update_particles()

        if game.celebrating:
            game.draw_celebration()

        if game.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            game.screen.blit(overlay, (0, 0))
            
            font = pygame.font.Font(None, 74)
            text = font.render("PAUSED", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
            game.screen.blit(text, text_rect)
            
            resume_rect = pygame.Rect(SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2, 100, 40)
            restart_rect = pygame.Rect(SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2 + 60, 100, 40)
            
            pygame.draw.rect(game.screen, GREEN, resume_rect)
            pygame.draw.rect(game.screen, RED, restart_rect)
            
            font = pygame.font.Font(None, 36)
            resume_text = font.render("Resume", True, BLACK)
            restart_text = font.render("Restart", True, BLACK)
            
            resume_text_rect = resume_text.get_rect(center=resume_rect.center)
            restart_text_rect = restart_text.get_rect(center=restart_rect.center)
            
            game.screen.blit(resume_text, resume_text_rect)
            game.screen.blit(restart_text, restart_text_rect)

        elif game.game_over:
            if not game.game_over_sound_played and game.game_over_sound:
                game.game_over_sound.play()
                game.game_over_sound_played = True

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            game.screen.blit(overlay, (0, 0))
            
            font = pygame.font.Font(None, 74)
            text = font.render("GAME OVER", True, RED)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
            game.screen.blit(text, text_rect)
            
            font = pygame.font.Font(None, 48)
            score_text = font.render(f"Stage: {game.stage}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            game.screen.blit(score_text, score_rect)
            
            restart_rect = pygame.Rect(SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT*2//3, 100, 40)
            pygame.draw.rect(game.screen, GREEN, restart_rect)
            
            font = pygame.font.Font(None, 36)
            restart_text = font.render("Restart", True, BLACK)
            restart_text_rect = restart_text.get_rect(center=restart_rect.center)
            game.screen.blit(restart_text, restart_text_rect)

        pygame.display.flip()
        game.clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
