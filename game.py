import pygame
import math
from sys import exit


pygame.init()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()

plansza = pygame.Surface((800,600))
plansza.fill("Grey")

trawa_1 = pygame.Surface((200,400))
trawa_1.fill("Green")

trawa_2 = pygame.Surface((200,400))
trawa_2.fill("Green")

trawa_3 = pygame.Surface((100,250))
trawa_3.fill("Green")

zamek = pygame.Surface((200,100))
zamek.fill("Brown")

przeciwnik = pygame.Surface((25,50))
przeciwnik.fill("Red")
przeciwnik_x_pos = 600
przeciwnik_y_pos = 500

TARGET = (400, 50)

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



    pygame.display.update()
    clock.tick(60)