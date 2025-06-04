import pygame
import math
import random
from sys import exit

pygame.init()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()

plansza = pygame.Surface((800,600))

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

tower_image = pygame.image.load("images/wieza.png").convert_alpha()
tower_image = pygame.transform.scale(tower_image, (50, 50))

TARGET = (400, 50)

przeszkody = [trawa_1_rect, trawa_2_rect, trawa_3_rect, zamek_rect]

sciezka_1 = [
    (260, 450),
    (260, 400),
    (260, 100),
    (400, 100),
    (400, 50)
]

sciezka_2 = [
    (515, 450),
    (515, 450),
    (515, 100),
    (400, 100),
    (400, 50)
]

sciezki = [sciezka_1, sciezka_2]


class Player:
    def __init__(self):
        self.gold = 10
    
    def portfel(self, koszt):
        return self.gold >= koszt
    
    def zakup(self, koszt):
        self.gold -= koszt

class Castle:
    def __init__(self, hp=100):
        self.hp = hp

    def dmg(self, obrazenia):
        self.hp -= obrazenia
    
    def zniszczony(self):
        return self.hp <= 0

class Tower:
    CENA = 10
    DELAY = 500

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 100
        self.damage = 10
        self.last_hit = 0
        self.image = tower_image
        self.rect = self.image.get_rect(topleft=(x,y))

    def in_range(self, enemy):
        odleglosc = ((enemy.x - self.x)**2 + (enemy.y - self.y)**2) ** 0.5
        return odleglosc <= self.radius
    
    def attack(self, enemies):
        strzal = pygame.time.get_ticks()
        if strzal - self.last_hit < self.DELAY:
            return
        
        closest = None
        min_odleglosc = float("inf")

        for enemy in enemies:
            if self.in_range(enemy):
                odleglosc = ((enemy.x - self.x)**2 + (enemy.y - self.y)**2) ** 0.5
                if odleglosc < min_odleglosc:
                    min_odleglosc = odleglosc
                    closest = enemy
        
        if closest:
            closest.take_damage(self.damage)
            self.last_hit = strzal
    
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
        pygame.draw.circle(surface, (0, 0, 255), (self.x + 25, self.y + 25), self.radius, 1)

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
    def __init__(self, x, y, hp = 30, width = 25, height = 50, speed = 1, sciezka = None, level = 1):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.level = level
        self.hp = hp + (level * 10)
        self.max_hp = hp + (level * 10)
        self.speed = speed + (level * 0.2)
        self.path_index = 0
        self.path = sciezka
        self.image = enemy_image

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

enemies = []
enemy_spawn = 2000
last_spawn = pygame.time.get_ticks()
max_enemies = 10
spawned_enemies = 0

wave_timer = pygame.time.get_ticks()
wave_interval = 10000

spawn_speedup_timer = pygame.time.get_ticks()
spawn_speedup_interval = 15000 

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        pozycja = pygame.mouse.get_pos()
        pole = budowniczy.sprawdzanie(pozycja)

        if pole and player.portfel(Tower.CENA):
            wieze.append(Tower(*pole))
            player.zakup(Tower.CENA)

    screen.blit(plansza, (0,0))
    screen.blit(trawa_1, (0,0))
    screen.blit(trawa_2, (600,0))
    screen.blit(trawa_3, (350, 150))
    screen.blit(zamek, (300, 0))

    czas = pygame.time.get_ticks()
    if spawned_enemies < max_enemies and czas - last_spawn >= enemy_spawn:
        x = random.randint(20, 780)
        y = random.randint(500, 550)

        fav_path = min(sciezki, key=lambda s:math.hypot(x - s[0][0], y - s[0][1]))

        level = (spawned_enemies // 10) + 1
        new_enemy = Enemy(x, y, sciezka = fav_path, level=level)
        enemies.append(new_enemy)
        spawned_enemies += 1
        last_spawn = czas

    if czas - spawn_speedup_timer > spawn_speedup_interval:
        enemy_spawn = max(500, enemy_spawn - 200)  
        spawn_speedup_timer = czas

    if pygame.time.get_ticks() - wave_timer > wave_interval:
        max_enemies += 5
        wave_timer = pygame.time.get_ticks()    

    

    for enemy in enemies:
        enemy.update()
        enemy.draw(screen)
    
    for wieza in wieze:
        wieza.attack(enemies)
        wieza.draw(screen)

    for enemy in enemies[:]:
        if enemy.zgon():
            enemies.remove(enemy)
            player.gold += 2
        elif enemy.path_index >= len(enemy.path):
            enemies.remove(enemy)
            castle.dmg(10)
    
    font = pygame.font.SysFont(None, 36)
    hp_text = font.render(f"Castle HP: {castle.hp}", True, (255, 0, 0))
    screen.blit(hp_text, (10, 10))

    if castle.zniszczony():
        print("GAME OVER")
        pygame.quit()
        exit()

    #for path in sciezki:
        #pygame.draw.lines(screen, (255, 255, 0), False, path, 3) - rysowanie sciezek

    pygame.display.update()
    clock.tick(60)