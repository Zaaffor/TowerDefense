import pygame
import math
import random
from sys import exit

pygame.init()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()


enemy_img = pygame.image.load("ludziki.png").convert_alpha()
grass_img = pygame.image.load("grass.png").convert()
castle_img = pygame.image.load("castle.png").convert_alpha()


plansza = pygame.Surface((800,600))
plansza.fill("Grey")

trawa_1 = pygame.transform.scale(grass_img, (200, 400))
trawa_1_rect = pygame.Rect(0, 0, 200, 400)

trawa_2 = pygame.transform.scale(grass_img, (200, 400))
trawa_2_rect = pygame.Rect(600, 0, 200, 400)

trawa_3 = pygame.transform.scale(grass_img, (100, 250))
trawa_3_rect = pygame.Rect(350, 150, 100, 250)

zamek = pygame.transform.scale(castle_img, (200, 100))
zamek_rect = pygame.Rect(300, 0, 200, 100) 

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

class Tower:
    CENA = 10
    DELAY = 500

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 115
        self.damage = 10
        self.last_hit = 0

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

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, hp = 30, speed = 1, sciezka = None):
        self.image = pygame.transform.scale(enemy_img, (45,60))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
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
        surface.blit(self.image, self.rect)
        hp_ratio = max(self.hp, 0) / self.max_hp
        hp_bar = pygame.Rect(self.rect.x, self.rect.y - 10, self.rect.width * hp_ratio, 5)
        pygame.draw.rect(surface, (0, 255, 0), hp_bar)

player = Player()

rozmiar_wiezy = 50
pola_do_budowy = []

for i in [trawa_1_rect, trawa_2_rect, trawa_3_rect]:
    for x in range(i.left, i.right, rozmiar_wiezy):
        for y in range(i.top, i.bottom, rozmiar_wiezy):
            pola_do_budowy.append((x, y))

budowniczy = Bob(pola_do_budowy, rozmiar_wiezy)
wieze = []

enemies = []
enemy_spawn = 2000
last_spawn = pygame.time.get_ticks()
max_enemies = 10
spawned_enemies = 0

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

        new_enemy = Enemy(x, y, sciezka = fav_path)
        enemies.append(new_enemy)
        spawned_enemies += 1
        last_spawn = czas

    for enemy in enemies:
        enemy.update()
        enemy.draw(screen)
    
    for wieza in wieze:
        wieza.attack(enemies)
        pygame.draw.circle(screen, (0, 0, 255), (wieza.x + 25, wieza.y + 25), 20)

    for enemy in enemies[:]:
        if enemy.zgon():
            enemies.remove(enemy)
            player.gold += 10

    #for path in sciezki:
        #pygame.draw.lines(screen, (255, 255, 0), False, path, 3) - rysowanie sciezek

    pygame.display.update()
    clock.tick(60)