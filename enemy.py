import random

import pygame

from settings import ENEMY_SIZE, RED, SCREEN_WIDTH, WHITE


class Enemy:
    def __init__(self, level):
        self.x = float(random.randint(10, SCREEN_WIDTH - ENEMY_SIZE - 10))
        self.y = float(-ENEMY_SIZE)
        self.max_health = random.randint(level, level * 3)
        self.health = self.max_health
        self.fall_speed = 2 + (level * 0.3)

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), ENEMY_SIZE, ENEMY_SIZE)

    def update(self):
        self.y += self.fall_speed

    def take_damage(self, amount):
        self.health -= amount

    def is_dead(self):
        return self.health <= 0

    def draw(self, screen, font):
        pygame.draw.rect(screen, RED, self.rect)

        hp_text = font.render(str(self.health), True, WHITE)
        text_x = self.x + (ENEMY_SIZE / 2) - (hp_text.get_width() / 2)
        text_y = self.y + (ENEMY_SIZE / 2) - (hp_text.get_height() / 2)
        screen.blit(hp_text, (int(text_x), int(text_y)))
