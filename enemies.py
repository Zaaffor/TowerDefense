import pygame
import math
import random

class Movement:
    def update_position(self, enemy):
        raise NotImplementedError()

class Path(Movement):
    def __init__(self, path, speed):
        self.path = path
        self.path_index = 0
        self.speed = speed

    def update_position(self, enemy):
        if self.path_index >= len(self.path):
            return
    
        target_x, target_y = self.path[self.path_index]
        dx, dy = target_x - enemy.x, target_y - enemy.y
        distance = math.hypot(dx, dy)

        if distance < self.speed:
            enemy.x = target_x
            enemy.y = target_y
            self.path_index += 1
        else:
            dx /= distance
            dy /= distance
            enemy.x += dx * self.speed
            enemy.y += dy * self.speed

        enemy.rect.topleft = (enemy.x, enemy.y)

class Damage:
    def Zamek_dmg(self):
        raise NotImplementedError()
    
class StandardDamage(Damage):
    def Zamek_dmg(self):
        return 10

class BossDamage(Damage):
    def Zamek_dmg(self):
        return 20
    
class Enemy:
    def __init__(self, x, y, hp, width, height, movement: Movement, dmg: Damage, image):
        self.x = x
        self.y = y
        self.max_hp = hp
        self.hp = hp
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.movement = movement
        self.dmg = dmg
        self.image = image

    def update(self):
        self.movement.update_position(self)

    def rany(self, dmg):
        self.hp -= dmg
    
    def zamek_dmg(self):
        return self.dmg.Zamek_dmg()
    
    def is_dead(self):
        return self.hp <= 0
    
    def take_damage(self, dmg):
        self.hp -= dmg
    
    def reached_castle(self):
        return self.movement.path_index >= len(self.movement.path)

    def draw(self, surf):
        surf.blit(self.image, self.rect.topleft)

class StandardEnemy(Enemy):
    def __init__(self, x, y, path, image, hp=30, speed=1):
        movement = Path(path, speed=speed)
        dmg = StandardDamage()
        super().__init__(x, y, hp, 25, 50, movement, dmg, image)

class FastEnemy(Enemy):
    def __init__(self, x, y, path, image, hp=20, speed=2):
        movement = Path(path, speed=speed)
        dmg = StandardDamage()
        super().__init__(x, y, hp, 25, 50, movement, dmg, image)

class TankEnemy(Enemy):
    def __init__(self, x, y, path, image, hp=100, speed=1.5):
        movement = Path(path, speed=speed)
        dmg = StandardDamage()
        super().__init__(x, y, hp, 25, 50, movement, dmg, image)

class Boss(Enemy):
    def __init__(self, x, y, path, image, hp=500, speed=1):
        movement = Path(path, speed=speed)
        dmg = BossDamage()
        super().__init__(x, y, hp, 120, 120, movement, dmg, image)  

class Explosion:
    LIFE = 300 

    def __init__(self, pos, image):
        self.x, self.y = pos
        self.birth = pygame.time.get_ticks()
        self.image = image

    def draw(self, surf):
        surf.blit(self.image, (self.x - 32, self.y - 32))

    def dead(self):
        return pygame.time.get_ticks() - self.birth > self.LIFE

class EnemyFactory:
    def __init__(self, enemy_images, boss_image, explosion_image):
        self.enemy_images = enemy_images 
        self.boss_image = boss_image
        self.explosion_image = explosion_image

    def create_enemy(self, x, y, wave, path, enemy_type='normal'):
        image = self.enemy_images.get(enemy_type, self.enemy_images.get('normal'))
        if enemy_type == 'normal':
            hp = 30 + wave * 2
            speed = 1
            return StandardEnemy(x, y, path, image, hp=hp, speed=speed)
        elif enemy_type == 'fast':
            hp = 20 + wave
            speed = 2 + wave * 0.1
            return FastEnemy(x, y, path, image, hp=hp, speed=speed)
        elif enemy_type == 'tank':
            hp = 100 + wave * 10
            speed = 1.5
            return TankEnemy(x, y, path, image, hp=hp, speed=speed)
        elif enemy_type == 'boss':
            hp = 500 + wave * 50
            speed = 1
            return Boss(x, y, path, self.boss_image, hp=hp, speed=speed)

    def pick_enemy_type(self, wave):
        types = ['normal']
        weights = [max(100 - wave*7, 30)]
        if wave >= 2:
            types.append('fast')
            weights.append(min((wave-1)*7, 40))
        if wave >= 5:
            types.append('tank')
            weights.append(min((wave-4)*5, 25))
        if wave >= 10:
            types.append('boss')
            weights.append(min((wave-9)*2, 10))
        total = sum(weights)
        weights = [w/total for w in weights]
        return random.choices(types, weights=weights, k=1)[0]

    def create_boss(self, x, y, level, path):
        hp = 500 + level * 50
        speed = 1
        return Boss(x, y, path, self.boss_image, hp=hp, speed=speed)

    def create_explosion(self, pos):
        return Explosion(pos, self.explosion_image)

    def get_spawn_coords(self):
        x = random.randint(20, 780)
        y = random.randint(500, 550)
        return x, y

    def get_boss_spawn_coords(self):
        return random.choice([(260, 550), (515, 550)])