import pygame
import sys
import math
from OpenGL.GL import *
from OpenGL.GLU import *

# Initialize pygame
pygame.init()

WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
pygame.display.set_caption("Two Player Shooter")

# Initialize OpenGL
glViewport(0, 0, WIDTH, HEIGHT)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluOrtho2D(0, WIDTH, HEIGHT, 0)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glEnable(GL_TEXTURE_2D)

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (1.0, 0.0, 0.0)
BLUE = (0.0, 0.0, 1.0)
EXPLOSION_COLOR = (1.0, 0.65, 0.0)
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

# Load the background image as a texture
background_image = pygame.image.load("ground.jpg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
background_texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, background_texture)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
background_data = pygame.image.tostring(background_image, "RGBA", 1)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, WIDTH, HEIGHT, 0, GL_RGBA, GL_UNSIGNED_BYTE, background_data)

class Player:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, player_size, player_size)
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
            glColor3f(*self.color)
            glBegin(GL_QUADS)
            glVertex2f(self.rect.x, self.rect.y)
            glVertex2f(self.rect.x + player_size, self.rect.y)
            glVertex2f(self.rect.x + player_size, self.rect.y + player_size)
            glVertex2f(self.rect.x, self.rect.y + player_size)
            glEnd()
            for bullet in self.bullets:
                glColor3f(*self.color)
                glBegin(GL_QUADS)
                glVertex2f(bullet['rect'].x, bullet['rect'].y)
                glVertex2f(bullet['rect'].x + 10, bullet['rect'].y)
                glVertex2f(bullet['rect'].x + 10, bullet['rect'].y + 5)
                glVertex2f(bullet['rect'].x, bullet['rect'].y + 5)
                glEnd()

    def move(self, keys, up, down, left, right, obstacles):
        if not self.exploding:
            # Horizontal movement
            if keys[left]:
                self.rect.x -= player_speed
                if self.rect.x < 0 or self.rect.collidelist(obstacles) != -1:
                    self.rect.x += player_speed
            if keys[right]:
                self.rect.x += player_speed
                if self.rect.x + player_size > WIDTH or self.rect.collidelist(obstacles) != -1:
                    self.rect.x -= player_speed

            # Apply gravity
            self.vertical_velocity += gravity
            if self.vertical_velocity > max_fall_speed:
                self.vertical_velocity = max_fall_speed
            self.rect.y += self.vertical_velocity

            # Check for collisions with the ground and obstacles
            self.on_ground = False
            if self.rect.y + player_size > HEIGHT:
                self.rect.y = HEIGHT - player_size
                self.vertical_velocity = 0
                self.on_ground = True
            elif self.rect.collidelist(obstacles) != -1:
                for obs in obstacles:
                    if self.rect.colliderect(obs):
                        if self.vertical_velocity > 0:  # Falling
                            self.rect.bottom = obs.top
                            self.vertical_velocity = 0
                            self.on_ground = True
                        elif self.vertical_velocity < 0:  # Jumping up
                            self.rect.top = obs.bottom
                            self.vertical_velocity = 0

            # Jumping
            if keys[up] and self.on_ground:
                self.vertical_velocity = jump_speed

    def shoot(self, target_pos):
        if not self.exploding:
            bullet_rect = pygame.Rect(self.rect.centerx, self.rect.centery, 10, 5)
            dir_x, dir_y = target_pos[0] - self.rect.centerx, target_pos[1] - self.rect.centery
            distance = math.sqrt(dir_x**2 + dir_y**2)
            if distance == 0:
                dir_x, dir_y = 0, 0
            else:
                dir_x, dir_y = dir_x / distance, dir_y / distance
            bullet = {'rect': bullet_rect, 'dir': (dir_x, dir_y)}
            self.bullets.append(bullet)

    def handle_bullets(self, opponent, obstacles):
        for bullet in self.bullets[:]:
            bullet['rect'].x += bullet['dir'][0] * bullet_speed
            bullet['rect'].y += bullet['dir'][1] * bullet_speed
            if bullet['rect'].colliderect(opponent.rect):
                self.bullets.remove(bullet)
                opponent.health -= 1
            elif bullet['rect'].collidelist(obstacles) != -1:
                self.bullets.remove(bullet)
            elif bullet['rect'].x > WIDTH or bullet['rect'].x < 0 or bullet['rect'].y > HEIGHT or bullet['rect'].y < 0:
                self.bullets.remove(bullet)

    def explode(self):
        if self.explosion_frame < explosion_duration:
            radius = explosion_radius * (self.explosion_frame / explosion_duration)
            glColor3f(*EXPLOSION_COLOR)
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(self.rect.centerx, self.rect.centery)
            for angle in range(0, 361, 10):
                x = self.rect.centerx + math.cos(math.radians(angle)) * radius
                y = self.rect.centery + math.sin(math.radians(angle)) * radius
                glVertex2f(x, y)
            glEnd()
            self.explosion_frame += 1
        else:
            self.exploding = False

class Obstacle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        
    def draw(self):
        glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_QUADS)
        glVertex2f(self.rect.x, self.rect.y)
        glVertex2f(self.rect.x + self.rect.width, self.rect.y)
        glVertex2f(self.rect.x + self.rect.width, self.rect.y + self.rect.height)
        glVertex2f(self.rect.x, self.rect.y + self.rect.height)
        glEnd()

# Create obstacles
obstacles = [
    Obstacle(100, 300, 200, 10),
    Obstacle(600, 500, 200, 10),
    Obstacle(300, 500, 200, 10)
]

def reset_game():
    global player1, player2, game_over, replay_button_rect
    player1 = Player(100, HEIGHT // 2 - player_size // 2, RED)
    player2 = Player(WIDTH - 100 - player_size, HEIGHT // 2 - player_size // 2, BLUE)
    game_over = False
    replay_button_rect = None

def draw_replay_button(win):
    font = pygame.font.SysFont(None, 50)
    text = font.render("Replay", True, BLACK)
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    pygame.draw.rect(win, GRAY, rect.inflate(20, 20))
    win.blit(text, rect)
    return rect

# Initialize game state
reset_game()

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)  
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_SPACE:
                player1.shoot((player2.rect.centerx, player2.rect.centery))
            if event.key == pygame.K_RETURN:
                player2.shoot((player1.rect.centerx, player1.rect.centery))
        if event.type == pygame.MOUSEBUTTONDOWN and game_over:
            if replay_button_rect and replay_button_rect.collidepoint(event.pos):
                reset_game()

    # Get key presses
    keys = pygame.key.get_pressed()
    if not game_over:
        player1.move(keys, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, [obs.rect for obs in obstacles])
        player2.move(keys, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, [obs.rect for obs in obstacles])

        # Handle bullets and check for collisions
        player1.handle_bullets(player2, [obs.rect for obs in obstacles])
        player2.handle_bullets(player1, [obs.rect for obs in obstacles])

    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT)

    # Draw the background image
    glBindTexture(GL_TEXTURE_2D, background_texture)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(0, 0)
    glTexCoord2f(1, 0)
    glVertex2f(WIDTH, 0)
    glTexCoord2f(1, 1)
    glVertex2f(WIDTH, HEIGHT)
    glTexCoord2f(0, 1)
    glVertex2f(0, HEIGHT)
    glEnd()

    # Draw everything with OpenGL
    player1.draw()
    player2.draw()

    # Draw obstacles using OpenGL
    for obstacle in obstacles:
        obstacle.draw()

    # Display health using Pygame
    font = pygame.font.SysFont(None, 36)
    health_text1 = font.render(f'Health: {player1.health}', True, BLACK)
    health_text2 = font.render(f'Health: {player2.health}', True, BLACK)
    win.blit(health_text1, (10, 10))
    win.blit(health_text2, (WIDTH - 150, 10))

    if game_over:
        replay_button_rect = draw_replay_button(win)

    # Swap the buffers
    pygame.display.flip()

    # Check for game over and trigger explosion
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

pygame.quit()
sys.exit()
