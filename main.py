import pygame
import sys
import math
from Obstacle import *
from Player import *

pygame.init()

WIDTH, HEIGHT = 1000, 750
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Two Player Shooter")

background_image = pygame.image.load("ground.jpg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

obstacles = [
    Obstacle(100, 300, 200, 10),
    Obstacle(600, 400, 200, 10),
    Obstacle(300, 500, 200, 10),
    Obstacle(50, 550, 200, 10),
    Obstacle(900, 450,200,10),
    Obstacle(500, 700, 200, 10),
    Obstacle(800, 600, 200, 10),
    Obstacle(500, 250, 200, 10),
    Obstacle(800,150,200,10),
    Obstacle(200,100,200,10)

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

    win.blit(background_image, (0, 0))

    # Draw everything
    player1.draw(win)
    player2.draw(win)
    for obstacle in obstacles:
        obstacle.draw(win)

    # Display health
    font = pygame.font.SysFont(None, 36)
    health_text1 = font.render(f'Health: {player1.health}', True, BLACK)
    health_text2 = font.render(f'Health: {player2.health}', True, BLACK)
    win.blit(health_text1, (10, 10))
    win.blit(health_text2, (WIDTH - 150, 10))

    if game_over:
        replay_button_rect = draw_replay_button(win)

    pygame.display.update()

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

