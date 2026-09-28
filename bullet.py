import pygame

from settings import BULLET_HEIGHT, BULLET_SPEED, BULLET_WIDTH, YELLOW


class Bullet:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.speed = BULLET_SPEED

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), BULLET_WIDTH, BULLET_HEIGHT)

    def update(self):
        self.y -= self.speed

    def is_off_screen(self):
        return self.y + BULLET_HEIGHT < 0

    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, self.rect)
