import random

import pygame

from enemy import Enemy
from player import Player
from settings import (
    BACKGROUND,
    BUTTON,
    DARK_GREEN,
    FPS,
    GOLD,
    GREEN,
    LIGHT_GRAY,
    PANEL,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)


class Game:
    PLAYING = "PLAYING"
    WAVE_CLEARED = "WAVE_CLEARED"
    WAVE_LOST = "WAVE_LOST"
    SHOP = "SHOP"

    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Systems-Driven Upgrade Game")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(None, 36)
        self.big_font = pygame.font.SysFont(None, 64)
        self.enemy_font = pygame.font.SysFont(None, 24)
        self.shop_font = pygame.font.SysFont(None, 28)

        self.player = Player()
        self.bullets = []
        self.enemies = []

        self.coins = 0
        self.current_level = 1
        self.enemies_killed_this_level = 0
        self.enemies_required_for_next_level = 5
        self.enemy_spawn_timer = 0

        self.game_state = self.PLAYING
        self.last_result = None  # "CLEARED" or "LOST"
        self.running = True

        self.damage_button = pygame.Rect(200, 200, 400, 50)
        self.speed_button = pygame.Rect(200, 270, 400, 50)
        self.rate_button = pygame.Rect(200, 340, 400, 50)
        self.continue_button = pygame.Rect(250, 430, 300, 50)
        self.result_button = pygame.Rect(250, 390, 300, 55)

    # -----------------------------
    # Derived values / progression
    # -----------------------------
    @property
    def damage_upgrade_cost(self):
        return self.player.damage_level * 10

    @property
    def speed_upgrade_cost(self):
        return self.player.speed_level * 8

    @property
    def rate_upgrade_cost(self):
        return self.player.rate_level * 12

    @property
    def spawn_rate(self):
        return max(800, 2000 - (self.current_level * 150))

    # -----------------------------
    # Main loop
    # -----------------------------
    def run(self):
        while self.running:
            current_time = pygame.time.get_ticks()
            self.handle_events(current_time)

            if self.game_state == self.PLAYING:
                self.update_playing(current_time)

            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

    # -----------------------------
    # Input / events
    # -----------------------------
    def handle_events(self, current_time):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
                continue

            mouse_pos = event.pos

            if self.game_state in (self.WAVE_CLEARED, self.WAVE_LOST):
                if self.result_button.collidepoint(mouse_pos):
                    self.game_state = self.SHOP

            elif self.game_state == self.SHOP:
                self.handle_shop_click(mouse_pos, current_time)

    def handle_shop_click(self, mouse_pos, current_time):
        if self.damage_button.collidepoint(mouse_pos):
            if self.coins >= self.damage_upgrade_cost:
                self.coins -= self.damage_upgrade_cost
                self.player.damage_level += 1

        elif self.speed_button.collidepoint(mouse_pos):
            if self.coins >= self.speed_upgrade_cost:
                self.coins -= self.speed_upgrade_cost
                self.player.speed_level += 1

        elif self.rate_button.collidepoint(mouse_pos):
            if self.coins >= self.rate_upgrade_cost:
                self.coins -= self.rate_upgrade_cost
                self.player.rate_level += 1

        elif self.continue_button.collidepoint(mouse_pos):
            self.start_wave(current_time)

    # -----------------------------
    # Gameplay update
    # -----------------------------
    def update_playing(self, current_time):
        keys = pygame.key.get_pressed()
        self.player.handle_movement(keys)

        if keys[pygame.K_SPACE]:
            new_bullet = self.player.try_shoot(current_time)
            if new_bullet:
                self.bullets.append(new_bullet)

        self.update_bullets()
        self.spawn_enemy_if_needed(current_time)

        # Stop immediately if an enemy reaches the bottom.
        if self.update_enemies():
            self.lose_wave()
            return

        self.handle_collisions()

    def update_bullets(self):
        for bullet in self.bullets:
            bullet.update()

        self.bullets = [bullet for bullet in self.bullets if not bullet.is_off_screen()]

    def spawn_enemy_if_needed(self, current_time):
        if current_time - self.enemy_spawn_timer > self.spawn_rate:
            self.enemies.append(Enemy(self.current_level))
            self.enemy_spawn_timer = current_time

    def update_enemies(self):
        for enemy in self.enemies:
            enemy.update()
            if enemy.y > SCREEN_HEIGHT:
                return True
        return False

    def handle_collisions(self):
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if not bullet.rect.colliderect(enemy.rect):
                    continue

                if bullet in self.bullets:
                    self.bullets.remove(bullet)

                enemy.take_damage(self.player.damage)

                if enemy.is_dead():
                    self.coins += enemy.max_health
                    self.enemies_killed_this_level += 1
                    self.enemies.remove(enemy)

                    if self.enemies_killed_this_level >= self.enemies_required_for_next_level:
                        self.clear_wave()
                        return

                break

    # -----------------------------
    # Wave/state transitions
    # -----------------------------
    def clear_wave(self):
        self.last_result = "CLEARED"
        self.game_state = self.WAVE_CLEARED
        self.bullets.clear()
        self.enemies.clear()

    def lose_wave(self):
        self.last_result = "LOST"
        self.game_state = self.WAVE_LOST
        self.bullets.clear()
        self.enemies.clear()

    def start_wave(self, current_time):
        # A cleared wave advances the level. A lost wave retries the same one.
        if self.last_result == "CLEARED":
            self.current_level += 1
            self.enemies_required_for_next_level = 5 + (self.current_level * 2)

        self.enemies_killed_this_level = 0
        self.bullets.clear()
        self.enemies.clear()

        # Reset the spawn timer so a new enemy does not instantly appear
        # because the player spent time in the result/shop screens.
        self.enemy_spawn_timer = current_time
        self.player.last_shot_time = current_time
        self.game_state = self.PLAYING

    # -----------------------------
    # Drawing
    # -----------------------------
    def draw(self):
        self.screen.fill(BACKGROUND)

        if self.game_state == self.PLAYING:
            self.draw_playing()
        elif self.game_state == self.SHOP:
            self.draw_shop()
        elif self.game_state == self.WAVE_CLEARED:
            self.draw_result_screen(cleared=True)
        elif self.game_state == self.WAVE_LOST:
            self.draw_result_screen(cleared=False)

        pygame.display.flip()

    def draw_playing(self):
        self.player.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen, self.enemy_font)

        coin_text = self.font.render(f"Coins: {self.coins}", True, GOLD)
        level_text = self.font.render(f"Wave: {self.current_level}", True, WHITE)
        progress_text = self.font.render(
            f"Kills: {self.enemies_killed_this_level}/{self.enemies_required_for_next_level}",
            True,
            LIGHT_GRAY,
        )

        self.screen.blit(coin_text, (20, 20))
        self.screen.blit(
            level_text,
            (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 20),
        )
        self.screen.blit(
            progress_text,
            (SCREEN_WIDTH - progress_text.get_width() - 20, 20),
        )

    def draw_result_screen(self, cleared):
        if cleared:
            title = "WAVE CLEARED!"
            title_color = GREEN
            subtitle = f"You cleared Wave {self.current_level}."
            button_text = "OPEN UPGRADE SHOP"
        else:
            title = "WAVE LOST"
            title_color = RED
            subtitle = f"An enemy got through on Wave {self.current_level}."
            button_text = "UPGRADE & RETRY"

        title_surface = self.big_font.render(title, True, title_color)
        subtitle_surface = self.font.render(subtitle, True, WHITE)
        coins_surface = self.font.render(f"Coins: {self.coins}", True, GOLD)

        self.screen.blit(
            title_surface,
            (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 180),
        )
        self.screen.blit(
            subtitle_surface,
            (SCREEN_WIDTH // 2 - subtitle_surface.get_width() // 2, 260),
        )
        self.screen.blit(
            coins_surface,
            (SCREEN_WIDTH // 2 - coins_surface.get_width() // 2, 310),
        )

        pygame.draw.rect(self.screen, DARK_GREEN, self.result_button)
        button_surface = self.shop_font.render(button_text, True, WHITE)
        self.screen.blit(
            button_surface,
            (
                self.result_button.centerx - button_surface.get_width() // 2,
                self.result_button.centery - button_surface.get_height() // 2,
            ),
        )

    def draw_shop(self):
        pygame.draw.rect(self.screen, PANEL, (150, 80, 500, 440))
        pygame.draw.rect(self.screen, GREEN, (150, 80, 500, 440), 3)

        title_text = self.font.render("UPGRADE SHOP", True, GREEN)
        wallet_text = self.font.render(f"Coins: {self.coins}", True, GOLD)
        self.screen.blit(
            title_text,
            (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100),
        )
        self.screen.blit(
            wallet_text,
            (SCREEN_WIDTH // 2 - wallet_text.get_width() // 2, 140),
        )

        pygame.draw.rect(self.screen, BUTTON, self.damage_button)
        pygame.draw.rect(self.screen, BUTTON, self.speed_button)
        pygame.draw.rect(self.screen, BUTTON, self.rate_button)
        pygame.draw.rect(self.screen, DARK_GREEN, self.continue_button)

        damage_text = self.shop_font.render(
            f"Upgrade Damage (Lvl {self.player.damage_level}) -> Cost: {self.damage_upgrade_cost} c",
            True,
            WHITE,
        )
        speed_text = self.shop_font.render(
            f"Upgrade Player Speed (Lvl {self.player.speed_level}) -> Cost: {self.speed_upgrade_cost} c",
            True,
            WHITE,
        )
        rate_text = self.shop_font.render(
            f"Upgrade Fire Rate (Lvl {self.player.rate_level}) -> Cost: {self.rate_upgrade_cost} c",
            True,
            WHITE,
        )

        if self.last_result == "LOST":
            continue_label = "RETRY WAVE"
        else:
            continue_label = "LAUNCH NEXT WAVE"

        continue_text = self.shop_font.render(continue_label, True, WHITE)

        self.screen.blit(damage_text, (self.damage_button.x + 20, self.damage_button.y + 12))
        self.screen.blit(speed_text, (self.speed_button.x + 20, self.speed_button.y + 12))
        self.screen.blit(rate_text, (self.rate_button.x + 20, self.rate_button.y + 12))
        self.screen.blit(
            continue_text,
            (
                self.continue_button.centerx - continue_text.get_width() // 2,
                self.continue_button.centery - continue_text.get_height() // 2,
            ),
        )
