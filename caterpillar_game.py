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

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = random.randint(30, 60)  # frames
        self.color = random.choice([YELLOW, GREEN, BLUE, RED])
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # gravity
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Caterpillar World Saver")
        self.clock = pygame.time.Clock()
        self.reset_game()
        self.create_victory_sound()
        self.create_game_over_sound()
        self.paused = False
        self.game_over = False
        self.last_damage_time = 0
        self.damage_cooldown = 500  # 500ms cooldown between damage

    def reset_game(self):
        self.stage = 1
        self.walls = []
        self.generate_walls()
        self.player = Player()
        self.player.game = self  # Add reference to game
        self.enemies = []
        self.particles = []
        self.celebrating = False
        self.celebration_timer = 0
        self.game_over = False
        self.game_over_sound_played = False  # Reset the sound played flag
        self.spawn_enemies()

    def create_victory_sound(self):
        # Create a more musical victory sound
        sample_rate = 44100
        duration = 0.6  # seconds
        t = numpy.linspace(0, duration, int(sample_rate * duration))
        
        # Create a pleasant chord progression
        frequencies = [
            [392, 523.25, 659.25],  # G4, C5, E5 (C major)
            [440, 554.37, 698.46],  # A4, C#5, F5 (F major)
            [523.25, 659.25, 783.99]  # C5, E5, G5 (C major higher)
        ]
        
        # Create the waveform with envelope
        waveform = numpy.zeros_like(t)
        segment_duration = duration / len(frequencies)
        
        for i, chord in enumerate(frequencies):
            # Time segment for this chord
            start = int(i * segment_duration * sample_rate)
            end = int((i + 1) * segment_duration * sample_rate)
            segment_t = t[start:end]
            
            # Create envelope for smooth transitions
            attack = 0.1
            decay = 0.3
            envelope = numpy.ones_like(segment_t)
            attack_samples = int(attack * len(segment_t))
            decay_samples = int(decay * len(segment_t))
            envelope[:attack_samples] = numpy.linspace(0, 1, attack_samples)
            envelope[-decay_samples:] = numpy.linspace(1, 0, decay_samples)
            
            # Add frequencies with envelope
            segment_wave = numpy.zeros_like(segment_t)
            for freq in chord:
                segment_wave += numpy.sin(2 * numpy.pi * freq * segment_t)
            segment_wave *= envelope
            waveform[start:end] = segment_wave
        
        # Normalize and convert to 16-bit integers
        waveform = (waveform * 32767 / numpy.max(numpy.abs(waveform))).astype(numpy.int16)
        
        # Convert to stereo
        stereo = numpy.column_stack([waveform, waveform])
        
        # Create sound from the array
        self.victory_sound = pygame.mixer.Sound(buffer=stereo.tobytes())
        self.victory_sound.set_volume(0.4)

    def create_game_over_sound(self):
        # Create a quoaa-like RIP sound with descending pitch and increasing duration
        sample_rate = 44100
        duration = 12.0  # Total duration doubled
        t = numpy.linspace(0, duration, int(sample_rate * duration), False)
        
        # Base frequencies for each quoaa (getting lower)
        base_freqs = [140, 100, 70]  # Each quoaa starts lower
        
        # Create three quoaa sounds with increasing durations
        melody = numpy.zeros_like(t)
        quoaa_times = [0.0, 3.5, 7.0]  # More space between quoaas
        quoaa_durations = [1.5, 2.5, 3.5]  # Each quoaa lasts longer
        
        for i, (start_time, base_freq) in enumerate(zip(quoaa_times, base_freqs)):
            # Time array for this quoaa
            quoaa_duration = quoaa_durations[i]
            idx_from = int(start_time * sample_rate)
            idx_to = int((start_time + quoaa_duration) * sample_rate)
            t_quoaa = numpy.linspace(0, quoaa_duration, idx_to - idx_from, False)
            
            # Frequency modulation with slower drop for longer quoaas
            decay_rate = 2.0 / (i + 1)  # Slower decay for each subsequent quoaa
            freq_mod = base_freq + (90 - i * 20) * numpy.exp(-decay_rate * t_quoaa)
            phase = 2 * numpy.pi * numpy.cumsum(freq_mod) / sample_rate
            
            # Create the quoaa sound
            quoaa = numpy.sin(phase)
            
            # Add deeper harmonics (more for later quoaas)
            sub_harmonic = 1.5 - (i * 0.1)  # Lower sub-harmonics for each quoaa
            quoaa += (0.4 + i * 0.1) * numpy.sin(sub_harmonic * phase)  # Stronger sub-harmonics
            quoaa += (0.3 - i * 0.05) * numpy.sin(2 * phase)
            quoaa += (0.15 - i * 0.03) * numpy.sin(3 * phase)
            
            # Slower amplitude envelope for each quoaa
            decay_env = 1.5 - (i * 0.3)  # Slower decay for each quoaa
            envelope = numpy.exp(-decay_env * t_quoaa / quoaa_duration)
            envelope = envelope * (1 - numpy.exp(-(10 - i * 2) * t_quoaa))  # Softer attack
            
            # Add to melody
            melody[idx_from:idx_to] += quoaa * envelope
        
        # Normalize and amplify
        melody = melody / numpy.max(numpy.abs(melody))
        melody = melody * 0.9  # Prevent clipping
        
        # Add more reverb effect for spookier sound
        reverb_delay = int(0.2 * sample_rate)  # 200ms delay
        reverb = numpy.zeros_like(melody)
        reverb[reverb_delay:] = melody[:-reverb_delay] * 0.5  # Stronger reverb
        melody = melody + reverb
        
        # Second reverb layer for more depth
        reverb_delay2 = int(0.4 * sample_rate)  # 400ms delay
        reverb2 = numpy.zeros_like(melody)
        reverb2[reverb_delay2:] = melody[:-reverb_delay2] * 0.3
        melody = melody + reverb2
        
        # Third reverb layer for extra long tail
        reverb_delay3 = int(0.6 * sample_rate)  # 600ms delay
        reverb3 = numpy.zeros_like(melody)
        reverb3[reverb_delay3:] = melody[:-reverb_delay3] * 0.2
        melody = melody + reverb3
        
        # Normalize again after adding reverb
        melody = melody / numpy.max(numpy.abs(melody))
        melody = melody * 0.9
        
        # Convert to 16-bit integer samples
        melody = numpy.int16(melody * 32767)
        
        # Create stereo sound with increasing delay for more depth
        stereo_delays = [int(0.02 * sample_rate), int(0.03 * sample_rate), int(0.04 * sample_rate)]
        right_channel = numpy.zeros_like(melody)
        
        for i, delay in enumerate(stereo_delays):
            start_idx = int(quoaa_times[i] * sample_rate)
            end_idx = int((quoaa_times[i] + quoaa_durations[i]) * sample_rate)
            if i < len(quoaa_times) - 1:
                next_start = int(quoaa_times[i + 1] * sample_rate)
            else:
                next_start = len(melody)
            
            segment = numpy.zeros_like(melody[start_idx:next_start])
            segment_len = min(len(melody[start_idx + delay:]), end_idx - start_idx)
            segment[:segment_len] = melody[start_idx:start_idx + segment_len]
            right_channel[start_idx:next_start] = segment
        
        stereo = numpy.vstack((melody, right_channel)).T
        
        self.game_over_sound = pygame.mixer.Sound(buffer=stereo.tobytes())
        self.game_over_sound.set_volume(1.0)  # Full volume for the effect

    def draw_menu_button(self, text, x, y, width=100, height=40):
        button_rect = pygame.Rect(x, y, width, height)
        mouse_pos = pygame.mouse.get_pos()
        button_color = LIGHT_GREEN if button_rect.collidepoint(mouse_pos) else GREEN
        
        pygame.draw.rect(self.screen, button_color, button_rect)
        pygame.draw.rect(self.screen, BLUE, button_rect, 2)
        
        font = pygame.font.Font(None, 32)
        text_surface = font.render(text, True, BLUE)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
        
        return button_rect

    def handle_menu_click(self, pos):
        # Check pause button
        pause_rect = pygame.Rect(WINDOW_WIDTH - 110, 10, 100, 40)
        if pause_rect.collidepoint(pos):
            self.paused = not self.paused
            return True
            
        # Check restart button (only check when paused)
        if self.paused:
            restart_rect = pygame.Rect(WINDOW_WIDTH - 110, 60, 100, 40)
            if restart_rect.collidepoint(pos):
                self.reset_game()
                self.paused = False
                return True
        
        return False

    def draw_pause_screen(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(WHITE)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Draw "PAUSED" text
        font = pygame.font.Font(None, 74)
        text = font.render("PAUSED", True, BLUE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        self.screen.blit(text, text_rect)
        
        # Draw restart button
        self.draw_menu_button("Restart", WINDOW_WIDTH - 110, 60)

    def create_celebration_particles(self):
        # Create particles around the player
        for _ in range(50):
            self.particles.append(Particle(
                random.randint(0, WINDOW_WIDTH),
                random.randint(0, WINDOW_HEIGHT)
            ))

    def update_particles(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw_celebration(self):
        # Draw celebration text
        font = pygame.font.Font(None, 74)
        text = font.render(f"Stage {self.stage} Complete!", True, YELLOW)
        text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        
        # Add glow effect
        glow_surf = pygame.Surface((text_rect.width + 20, text_rect.height + 20))
        glow_surf.fill(WHITE)
        glow_surf.set_alpha(int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 50))
        self.screen.blit(glow_surf, glow_surf.get_rect(center=text_rect.center))
        self.screen.blit(text, text_rect)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)

    def generate_walls(self):
        self.walls = []
        num_walls = min(3 + self.stage // 10, 8)  # More walls as stages progress, max 8
        
        min_length = 120  # Minimum wall length
        max_length = 200  # Maximum wall length
        wall_thickness = 20  # Thin walls
        
        # Create walls avoiding player spawn area
        spawn_area = pygame.Rect(50, WINDOW_HEIGHT//2 - 100, 200, 200)
        
        attempts = 0
        while len(self.walls) < num_walls and attempts < 100:
            is_vertical = random.choice([True, False])
            
            if is_vertical:
                height = random.randint(min_length, max_length)
                width = wall_thickness
                x = random.randint(0, WINDOW_WIDTH - width - height//3)  # Account for L shape
                y = random.randint(0, WINDOW_HEIGHT - height)
            else:
                width = random.randint(min_length, max_length)
                height = wall_thickness
                x = random.randint(0, WINDOW_WIDTH - width)
                y = random.randint(0, WINDOW_HEIGHT - height - width//3)  # Account for L shape
            
            new_wall = Wall(x, y, width, height, is_vertical)
            
            # Check if wall overlaps with spawn area or other walls
            overlap = False
            if new_wall.collides_with(spawn_area):
                overlap = True
            
            for wall in self.walls:
                if (new_wall.collides_with(wall.rect1) or 
                    (wall.rect2 and new_wall.collides_with(wall.rect2))):
                    overlap = True
                    break
            
            if not overlap:
                self.walls.append(new_wall)
            
            attempts += 1

    def spawn_enemies(self):
        self.enemies.clear()
        num_enemies = self.stage + 1
        self.player.update_speed(self.stage)
        
        for _ in range(num_enemies):
            while True:
                x = random.randint(0, WINDOW_WIDTH - 40)
                y = random.randint(0, WINDOW_HEIGHT - 40)
                enemy = Enemy(x, y)
                
                # Check if enemy spawns on a wall
                valid_position = True
                for wall in self.walls:
                    if wall.collides_with(enemy.rect):
                        valid_position = False
                        break
                
                if valid_position:
                    self.enemies.append(enemy)
                    break

    def reset_stage(self):
        self.player.lives = 8
        self.enemies.clear()
        num_enemies = self.stage + 1
        for _ in range(num_enemies):
            while True:
                x = random.randint(0, WINDOW_WIDTH - 40)
                y = random.randint(0, WINDOW_HEIGHT - 40)
                enemy = Enemy(x, y)
                
                # Check if enemy spawns on a wall
                valid_position = True
                for wall in self.walls:
                    if wall.collides_with(enemy.rect):
                        valid_position = False
                        break
                
                if valid_position:
                    self.enemies.append(enemy)
                    break

    def handle_collisions(self):
        current_time = pygame.time.get_ticks()
        for enemy in self.enemies:
            if not enemy.converted:
                head_rect = self.player.get_head_rect()
                tail_rect = self.player.get_tail_rect()

                tail_hit = False
                for i in range(1, len(self.player.segments)):
                    seg_x, seg_y = self.player.segments[i].center
                    seg_rect = pygame.Rect(seg_x - 8, seg_y - 8, 16, 16)
                    if seg_rect.colliderect(enemy.rect):
                        tail_hit = True
                        break

                if tail_hit:
                    # Only apply damage if cooldown has passed
                    if current_time - self.last_damage_time >= self.damage_cooldown:
                        if self.player.lose_energy(10):  # Returns True if life was lost
                            if self.player.lives <= 0:
                                self.game_over = True
                                if not hasattr(self, 'game_over_sound_played'):
                                    self.game_over_sound_played = False
                                if not self.game_over_sound_played:
                                    self.game_over_sound.play()
                                    self.game_over_sound_played = True
                        self.last_damage_time = current_time
                elif head_rect.colliderect(enemy.rect):
                    enemy.converted = True
                    # Push enemy away from head
                    dx = enemy.rect.centerx - head_rect.centerx
                    dy = enemy.rect.centery - head_rect.centery
                    magnitude = 15
                    angle = math.atan2(dy, dx)
                    enemy.rect.x += math.cos(angle) * magnitude
                    enemy.rect.y += math.sin(angle) * magnitude

    def draw_energy_bar(self):
        # Draw energy bar background
        bar_width = 300
        bar_height = 20
        x = (WINDOW_WIDTH - bar_width) // 2  # Center horizontally
        y = WINDOW_HEIGHT - bar_height - 10  # Bottom of screen with 10px padding
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (x, y, bar_width, bar_height))
        
        # Draw current energy
        energy_width = int((self.player.energy / self.player.max_energy) * bar_width)
        energy_color = (0, 255, 0)  # Green
        if self.player.energy < self.player.max_energy * 0.3:  # Below 30%
            energy_color = (255, 0, 0)  # Red
        elif self.player.energy < self.player.max_energy * 0.6:  # Below 60%
            energy_color = (255, 255, 0)  # Yellow
            
        pygame.draw.rect(self.screen, energy_color, 
                        (x, y, energy_width, bar_height))
        
        # Draw border
        pygame.draw.rect(self.screen, BLUE, 
                        (x, y, bar_width, bar_height), 2)

        # Draw energy text
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
        y = 45  # Moved below stage text
        
        for i in range(self.player.lives):
            x = start_x + i * (heart_width + heart_spacing)
            # Draw heart shape
            pygame.draw.circle(self.screen, RED, (x + 6, y + 6), 6)
            pygame.draw.circle(self.screen, RED, (x + 14, y + 6), 6)
            points = [(x + 10, y + 18), (x, y + 8), (x + 10, y + 2), 
                     (x + 20, y + 8)]
            pygame.draw.polygon(self.screen, RED, points)

    def draw_game_over(self):
        if not hasattr(self, 'game_over_sound_played'):
            self.game_over_sound_played = False
            
        if not self.game_over_sound_played:
            self.game_over_sound.play()
            self.game_over_sound_played = True
            
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(WHITE)
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        
        # Draw "GAME OVER" text
        font = pygame.font.Font(None, 74)
        text = font.render("GAME OVER", True, RED)
        text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 50))
        self.screen.blit(text, text_rect)
        
        # Draw score
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"Stage Reached: {self.stage}", True, BLUE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 20))
        self.screen.blit(score_text, score_rect)
        
        # Draw restart button
        button_rect = self.draw_menu_button("Restart Game", 
                                          WINDOW_WIDTH/2 - 100, 
                                          WINDOW_HEIGHT/2 + 80,
                                          200, 50)
        return button_rect

    def handle_game_over_click(self, pos):
        if self.game_over:
            button_rect = pygame.Rect(WINDOW_WIDTH/2 - 100, 
                                    WINDOW_HEIGHT/2 + 80,
                                    200, 50)
            if button_rect.collidepoint(pos):
                self.reset_game()
                return True
        return False

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.handle_game_over_click(event.pos):
                            continue
                        if self.handle_menu_click(event.pos):
                            continue

            if not self.paused and not self.game_over:
                if self.celebrating:
                    self.celebration_timer -= 1
                    self.update_particles()
                    if self.celebration_timer <= 0:
                        self.celebrating = False
                        self.generate_walls()  # Generate new walls for next stage
                        self.spawn_enemies()
                else:
                    keys = pygame.key.get_pressed()
                    self.player.move(keys, self.walls)

                    for enemy in self.enemies:
                        enemy.move(self.player.segments, self.walls)

                    self.handle_collisions()

                    if all(enemy.converted for enemy in self.enemies):
                        self.stage += 1
                        if self.stage > 155:
                            print("Congratulations! You've completed all stages!")
                            running = False
                        else:
                            # Start celebration
                            self.celebrating = True
                            self.celebration_timer = 90  # 1.5 seconds at 60 FPS
                            self.create_celebration_particles()
                            self.victory_sound.play()

            self.screen.fill(WHITE)
            
            # Draw walls
            for wall in self.walls:
                wall.draw(self.screen)
            
            if self.celebrating:
                self.draw_celebration()
            
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)

            # Draw HUD
            font = pygame.font.Font(None, 36)
            stage_text = font.render(f"Stage: {self.stage}", True, BLUE)
            self.screen.blit(stage_text, (10, 10))
            self.draw_lives()
            self.draw_energy_bar()
            speed_multiplier = min(2.0, 1.0 + (self.stage // 10) * 0.05)
            speed_text = font.render(f"Speed: {speed_multiplier:.2f}x", True, BLUE)
            
            self.screen.blit(speed_text, (10, 130))
            
            # Draw pause button
            self.draw_menu_button("Pause", WINDOW_WIDTH - 110, 10)
            
            # Draw pause screen if paused
            if self.paused:
                self.draw_pause_screen()

            if self.game_over:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
