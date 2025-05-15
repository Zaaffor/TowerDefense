import pygame
import math
import random
from sys import exit


pygame.init()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()

plansza = pygame.Surface((800,600))
plansza.fill("Grey")

trawa_1 = pygame.Surface((200,400))
trawa_1.fill("Green")
trawa_1_rect = pygame.Rect(0, 0, 200, 400)

trawa_2 = pygame.Surface((200,400))
trawa_2.fill("Green")
trawa_2_rect = pygame.Rect(600, 0, 200, 400)

trawa_3 = pygame.Surface((100,250))
trawa_3.fill("Green")
trawa_3_rect = pygame.Rect(350, 150, 100, 250)

zamek = pygame.Surface((200,100))
zamek.fill("Brown")
zamek_rect = pygame.Rect(300, 0, 200, 100)

TARGET = (400, 50)

przeszkody = [trawa_1_rect, trawa_2_rect, trawa_3_rect, zamek_rect]

class Enemy:
    def __init__(self, x, y, width = 25, height = 50, speed = 1):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.x = x
        self.y = y

    def update(self, target_x, target_y, przeszkody):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        dx /= distance
        dy /= distance
        next_x = self.x + dx * self.speed
        next_y = self.y + dy * self.speed
        next_rect = pygame.Rect(next_x, next_y, self.rect.width, self.rect.height)

        for przeszkoda in przeszkody:
            if next_rect.colliderect(przeszkoda):
                next_y = self.y

        self.x = next_x
        self.y = next_y

        self.rect.topleft = (self.x, self.y)
    
    def draw(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), self.rect)

enemies = []
for _ in range(5):
    x = random.randint(20, 780)
    y = random.randint(500, 550)
    enemy = Enemy(x,y)
    enemies.append(enemy)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.blit(plansza, (0,0))
    screen.blit(trawa_1, (0,0))
    screen.blit(trawa_2, (600,0))
    screen.blit(trawa_3, (350, 150))
    screen.blit(zamek, (300, 0))

    for enemy in enemies:
        enemy.update(*TARGET, przeszkody)
        enemy.draw(screen)
        



    pygame.display.update()
    clock.tick(60)