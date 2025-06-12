import pygame

from player import Player
from zamek import Castle
from fale import FalaManager, FalaStandard
from bob import BuildManager
from tower import TowerFactory
from enemies import EnemyFactory
from petla import GameManager

sciezka_1 = [(260, 450), (260, 400), (260, 100), (400, 100), (400, 50)]
sciezka_2 = [(515, 450), (515, 450), (515, 100), (400, 100), (400, 50)]
sciezki = [sciezka_1, sciezka_2]

def load_assets():
    assets = {}
    assets["board"] = pygame.Surface((800, 600))
    kostka = pygame.image.load("images/kostka.png").convert_alpha()
    kostka = pygame.transform.scale(kostka, (kostka.get_width() // 8, kostka.get_height() // 8))
    explosion_img = pygame.image.load("images/wybuch.png").convert_alpha()
    explosion_img = pygame.transform.scale(explosion_img, (64, 64))

    for x in range(0, 800, kostka.get_width()):
        for y in range(0, 600, kostka.get_height()):
            assets["board"].blit(kostka, (x, y))

    assets["grass1"] = pygame.transform.scale(pygame.image.load("images/grass.png").convert_alpha(), (200, 400))
    assets["grass2"] = pygame.transform.scale(pygame.image.load("images/grass.png").convert_alpha(), (200, 400))
    assets["grass3"] = pygame.transform.scale(pygame.image.load("images/grass.png").convert_alpha(), (100, 250))
    assets["castle"] = pygame.transform.scale(pygame.image.load("images/castle.png").convert_alpha(), (200, 100))
    assets["bomb_icon"] = pygame.transform.scale(pygame.image.load("images/bomb.png").convert_alpha(), (40, 40))
    assets["font"] = pygame.font.SysFont(None, 36)
    return assets, explosion_img

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tower Defense SOLID")
    clock = pygame.time.Clock()

    normal_img = pygame.transform.scale(
        pygame.image.load("images/ludziki.png").convert_alpha(), (60, 60)
    )
    fast_img = pygame.transform.scale(
        pygame.image.load("images/ludziki2.png").convert_alpha(), (60, 60)
    )
    tank_img = pygame.transform.scale(
        pygame.image.load("images/ludziki3.png").convert_alpha(), (60, 60)
    )
    boss_img = pygame.transform.scale(
        pygame.image.load("images/boss.png").convert_alpha(), (120, 120)
    )

    enemy_images = {
        'normal': normal_img,
        'fast': fast_img,
        'tank': tank_img,
        'boss': boss_img
    }

    assets, explosion_img = load_assets()

    player = Player()
    castle = Castle()
    wave_manager = FalaManager(FalaStandard())

    build_manager = BuildManager(
        build_zones=[
            pygame.Rect(0, 0, 200, 400),  
            pygame.Rect(600, 0, 200, 400),  
            pygame.Rect(350, 150, 100, 250),  
        ],
        tower_size=50
    )

    tower_factory = TowerFactory()
    enemy_factory = EnemyFactory(enemy_images, boss_img, explosion_img)

    game_manager = GameManager(
        player=player,
        castle=castle,
        wave_manager=wave_manager,
        build_manager=build_manager,
        tower_factory=tower_factory,
        enemy_factory=enemy_factory,
        screen=screen,
        assets=assets,
        sciezki=sciezki
    )

    game_manager.run(clock, fps=60)

if __name__ == "__main__":
    main()