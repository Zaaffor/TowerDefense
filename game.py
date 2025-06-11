import pygame
import math
import random
from sys import exit
from collections import deque

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()

plansza = pygame.Surface((800, 600))

kostka = pygame.image.load("images/kostka.png").convert_alpha()
kostka = pygame.transform.scale(kostka, (kostka.get_width() // 8, kostka.get_height() // 8))

for x in range(0, 800, kostka.get_width()):
    for y in range(0, 600, kostka.get_height()):
        plansza.blit(kostka, (x, y))

trawa_1 = pygame.image.load("images/grass.png").convert_alpha()
trawa_1 = pygame.transform.scale(trawa_1, (200, 400))
trawa_1_rect = pygame.Rect(0, 0, 200, 400)

trawa_2 = pygame.image.load("images/grass.png").convert_alpha()
trawa_2 = pygame.transform.scale(trawa_2, (200, 400))
trawa_2_rect = pygame.Rect(600, 0, 200, 400)

trawa_3 = pygame.image.load("images/grass.png").convert_alpha()
trawa_3 = pygame.transform.scale(trawa_3, (100, 250))
trawa_3_rect = pygame.Rect(350, 150, 100, 250)

zamek = pygame.image.load("images/castle.png").convert_alpha()
zamek = pygame.transform.scale(zamek, (200, 100))
zamek_rect = pygame.Rect(300, 0, 200, 100)

enemy_image = pygame.image.load("images/ludziki.png").convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (60, 60))

enemy_image2 = pygame.image.load("images/ludziki2.png").convert_alpha()
enemy_image2 = pygame.transform.scale(enemy_image2, (60, 60))

enemy_image3 = pygame.image.load("images/ludziki3.png").convert_alpha()
enemy_image3 = pygame.transform.scale(enemy_image3, (60, 60))

tower_image = pygame.image.load("images/wieza.png").convert_alpha()
tower_image = pygame.transform.scale(tower_image, (50, 50))


boss_image = pygame.image.load("images/boss.png").convert_alpha()
boss_image = pygame.transform.scale(boss_image, (120, 120))

bomb_icon = pygame.image.load("images/bomb.png").convert_alpha()
bomb_icon = pygame.transform.scale(bomb_icon, (40, 40))

explosion_img = pygame.image.load("images/wybuch.png").convert_alpha()
explosion_img = pygame.transform.scale(explosion_img, (64, 64))

#

TARGET = (400, 50)

przeszkody = [trawa_1_rect, trawa_2_rect, trawa_3_rect, zamek_rect]

sciezka_1 = [(260, 450), (260, 400), (260, 100), (400, 100), (400, 50)]
sciezka_2 = [(515, 450), (515, 450), (515, 100), (400, 100), (400, 50)]
sciezki = [sciezka_1, sciezka_2]


class Player:
    def __init__(self):
        self.gold = 10
        self.koszt = 10

    def portfel(self):
        return self.gold >= self.koszt

    def zakup(self):
        self.gold -= self.koszt
        self.koszt += 2

    def can_upgrade(self, cost):
        return self.gold >= cost

    def pay_upgrade(self, cost):
        self.gold -= cost


class Castle:
    def __init__(self, hp=100):
        self.hp = hp

    def dmg(self, obrazenia):
        self.hp -= obrazenia

    def zniszczony(self):
        return self.hp <= 0


class Tower:
    DELAY = 500

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 120
        self.damage = 10
        self.last_hit = 0
        self.image = tower_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.level = 1
        self.upgrade_cost = 15
        self.selected = False
        self.path1_level = 0  # zasieg sciezka
        self.path2_level = 0  # speed sciezka
        self.path3_level = 0  # moc sciezka
        self.max_path_level = 5  # Max upgrade / sciezke
        self.path1_rect = None
        self.path2_rect = None
        self.path3_rect = None

    def in_range(self, enemy):
        odleglosc = ((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2) ** 0.5
        return odleglosc <= self.radius

    def attack(self, enemies):
        current_delay = self.DELAY
        if self.path2_level > 0:
            current_delay = max(100, self.DELAY - (self.path2_level * 100))

        strzal = pygame.time.get_ticks()
        if strzal - self.last_hit < current_delay:
            return

        closest = None
        min_odleglosc = float("inf")

        for enemy in enemies:
            if self.in_range(enemy):
                odleglosc = ((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2) ** 0.5
                if odleglosc < min_odleglosc:
                    min_odleglosc = odleglosc
                    closest = enemy

        if closest:
            current_damage = self.damage
            if self.path3_level > 0:
                current_damage += self.path3_level * 5
            closest.take_damage(current_damage)
            self.last_hit = strzal

    def upgrade_path(self, path_number):
        if path_number == 1 and self.path1_level < self.max_path_level:  # zasieg sciezka
            self.path1_level += 1
            self.radius += 20
            return True
        elif path_number == 2 and self.path2_level < self.max_path_level:  # speed sciezka
            self.path2_level += 1
            return True
        elif path_number == 3 and self.path3_level < self.max_path_level:  # moc sciezka
            self.path3_level += 1
            return True
        return False

    def get_upgrade_cost(self, path_number):
        base_cost = 5 + (max(self.path1_level, self.path2_level, self.path3_level) * 5)
        return base_cost

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
        pygame.draw.circle(surface, (0, 0, 255), (self.x + 25, self.y + 25), self.radius, 1)

        if self.selected:
            self.draw_upgrade_menu(surface)

    def draw_upgrade_menu(self, surface):
        menu_rect = pygame.Rect(self.x - 50, self.y - 120, 150, 110)
        pygame.draw.rect(surface, (50, 50, 50), menu_rect)
        pygame.draw.rect(surface, (200, 200, 200), menu_rect, 2)

        font = pygame.font.SysFont(None, 20)
        small_font = pygame.font.SysFont(None, 16)

        # sciezka 1 (zasieg)
        self.path1_rect = pygame.Rect(self.x - 40, self.y - 110, 130, 30)
        path1_color = (100, 100, 255) if self.path1_level < self.max_path_level else (150, 150, 150)
        pygame.draw.rect(surface, path1_color, self.path1_rect)
        path1_text = font.render(f"Range ({self.path1_level}/5)", True, (255, 255, 255))
        surface.blit(path1_text, (self.path1_rect.x + 5, self.path1_rect.y + 5))
        if self.path1_level < self.max_path_level:
            cost_text = small_font.render(f"Cost: {self.get_upgrade_cost(1)}", True, (255, 255, 0))
            surface.blit(cost_text, (self.path1_rect.x + 5, self.path1_rect.y + 20))

        # sciezka 2 (speed)
        self.path2_rect = pygame.Rect(self.x - 40, self.y - 75, 130, 30)
        path2_color = (100, 100, 255) if self.path2_level < self.max_path_level else (150, 150, 150)
        pygame.draw.rect(surface, path2_color, self.path2_rect)
        path2_text = font.render(f"Speed ({self.path2_level}/5)", True, (255, 255, 255))
        surface.blit(path2_text, (self.path2_rect.x + 5, self.path2_rect.y + 5))
        if self.path2_level < self.max_path_level:
            cost_text = small_font.render(f"Cost: {self.get_upgrade_cost(2)}", True, (255, 255, 0))
            surface.blit(cost_text, (self.path2_rect.x + 5, self.path2_rect.y + 20))

        # sciezka 3 (moc)
        self.path3_rect = pygame.Rect(self.x - 40, self.y - 40, 130, 30)
        path3_color = (100, 100, 255) if self.path3_level < self.max_path_level else (150, 150, 150)
        pygame.draw.rect(surface, path3_color, self.path3_rect)
        path3_text = font.render(f"Power ({self.path3_level}/5)", True, (255, 255, 255))
        surface.blit(path3_text, (self.path3_rect.x + 5, self.path3_rect.y + 5))
        if self.path3_level < self.max_path_level:
            cost_text = small_font.render(f"Cost: {self.get_upgrade_cost(3)}", True, (255, 255, 0))
            surface.blit(cost_text, (self.path3_rect.x + 5, self.path3_rect.y + 20))


class Bob:
    def __init__(self, pole_do_budowy, rozmiar):
        self.pdb = pole_do_budowy
        self.rozmiar = rozmiar

    def sprawdzanie(self, pozycja):
        for pole in self.pdb:
            pole_rect = pygame.Rect(pole[0], pole[1], self.rozmiar, self.rozmiar)
            if pole_rect.collidepoint(pozycja):
                return pole
        return None


class Enemy:
    def __init__(self, x, y, hp=30, width=25, height=50, speed=1, sciezka=None, level=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.level = level

        random_tier = random.randint(1, level)
        bonus_hp = 5 * (level - 1)

        if (random_tier >= 5):
            self.max_hp = hp + 30 + bonus_hp
            self.speed = speed
            self.image = enemy_image3
        elif (random_tier >= 3):
            self.max_hp = hp + bonus_hp
            self.speed = speed + 1
            self.image = enemy_image2
        else:
            self.max_hp = hp + bonus_hp
            self.speed = speed
            self.image = enemy_image

        self.hp = self.max_hp
        self.path_index = 0
        self.path = sciezka

    def update(self):
        if self.path_index >= len(self.path):
            return

        target_x, target_y = self.path[self.path_index]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        if distance < self.speed:
            self.x = target_x
            self.y = target_y
            self.path_index += 1
        else:
            dx /= distance
            dy /= distance
            self.x += dx * self.speed
            self.y += dy * self.speed

        self.rect.topleft = (self.x, self.y)

    def take_damage(self, dmg):
        self.hp -= dmg

    def zgon(self):
        return self.hp <= 0

    def draw(self, surface):
        image_rect = self.image.get_rect(center=self.rect.center)
        surface.blit(self.image, image_rect.topleft)
        max_hp = self.max_hp
        b_width = self.rect.width
        b_height = 5
        hp_ratio = max(self.hp, 0) / max_hp
        b_hp_rect = pygame.Rect(self.rect.x, self.rect.y - 10, b_width * hp_ratio, b_height)
        pygame.draw.rect(surface, (0, 255, 0), b_hp_rect)




class Boss(Enemy):
   #Duży przeciwnik boss z wiekszymHP i 2x wieksyzmi obrażeniami dla zamku
    def __init__(self, x, y, sciezka, level=1):
        super().__init__(x, y, hp=500 + level * 150, width=120, height=120,
                         speed=0.6 + 0.1 * level, sciezka=sciezka, level=level)
        self.image = boss_image

    # obrazenia 20 a nie 10
    def castle_hit_dmg(self):
        return 20


class Explosion:
    LIFE = 300 

    def __init__(self, pos):
        self.x, self.y = pos
        self.birth = pygame.time.get_ticks()

    def draw(self, surf):
        surf.blit(explosion_img, (self.x - 32, self.y - 32))

    def dead(self):
        return pygame.time.get_ticks() - self.birth > self.LIFE

#




class WaveManagment:
    def __init__(self):
        self.aktualna_fala = 1
        self.enemies_to_spawn = self.enemy_count()
        self.spawned = 0
        self.spawn_interval = 2000
        self.last_spawn = pygame.time.get_ticks()
        self.last_wave = pygame.time.get_ticks()
        self.przerwa = 5000
        self.next_wave = False

    def enemy_count(self):
        return 5 + (self.aktualna_fala - 1) * 2

    def update(self):
        teraz = pygame.time.get_ticks()
        if self.spawned >= self.enemies_to_spawn:
            if teraz - self.last_wave > self.przerwa:
                self.next_wave = True 
        if self.next_wave:
            self.aktualna_fala += 1
            self.enemies_to_spawn = self.enemy_count()
            self.spawned = 0
            self.next_wave = False
            self.last_wave = teraz
            self.spawn_interval = max(500, self.spawn_interval - 200)

    def should_spawn(self):
        teraz = pygame.time.get_ticks()
        return self.spawned < self.enemies_to_spawn and teraz - self.last_spawn >= self.spawn_interval

    def rejestr(self):
        self.spawned += 1
        self.last_spawn = pygame.time.get_ticks()


player = Player()
rozmiar_wiezy = 50
pola_do_budowy = []

for i in [trawa_1_rect, trawa_2_rect, trawa_3_rect]:
    for x in range(i.left, i.right, rozmiar_wiezy):
        for y in range(i.top, i.bottom, rozmiar_wiezy):
            pola_do_budowy.append((x, y))

budowniczy = Bob(pola_do_budowy, rozmiar_wiezy)
wieze = []
castle = Castle()
fale = WaveManagment()
enemies = []
enemy_spawn = 2000
last_spawn = pygame.time.get_ticks()
max_enemies = 10
spawned_enemies = 0
wave_timer = pygame.time.get_ticks()
wave_interval = 10000
spawn_speedup_timer = pygame.time.get_ticks()
spawn_speedup_interval = 10000
kill_count = 0
selected_tower = None


# nowe 

BOMBS_MAX     = 3
BOMB_RADIUS   = 120  # zasięg obrażeń
BOMB_DMG      = 150 # obrażenia w środku wybuchu
bombs_left    = BOMBS_MAX
bomb_cooldown = 5000   # ms czas między wybuchami
last_bomb     = 0
explosions    = deque()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pozycja = pygame.mouse.get_pos()

            if selected_tower:
                path_clicked = None
                if selected_tower.path1_rect and selected_tower.path1_rect.collidepoint(
                        pozycja) and selected_tower.path1_level < selected_tower.max_path_level:
                    path_clicked = 1
                elif selected_tower.path2_rect and selected_tower.path2_rect.collidepoint(
                        pozycja) and selected_tower.path2_level < selected_tower.max_path_level:
                    path_clicked = 2
                elif selected_tower.path3_rect and selected_tower.path3_rect.collidepoint(
                        pozycja) and selected_tower.path3_level < selected_tower.max_path_level:
                    path_clicked = 3

                if path_clicked:
                    upgrade_cost = selected_tower.get_upgrade_cost(path_clicked)
                    if player.can_upgrade(upgrade_cost) and selected_tower.upgrade_path(path_clicked):
                        player.pay_upgrade(upgrade_cost)
                    continue

            if selected_tower:
                selected_tower.selected = False
                selected_tower = None

            tower_clicked = False
            for wieza in wieze:
                if wieza.rect.collidepoint(pozycja):
                    wieza.selected = True
                    selected_tower = wieza
                    tower_clicked = True
                    break

            if not tower_clicked:
                pole = budowniczy.sprawdzanie(pozycja)
                if pole and player.portfel():
                    zajete = any(wieza.rect.topleft == pole for wieza in wieze)
                    if not zajete:
                        wieze.append(Tower(*pole))
                        player.zakup()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if selected_tower:
                selected_tower.selected = False
                selected_tower = None

         
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            now = pygame.time.get_ticks()
            if bombs_left > 0 and now - last_bomb >= bomb_cooldown:
                bomb_pos = pygame.mouse.get_pos()
                explosions.append(Explosion(bomb_pos))
                bombs_left -= 1
                last_bomb = now

                for e in enemies[:]:
                    if math.hypot(e.x - bomb_pos[0], e.y - bomb_pos[1]) <= BOMB_RADIUS:
                        e.take_damage(BOMB_DMG)

    screen.blit(plansza, (0, 0))
    screen.blit(trawa_1, (0, 0))
    screen.blit(trawa_2, (600, 0))
    screen.blit(trawa_3, (350, 150))
    screen.blit(zamek, (300, 0))

    czas = pygame.time.get_ticks()
    fale.update()



    if fale.aktualna_fala % 5 == 0 and not any(isinstance(e, Boss) for e in enemies):
        bx, by = random.choice([(260, 550), (515, 550)])
        enemies.append(Boss(bx, by, sciezka_1 if bx == 260 else sciezka_2, level=fale.aktualna_fala))

#

    if fale.should_spawn():
        x = random.randint(20, 780)
        y = random.randint(500, 550)
        fav_path = min(sciezki, key=lambda s: math.hypot(x - s[0][0], y - s[0][1]))
        level = fale.aktualna_fala
        new_enemy = Enemy(x, y, sciezka=fav_path, level=level)
        enemies.append(new_enemy)
        fale.rejestr()

    if czas - spawn_speedup_timer > spawn_speedup_interval:
        enemy_spawn = max(500, enemy_spawn - 200)
        spawn_speedup_timer = czas

    if pygame.time.get_ticks() - wave_timer > wave_interval:
        max_enemies += 5
        wave_timer = pygame.time.get_ticks()

    for enemy in enemies:
        enemy.update()
        enemy.draw(screen)


    for exp in list(explosions):
        exp.draw(screen)
        if exp.dead():
            explosions.popleft()
            #


    for wieza in wieze:
        wieza.attack(enemies)
        wieza.draw(screen)

    for enemy in enemies[:]:
        if enemy.zgon():
            enemies.remove(enemy)
            player.gold += 2
            kill_count += 1
      #  elif enemy.path_index >= len(enemy.path):
      #      enemies.remove(enemy)
      #      castle.dmg(10)

        elif enemy.path_index >= len(enemy.path):
                enemies.remove(enemy)
                dmg = enemy.castle_hit_dmg() if hasattr(enemy, "castle_hit_dmg") else 10
                castle.dmg(dmg)
                

    font = pygame.font.SysFont(None, 36)
    hp_text = font.render(f"Castle HP: {castle.hp}", True, (255, 0, 0))
    gold_text = font.render(f"Gold: {player.gold}", True, (255, 255, 0))
    fala_text = font.render(f"Fala: {fale.aktualna_fala}", True, (255, 255, 255))
    kill_text = font.render(f"Zabici: {kill_count}", True, (255, 255, 255))
    screen.blit(hp_text, (10, 10))
    screen.blit(gold_text, (10, 30))
    screen.blit(fala_text, (700, 10))
    screen.blit(kill_text, (660, 30))

     
    screen.blit(bomb_icon, (10, 60))          
    bombs_text = font.render(f"x {bombs_left}", True, (255, 255, 255))
    screen.blit(bombs_text, (50, 62)) 


    if castle.zniszczony():
        print("GAME OVER")
        pygame.quit()
        exit()

    pygame.display.update()
    clock.tick(60)