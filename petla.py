import pygame
import random
import math
from collections import deque

sciezka_1 = [(260, 450), (260, 400), (260, 100), (400, 100), (400, 50)]
sciezka_2 = [(515, 450), (515, 450), (515, 100), (400, 100), (400, 50)]
sciezki = [sciezka_1, sciezka_2]

class GameManager:
    def __init__(self, player, castle, wave_manager, build_manager, tower_factory, enemy_factory, screen, assets, sciezki):
        self.player = player
        self.castle = castle
        self.wave_manager = wave_manager
        self.build_manager = build_manager
        self.tower_factory = tower_factory
        self.enemy_factory = enemy_factory
        self.screen = screen
        self.assets = assets
        self.sciezki = sciezki

        self.towers = []
        self.enemies = []
        self.selected_tower = None
        self.explosions = deque()
        self.bombs_left = 3
        self.last_bomb = 0
        self.bomb_cooldown = 5000
        self.kill_count = 0

        self.BOMB_RADIUS = 120
        self.BOMB_DMG = 150

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if self.selected_tower:
                    path_clicked = self.selected_tower.check_upgrade_click(pos)
                    if path_clicked:
                        cost = self.selected_tower.get_upgrade_cost(path_clicked)
                        if self.player.pay_upgrade(cost):
                            self.selected_tower.upgrade(path_clicked)
                        return

                if self.selected_tower:
                    self.selected_tower.selected = False
                    self.selected_tower = None

                for tower in self.towers:
                    if tower.rect.collidepoint(pos):
                        tower.selected = True
                        self.selected_tower = tower
                        break
                else:
                    if self.build_manager.is_valid_cell(pos) and self.player.buy_tower():
                        new_tower = self.tower_factory.create_tower(*self.build_manager.get_cell_coords(pos))
                        self.towers.append(new_tower)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if self.selected_tower:
                    self.selected_tower.selected = False
                    self.selected_tower = None

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                now = pygame.time.get_ticks()
                if self.bombs_left > 0 and now - self.last_bomb >= self.bomb_cooldown:
                    bomb_pos = pygame.mouse.get_pos()
                    self.explosions.append(self.enemy_factory.create_explosion(bomb_pos))
                    self.bombs_left -= 1
                    self.last_bomb = now
                    for e in self.enemies:
                        if ((e.x - bomb_pos[0]) ** 2 + (e.y - bomb_pos[1]) ** 2) ** 0.5 <= self.BOMB_RADIUS:
                            e.take_damage(self.BOMB_DMG)

    def update(self):
        self.wave_manager.update()

        if self.wave_manager.is_boss_wave() and not self.wave_manager.boss_already_spawned():
            bx, by = self.enemy_factory.get_boss_spawn_coords()
            sciezka = self.sciezki[0] if bx == 260 else self.sciezki[1]
            boss_enemy = self.enemy_factory.create_boss(bx, by, self.wave_manager.get_current_wave(), sciezka)
            self.enemies.append(boss_enemy)
            self.wave_manager.set_boss_spawned()

        if self.wave_manager.should_spawn():
            x, y = self.enemy_factory.get_spawn_coords()
            sciezka = self.get_closest_path(x, y)
            wave = self.wave_manager.get_current_wave()
            enemy_type = self.enemy_factory.pick_enemy_type(wave)
            new_enemy = self.enemy_factory.create_enemy(x, y, wave, sciezka, enemy_type=enemy_type)
            self.enemies.append(new_enemy)
            self.wave_manager.rejestr()

        for enemy in self.enemies:
            enemy.update()

        for tower in self.towers:
            tower.attack(self.enemies)

        for enemy in self.enemies[:]:
            if enemy.is_dead():
                self.enemies.remove(enemy)
                self.player.gold += 2
                self.kill_count += 1
            elif enemy.reached_castle():
                print(f"Enemy reached castle! Castle HP before: {self.castle.hp}")
                self.enemies.remove(enemy)
                dmg = enemy.castle_hit_dmg() if hasattr(enemy, "castle_hit_dmg") else 10
                print(f"Castle takes {dmg} dmg")
                self.castle.take_damage(dmg)
                print(f"Castle HP after: {self.castle.hp}")

        # OBSŁUGA WYBUCHÓW
        for exp in list(self.explosions):
            if exp.dead():
                self.explosions.popleft()

    def get_closest_path(self, x, y):
        return min(self.sciezki, key=lambda path: (path[0][0] - x) ** 2 + (path[0][1] - y) ** 2)

    def draw(self):
        self.screen.blit(self.assets["board"], (0, 0))
        self.screen.blit(self.assets["grass1"], (0, 0))
        self.screen.blit(self.assets["grass2"], (600, 0))
        self.screen.blit(self.assets["grass3"], (350, 150))
        self.screen.blit(self.assets["castle"], (300, 0))

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for exp in self.explosions:
            exp.draw(self.screen)

        for tower in self.towers:
            tower.draw(self.screen)

        font = self.assets["font"]
        self.screen.blit(font.render(f"Castle HP: {self.castle.hp}", True, (255, 0, 0)), (10, 10))
        self.screen.blit(font.render(f"Gold: {self.player.gold}", True, (255, 255, 0)), (10, 30))
        self.screen.blit(font.render(f"Fala: {self.wave_manager.get_current_wave()}", True, (255, 255, 255)), (700, 10))
        self.screen.blit(font.render(f"Zabici: {self.kill_count}", True, (255, 255, 255)), (660, 30))
        self.screen.blit(self.assets["bomb_icon"], (10, 60))
        self.screen.blit(font.render(f"x {self.bombs_left}", True, (255, 255, 255)), (50, 62))

    def game_over(self):
        over = self.castle.is_destroyed()
        if over:
            print(f"GAME OVER - castle destroyed at HP={self.castle.hp}")
        return over

    def run(self, clock, fps=60):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.update()
            clock.tick(fps)
            if self.game_over():
                print("GAME OVER")
                pygame.quit()
                exit()