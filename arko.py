import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import glfw
import sys
import math

# Initialize Pygame
pygame.init()

WIDTH, HEIGHT = 1000, 750
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Two Player Shooter")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BROWN = (100, 40, 0)
BLUE = (0, 0, 255)
EXPLOSION_COLOR = (255, 165, 0)
GRAY = (200, 200, 200)

# Define player and bullet properties
player_size = 50
player_speed = 5
bullet_speed = 7
explosion_radius = 50
explosion_duration = 30
gravity = 0.5
jump_speed = -15
max_fall_speed = 10

background_image = pygame.image.load("ground.jpg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

class Player:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.bullets = []
        self.health = 3  # Each player starts with 3 health points
        self.exploding = False
        self.explosion_frame = 0
        self.vertical_velocity = 0
        self.on_ground = False

    def draw(self):
        if self.exploding:
            self.explode()
        else:
            pygame.draw.rect(win, self.color, (self.x, self.y, player_size, player_size))
            for bullet in self.bullets:
                pygame.draw.rect(win, self.color, (bullet['x'], bullet['y'], 10, 10))

    def move(self, keys, up, down, left, right, obstacles):
        if not self.exploding:
            # Horizontal movement
            if keys[left]:
                self.x -= player_speed
                if self.x < 0 or self.collide_with_obstacles(obstacles):
                    self.x += player_speed
            if keys[right]:
                self.x += player_speed
                if self.x + player_size > WIDTH or self.collide_with_obstacles(obstacles):
                    self.x -= player_speed

            # Apply gravity
            self.vertical_velocity += gravity
            if self.vertical_velocity > max_fall_speed:
                self.vertical_velocity = max_fall_speed
            self.y += self.vertical_velocity

            # Check for collisions with the ground and obstacles
            self.on_ground = False
            if self.y + player_size > HEIGHT:
                self.y = HEIGHT - player_size
                self.vertical_velocity = 0
                self.on_ground = True
            elif self.collide_with_obstacles(obstacles):
                for obs in obstacles:
                    if self.rect_collide(self.x, self.y, player_size, player_size, obs.x, obs.y, obs.width, obs.height):
                        if self.vertical_velocity > 0:  # Falling
                            self.y = obs.y - player_size
                            self.vertical_velocity = 0
                            self.on_ground = True
                        elif self.vertical_velocity < 0:  # Jumping up
                            self.y = obs.y + obs.height
                            self.vertical_velocity = 0

            # Jumping
            if keys[up] and self.on_ground:
                self.vertical_velocity = jump_speed

    def shoot(self, target_pos):
        if not self.exploding:
            dir_x, dir_y = target_pos[0] - self.x, target_pos[1] - self.y
            distance = math.sqrt(dir_x**2 + dir_y**2)
            if distance == 0:
                dir_x, dir_y = 0, 0
            else:
                dir_x, dir_y = dir_x / distance, dir_y / distance
            bullet = {'x': self.x, 'y': self.y, 'dir': (dir_x, dir_y)}
            self.bullets.append(bullet)

    def handle_bullets(self, opponent, obstacles):
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['dir'][0] * bullet_speed
            bullet['y'] += bullet['dir'][1] * bullet_speed
            if self.rect_collide(bullet['x'], bullet['y'], 10, 10, opponent.x, opponent.y, player_size, player_size):
                self.bullets.remove(bullet)
                opponent.health -= 1
            elif any(self.rect_collide(bullet['x'], bullet['y'], 10, 10, obs.x, obs.y, obs.width, obs.height) for obs in obstacles):
                self.bullets.remove(bullet)
            elif bullet['x'] > WIDTH or bullet['x'] < 0 or bullet['y'] > HEIGHT or bullet['y'] < 0:
                self.bullets.remove(bullet)

    def explode(self):
        if self.explosion_frame < explosion_duration:
            radius = explosion_radius * (self.explosion_frame / explosion_duration)
            pygame.draw.circle(win, EXPLOSION_COLOR, (int(self.x + player_size // 2), int(self.y + player_size // 2)), int(radius))
            self.explosion_frame += 1
        else:
            self.exploding = False

    def rect_collide(self, x1, y1, w1, h1, x2, y2, w2, h2):
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2

    def collide_with_obstacles(self, obstacles):
        return any(self.rect_collide(self.x, self.y, player_size, player_size, obs.x, obs.y, obs.width, obs.height) for obs in obstacles)

class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def draw(self):
        pygame.draw.rect(win, BROWN, (self.x, self.y, self.width, self.height))

def reset_game():
    global player1, player2, game_over, replay_button_rect
    player1 = Player(100, HEIGHT // 2 - player_size // 2, RED)
    player2 = Player(WIDTH - 100 - player_size, HEIGHT // 2 - player_size // 2, BLUE)
    game_over = False
    replay_button_rect = None

def draw_replay_button():
    font = pygame.font.SysFont(None, 50)
    text = font.render("Replay", True, BLACK)
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    pygame.draw.rect(win, GRAY, rect.inflate(20, 20))
    win.blit(text, rect)
    return rect

# Create obstacles
obstacles = [
    Obstacle(100, 300, 200, 10),
    Obstacle(600, 400, 200, 10),
    Obstacle(300, 500, 200, 10),
    Obstacle(50, 550, 200, 10),
    Obstacle(900, 450, 200, 10),
    Obstacle(500, 700, 200, 10),
    Obstacle(800, 600, 200, 10),
    Obstacle(500, 250, 200, 10),
    Obstacle(800, 150, 200, 10),
    Obstacle(200, 100, 200, 10)
]

# Initialize game state
reset_game()

# Main game loop
clock = pygame.time.Clock()

while True:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN and not game_over:
            if event.key == K_SPACE:
                player1.shoot((player2.x + player_size // 2, player2.y + player_size // 2))
            if event.key == K_RETURN:
                player2.shoot((player1.x + player_size // 2, player1.y + player_size // 2))
        if event.type == MOUSEBUTTONDOWN and game_over:
            if replay_button_rect and replay_button_rect.collidepoint(event.pos):
                reset_game()

    keys = pygame.key.get_pressed()

    if not game_over:
        player1.move(keys, K_w, K_s, K_a, K_d, obstacles)
        player2.move(keys, K_UP, K_DOWN, K_LEFT, K_RIGHT, obstacles)

        player1.handle_bullets(player2, obstacles)
        player2.handle_bullets(player1, obstacles)

    win.blit(background_image, (0, 0))

    player1.draw()
    player2.draw()
    for obstacle in obstacles:
        obstacle.draw()

    pygame.display.update()

    if player1.health <= 0 and not player1.exploding:
        player1.exploding = True
        player1.explosion_frame = 0
    if player2.health <= 0 and not player2.exploding:
        player2.exploding = True
        player2.explosion_frame = 0

    if player1.health <= 0 and player1.explosion_frame >= explosion_duration:
        print("Player 2 Wins!")
        game_over = True
    if player2.health <= 0 and player2.explosion_frame >= explosion_duration:
        print("Player 1 Wins!")
        game_over = True
