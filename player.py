import pygame

from bullet import Bullet
from settings import (
    GREEN,
    PLAYER_HEIGHT,
    PLAYER_START_Y,
    PLAYER_WIDTH,
    SCREEN_WIDTH,
)


class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = (SCREEN_WIDTH // 2) - (self.width // 2)
        self.y = PLAYER_START_Y

        self.damage_level = 1
        self.speed_level = 1
        self.rate_level = 1
        self.last_shot_time = 0

    @property
    def damage(self):
        return self.damage_level

    @property
    def move_speed(self):
        # The speed upgrade now affects ONLY player movement.
        return 6 + self.speed_level

    @property
    def shoot_cooldown(self):
        return max(100, 400 - (self.rate_level * 50))

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def handle_movement(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.move_speed

        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

    def try_shoot(self, current_time):
        if current_time - self.last_shot_time < self.shoot_cooldown:
            return None

        bullet_x = self.x + (self.width // 2) - 4
        bullet_y = self.y
        self.last_shot_time = current_time
        return Bullet(bullet_x, bullet_y)

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect)
