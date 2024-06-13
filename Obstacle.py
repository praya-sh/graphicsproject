import pygame
import sys
import math

BLACK = (0, 0, 0)
BROWN = (100, 40, 0)

class Obstacle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        
    def draw(self, win):
        pygame.draw.rect(win, BROWN, self.rect)