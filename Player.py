import pygame
import sys
import math

WIDTH, HEIGHT = 1000, 750
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Two Player Shooter")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
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

    def draw(self, win):
        if self.exploding:
            self.explode(win)
        else:
            pygame.draw.rect(win, self.color, self.rect)
            for bullet in self.bullets:
                pygame.draw.rect(win, self.color, bullet['rect'])

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

    def explode(self, win):
        if self.explosion_frame < explosion_duration:
            radius = explosion_radius * (self.explosion_frame / explosion_duration)
            pygame.draw.circle(win, EXPLOSION_COLOR, self.rect.center, int(radius))
            self.explosion_frame += 1
        else:
            self.exploding = False