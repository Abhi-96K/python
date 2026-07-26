"""
Beautiful Snake Game - Mac Compatible
Author: Abhirath-style polished version 😎

Controls:
- Arrow Keys / W A S D : Move
- Space : Pause / Resume
- R : Restart after game over
- Esc : Quit

Install:
    python3 -m venv venv
    source venv/bin/activate
    pip install pygame

Run:
    python snake_game.py
"""

import math
import random
import sys
from dataclasses import dataclass
import os

import pygame

# -----------------------------
# Game Settings
# -----------------------------
WIDTH, HEIGHT = 900, 650
CELL_SIZE = 35  # Larger cells for easier gameplay
FPS = 60
MOVE_DELAY_START = 180  # Slower starting speed
MIN_MOVE_DELAY = 100  # Never gets too fast

GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

# Colors - Bright & Attractive
BG_TOP = (20, 30, 50)
BG_BOTTOM = (40, 60, 90)
GRID_COLOR = (255, 255, 255, 12)
SNAKE_HEAD = (120, 255, 150)  # Bright green
SNAKE_BODY = (60, 220, 120)   # Fresh green
SNAKE_BODY_DARK = (40, 180, 90)
FOOD_COLOR = (255, 100, 150)  # Pink
FOOD_GLOW = (255, 80, 130)
TEXT = (255, 255, 255)
MUTED_TEXT = (180, 200, 220)
DANGER = (255, 100, 100)
GOLD = (255, 220, 120)

pygame.init()
pygame.display.set_caption("Beautiful Snake - Mac Edition")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# High score file
HIGH_SCORE_FILE = os.path.expanduser("~/.snake_highscore")

def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            f.write(str(score))
    except:
        pass

HIGH_SCORE = load_high_score()

try:
    FONT_BIG = pygame.font.SysFont("Avenir Next", 58, bold=True)
    FONT_MED = pygame.font.SysFont("Avenir Next", 28, bold=True)
    FONT_SMALL = pygame.font.SysFont("Avenir Next", 18)
except Exception:
    FONT_BIG = pygame.font.SysFont(None, 58, bold=True)
    FONT_MED = pygame.font.SysFont(None, 28, bold=True)
    FONT_SMALL = pygame.font.SysFont(None, 18)


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    radius: float
    life: float
    color: tuple

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.03
        self.life -= 1
        self.radius *= 0.985

    def draw(self, surface):
        if self.life <= 0 or self.radius <= 0:
            return
        alpha = max(0, min(255, int(255 * (self.life / 45))))
        glow = pygame.Surface((int(self.radius * 4), int(self.radius * 4)), pygame.SRCALPHA)
        pygame.draw.circle(
            glow,
            (*self.color, alpha),
            (glow.get_width() // 2, glow.get_height() // 2),
            int(self.radius),
        )
        surface.blit(glow, (self.x - glow.get_width() // 2, self.y - glow.get_height() // 2))


@dataclass
class Star:
    x: float
    y: float
    size: float
    speed: float
    brightness: float
    
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surface):
        alpha = int(self.brightness * 255)
        pygame.draw.circle(surface, (255, 255, 255, alpha), (int(self.x), int(self.y)), int(self.size))


def lerp(a, b, t):
    return int(a + (b - a) * t)


def draw_vertical_gradient(surface, top_color, bottom_color):
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = (
            lerp(top_color[0], bottom_color[0], t),
            lerp(top_color[1], bottom_color[1], t),
            lerp(top_color[2], bottom_color[2], t),
        )
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))


def draw_soft_circle(surface, x, y, radius, color, alpha):
    glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -4):
        current_alpha = int(alpha * (r / radius) ** 2)
        pygame.draw.circle(glow, (*color, current_alpha), (radius, radius), r)
    surface.blit(glow, (x - radius, y - radius), special_flags=pygame.BLEND_PREMULTIPLIED)


def draw_grid(surface):
    grid = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(grid, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(grid, GRID_COLOR, (0, y), (WIDTH, y))
    surface.blit(grid, (0, 0))


def rounded_rect(surface, rect, color, radius=18, alpha=255):
    layer = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(layer, (*color[:3], alpha), layer.get_rect(), border_radius=radius)
    surface.blit(layer, rect.topleft)


def cell_to_pixel(cell):
    return cell[0] * CELL_SIZE + CELL_SIZE // 2, cell[1] * CELL_SIZE + CELL_SIZE // 2


def random_food(snake):
    while True:
        pos = (random.randint(1, GRID_WIDTH - 2), random.randint(2, GRID_HEIGHT - 2))
        if pos not in snake:
            return pos


def spawn_special_food():
    """Returns (position, points, duration) for special food"""
    food_types = [
        ((255, 215, 0), 5, 5000, "GOLD"),      # Gold - 5 points, 5 seconds
        ((147, 112, 219), 3, 8000, "GEM"),     # Purple gem - 3 points, 8 seconds
        ((0, 255, 255), 2, 10000, "DIAMOND"),  # Cyan diamond - 2 points, 10 seconds
    ]
    return random.choice(food_types)


def draw_text_center(surface, text, font, color, y):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(WIDTH // 2, y))
    surface.blit(rendered, rect)


def spawn_food_particles(particles, food):
    fx, fy = cell_to_pixel(food)
    for _ in range(28):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.2, 4.3)
        particles.append(
            Particle(
                fx,
                fy,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.uniform(2.5, 5.8),
                random.uniform(24, 45),
                random.choice([FOOD_COLOR, GOLD, SNAKE_HEAD]),
            )
        )


def spawn_death_particles(particles, snake):
    for segment in snake:
        sx, sy = cell_to_pixel(segment)
        for _ in range(4):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1.5, 4.8)
            particles.append(
                Particle(
                    sx,
                    sy,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    random.uniform(2, 5),
                    random.uniform(25, 55),
                    random.choice([DANGER, SNAKE_HEAD, SNAKE_BODY]),
                )
            )


def reset_game():
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2), (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2), (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)]
    direction = (1, 0)
    next_direction = (1, 0)
    food = random_food(snake)
    score = 0
    move_delay = MOVE_DELAY_START
    game_over = False
    paused = False
    last_move_time = pygame.time.get_ticks()
    
    # Special food system
    special_food = None
    special_food_spawn_time = 0
    
    # Screen shake
    screen_shake = 0
    shake_offset = (0, 0)
    
    return snake, direction, next_direction, food, score, move_delay, game_over, paused, last_move_time, special_food, special_food_spawn_time, screen_shake, shake_offset


def draw_snake(surface, snake, direction, tick):
    # Simple and clean snake drawing
    for i, segment in enumerate(snake):
        px, py = cell_to_pixel(segment)
        
        # Head is brighter, body fades to darker
        if i == 0:
            color = SNAKE_HEAD
        else:
            t = min(1, i / 5)  # Fade over first 5 segments
            color = (
                lerp(SNAKE_BODY[0], SNAKE_BODY_DARK[0], t),
                lerp(SNAKE_BODY[1], SNAKE_BODY_DARK[1], t),
                lerp(SNAKE_BODY[2], SNAKE_BODY_DARK[2], t),
            )
        
        # Draw rounded rectangle for each segment
        rect = pygame.Rect(segment[0] * CELL_SIZE + 3, segment[1] * CELL_SIZE + 3, CELL_SIZE - 6, CELL_SIZE - 6)
        pygame.draw.rect(surface, color, rect, border_radius=12)
        
        # Small highlight on each segment
        pygame.draw.circle(surface, (255, 255, 255, 40), (px - 4, py - 4), 3)

    # Eyes on head
    hx, hy = cell_to_pixel(snake[0])
    dx, dy = direction
    eye_offset_forward = 6
    eye_side = 5

    if dx != 0:
        eye1 = (hx + dx * eye_offset_forward, hy - eye_side)
        eye2 = (hx + dx * eye_offset_forward, hy + eye_side)
    else:
        eye1 = (hx - eye_side, hy + dy * eye_offset_forward)
        eye2 = (hx + eye_side, hy + dy * eye_offset_forward)

    for eye in (eye1, eye2):
        pygame.draw.circle(surface, (20, 30, 40), eye, 4)
        pygame.draw.circle(surface, (255, 255, 255), (eye[0] - 1, eye[1] - 1), 1)


def draw_food(surface, food, tick, special_food=None):
    fx, fy = cell_to_pixel(food)
    
    # Simple pulsing food
    pulse = 1 + math.sin(tick * 0.008) * 0.15
    
    # Glow
    glow = pygame.Surface((int(50 * pulse), int(50 * pulse)), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*FOOD_GLOW, 80), (glow.get_width() // 2, glow.get_height() // 2), int(20 * pulse))
    surface.blit(glow, (fx - glow.get_width() // 2, fy - glow.get_height() // 2))
    
    # Main food
    pygame.draw.circle(surface, FOOD_COLOR, (fx, fy), int(12 * pulse))
    pygame.draw.circle(surface, (255, 200, 220), (fx - 3, fy - 3), int(4 * pulse))
    
    # Special food if active
    if special_food is not None:
        sf_pos, sf_color, sf_points, sf_duration, sf_name = special_food
        sfx, sfy = cell_to_pixel(sf_pos)
        pulse2 = 1 + math.sin(tick * 0.012) * 0.2
        
        # Glow
        glow2 = pygame.Surface((int(55 * pulse2), int(55 * pulse2)), pygame.SRCALPHA)
        pygame.draw.circle(glow2, (*sf_color, 100), (glow2.get_width() // 2, glow2.get_height() // 2), int(22 * pulse2))
        surface.blit(glow2, (sfx - glow2.get_width() // 2, sfy - glow2.get_height() // 2))
        
        pygame.draw.circle(surface, sf_color, (sfx, sfy), int(14 * pulse2))


def draw_hud(surface, score, move_delay, high_score):
    rounded_rect(surface, pygame.Rect(22, 18, 220, 58), (255, 255, 255), radius=20, alpha=22)
    score_text = FONT_MED.render(f"Score  {score}", True, TEXT)
    surface.blit(score_text, (42, 31))
    
    # High score display
    if high_score > 0:
        hs_text = FONT_SMALL.render(f"Best: {high_score}", True, GOLD)
        surface.blit(hs_text, (42, 58))

    speed = max(1, int((MOVE_DELAY_START - move_delay + 15) / 10))
    speed_text = FONT_SMALL.render(f"Speed Level: {speed}", True, MUTED_TEXT)
    surface.blit(speed_text, (WIDTH - 170, 35))

    hint = FONT_SMALL.render("WASD / Arrows • Space Pause • Esc Quit", True, MUTED_TEXT)
    surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 32))


def main():
    snake, direction, next_direction, food, score, move_delay, game_over, paused, last_move_time, special_food, special_food_spawn_time, screen_shake, shake_offset = reset_game()
    particles = []
    death_particles_spawned = False
    
    # Background stars
    stars = []
    for _ in range(40):
        stars.append(Star(
            random.randint(0, WIDTH),
            random.randint(0, HEIGHT),
            random.uniform(0.5, 1.5),
            random.uniform(0.1, 0.5),
            random.uniform(0.2, 0.6)
        ))
    
    # Game states: "start", "playing", "paused", "game_over"
    game_state = "start"
    current_high_score = HIGH_SCORE
    
    while True:
        dt = clock.tick(FPS)
        tick = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_SPACE:
                    if game_state == "start":
                        game_state = "playing"
                    elif game_state == "playing":
                        paused = not paused
                        if paused:
                            game_state = "paused"
                    elif game_state == "paused":
                        paused = False
                        game_state = "playing"

                if event.key == pygame.K_r and game_state == "game_over":
                    snake, direction, next_direction, food, score, move_delay, game_over, paused, last_move_time, special_food, special_food_spawn_time, screen_shake, shake_offset = reset_game()
                    particles.clear()
                    death_particles_spawned = False
                    game_state = "playing"

                # Movement controls
                if game_state == "playing" and not paused:
                    if event.key in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
                        next_direction = (0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
                        next_direction = (0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
                        next_direction = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                        next_direction = (1, 0)

        # Game logic
        if game_state == "playing" and not paused and not game_over and tick - last_move_time >= move_delay:
            direction = next_direction
            head_x, head_y = snake[0]
            new_head = (head_x + direction[0], head_y + direction[1])

            hit_wall = new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT
            hit_self = new_head in snake

            if hit_wall or hit_self:
                game_over = True
                if not death_particles_spawned:
                    spawn_death_particles(particles, snake)
                    death_particles_spawned = True
            else:
                snake.insert(0, new_head)

                if new_head == food:
                    score += 1
                    spawn_food_particles(particles, food)
                    food = random_food(snake)
                    move_delay = max(MIN_MOVE_DELAY, move_delay - 1)
                else:
                    snake.pop()

            last_move_time = tick

        # Update stars
        for star in stars:
            star.update()

        # Update particles
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0 or particle.radius <= 0.5:
                particles.remove(particle)

        # Drawing
        draw_vertical_gradient(screen, BG_TOP, BG_BOTTOM)
        
        # Draw stars
        for star in stars:
            star.draw(screen)
        
        draw_grid(screen)

        draw_food(screen, food, tick, special_food)
        draw_snake(screen, snake, direction, tick)

        for particle in particles:
            particle.draw(screen)

        draw_hud(screen, score, move_delay, current_high_score)

        # Start screen
        if game_state == "start":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 80))
            screen.blit(overlay, (0, 0))
            
            # Simple title
            draw_text_center(screen, "🐍 SNAKE", FONT_BIG, SNAKE_HEAD, HEIGHT // 2 - 60)
            draw_text_center(screen, "Press SPACE to Start", FONT_MED, TEXT, HEIGHT // 2 + 20)
            draw_text_center(screen, "Arrow Keys or WASD to move", FONT_SMALL, MUTED_TEXT, HEIGHT // 2 + 60)
            
            if current_high_score > 0:
                draw_text_center(screen, f"High Score: {current_high_score}", FONT_SMALL, GOLD, HEIGHT // 2 + 100)

        # Paused screen
        if game_state == "paused":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            draw_text_center(screen, "PAUSED", FONT_BIG, TEXT, HEIGHT // 2 - 20)
            draw_text_center(screen, "Press Space to continue", FONT_MED, MUTED_TEXT, HEIGHT // 2 + 35)

        # Game over screen
        if game_over:
            # Update high score
            if score > current_high_score:
                current_high_score = score
                save_high_score(current_high_score)
            
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))

            rounded_rect(screen, pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 120, 400, 240), (255, 255, 255), radius=25, alpha=25)
            draw_text_center(screen, "GAME OVER", FONT_BIG, DANGER, HEIGHT // 2 - 60)
            draw_text_center(screen, f"Score: {score}", FONT_MED, TEXT, HEIGHT // 2)
            
            if score >= current_high_score and score > 0:
                draw_text_center(screen, "🎉 New High Score! 🎉", FONT_MED, GOLD, HEIGHT // 2 + 40)
                draw_text_center(screen, "Press R to restart", FONT_SMALL, GOLD, HEIGHT // 2 + 80)
            else:
                draw_text_center(screen, f"Best: {current_high_score}", FONT_SMALL, GOLD, HEIGHT // 2 + 40)
                draw_text_center(screen, "Press R to restart", FONT_MED, TEXT, HEIGHT // 2 + 75)
            
            game_state = "game_over"

        pygame.display.flip()


if __name__ == "__main__":
    main()
