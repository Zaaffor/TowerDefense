import pygame

class Attack:
    def attack(self, tower, enemies):
        return NotImplementedError()
    
class SingleAttack(Attack):
    def attack(self, tower, enemies):
        najblizszy = None
        min_dist = float('inf')
        for enemy in enemies:
            if TowerUtility.in_range(tower, enemy):
                dist = TowerUtility.distance_to(tower, enemy)
                if dist < min_dist:
                    min_dist = dist
                    najblizszy = enemy
        if najblizszy:
            najblizszy.take_damage(tower.stats.damage)
            tower.stats.last_hit = pygame.time.get_ticks()

class TowerStats:
    def __init__(self, radius, damage, delay=500):
        self.radius = radius
        self.damage = damage
        self.delay = delay
        self.path1_level = 0
        self.path2_level = 0
        self.path3_level = 0
        self.max_path_level = 5
        self.last_hit = 0
    
    def upgrade(self, path):
        if path == 1 and self.path1_level < self.max_path_level:
            self.path1_level += 1
            self.radius += 20
            return True
        elif path == 2 and self.path2_level < self.max_path_level:
            self.path2_level += 1
            self.delay = max(100, self.delay - 100)
            return True
        elif path == 3 and self.path3_level < self.max_path_level:
            self.path3_level += 1
            self.damage += 5
            return True
        return False
    
    def get_upgrade_cost(self, path):
        return 5 + (max(self.path1_level, self.path2_level, self.path3_level) * 5)
    
class TowerUtility:
    @staticmethod
    def in_range(tower, enemy):
        return TowerUtility.distance_to(tower, enemy) <= tower.stats.radius
    
    @staticmethod
    def distance_to(tower, enemy):
        cx = tower.x + tower.rect.width // 2
        cy = tower.y + tower.rect.height // 2
        ex = enemy.x + enemy.rect.width // 2
        ey = enemy.y + enemy.rect.height // 2
        return ((cx - ex) ** 2 + (cy - ey) ** 2) ** 0.5

class TowerImg:
    def __init__(self, tower, image):
        self.tower = tower
        self.image = image
        self.path1_rect = pygame.Rect(-100, -100, 1, 1)
        self.path2_rect = pygame.Rect(-100, -100, 1, 1)
        self.path3_rect = pygame.Rect(-100, -100, 1, 1)

    def draw(self, surface):
        surface.blit(self.image, (self.tower.x, self.tower.y))
        pygame.draw.circle(surface, (0, 0, 255), (self.tower.x + 25, self.tower.y + 25), self.tower.stats.radius, 1)
        if self.tower.selected:
            self.draw_upgrade_menu(surface)

    def check_upgrade_click(self, pos):
        if self.path1_rect.collidepoint(pos):
            return 1
        if self.path2_rect.collidepoint(pos):
            return 2
        if self.path3_rect.collidepoint(pos):
            return 3
        return None

    def draw_upgrade_menu(self, surface):
        x = self.tower.x
        y = self.tower.y

        menu_rect = pygame.Rect(x - 50, y - 120, 150, 110)
        pygame.draw.rect(surface, (50, 50, 50), menu_rect)
        pygame.draw.rect(surface, (200, 200, 200), menu_rect, 2)

        font = pygame.font.SysFont(None, 20)
        small_font = pygame.font.SysFont(None, 16)

        # Ścieżka 1 (zasięg)
        self.path1_rect = pygame.Rect(x - 40, y - 110, 130, 30)
        path1_color = (100, 100, 255) if self.tower.stats.path1_level < self.tower.stats.max_path_level else (150, 150, 150)
        pygame.draw.rect(surface, path1_color, self.path1_rect)
        path1_text = font.render(f"Range ({self.tower.stats.path1_level}/5)", True, (255, 255, 255))
        surface.blit(path1_text, (self.path1_rect.x + 5, self.path1_rect.y + 5))
        if self.tower.stats.path1_level < self.tower.stats.max_path_level:
            cost_text = small_font.render(f"Cost: {self.tower.stats.get_upgrade_cost(1)}", True, (255, 255, 0))
            surface.blit(cost_text, (self.path1_rect.x + 5, self.path1_rect.y + 20))

        # Ścieżka 2 (szybkość)
        self.path2_rect = pygame.Rect(x - 40, y - 75, 130, 30)
        path2_color = (100, 100, 255) if self.tower.stats.path2_level < self.tower.stats.max_path_level else (150, 150, 150)
        pygame.draw.rect(surface, path2_color, self.path2_rect)
        path2_text = font.render(f"Speed ({self.tower.stats.path2_level}/5)", True, (255, 255, 255))
        surface.blit(path2_text, (self.path2_rect.x + 5, self.path2_rect.y + 5))
        if self.tower.stats.path2_level < self.tower.stats.max_path_level:
            cost_text = small_font.render(f"Cost: {self.tower.stats.get_upgrade_cost(2)}", True, (255, 255, 0))
            surface.blit(cost_text, (self.path2_rect.x + 5, self.path2_rect.y + 20))

        # Ścieżka 3 (moc)
        self.path3_rect = pygame.Rect(x - 40, y - 40, 130, 30)
        path3_color = (100, 100, 255) if self.tower.stats.path3_level < self.tower.stats.max_path_level else (150, 150, 150)
        pygame.draw.rect(surface, path3_color, self.path3_rect)
        path3_text = font.render(f"Power ({self.tower.stats.path3_level}/5)", True, (255, 255, 255))
        surface.blit(path3_text, (self.path3_rect.x + 5, self.path3_rect.y + 5))
        if self.tower.stats.path3_level < self.tower.stats.max_path_level:
            cost_text = small_font.render(f"Cost: {self.tower.stats.get_upgrade_cost(3)}", True, (255, 255, 0))
            surface.blit(cost_text, (self.path3_rect.x + 5, self.path3_rect.y + 20))

class Tower:
    def __init__(self, x, y, attack=None, image=None):
        self.x = x
        self.y = y
        self.selected = False
        self.stats = TowerStats(radius=120, damage=10)
        self.attack_strategy = attack if attack else SingleAttack()
        if image is not None:
            self.image = pygame.transform.scale(image, (50, 50))
        else:
            self.image = pygame.Surface((50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.view = TowerImg(self, self.image)
    
    def attack(self, enemies):
        now = pygame.time.get_ticks()
        if now - self.stats.last_hit >= self.stats.delay:
            self.attack_strategy.attack(self, enemies)
    
    def check_upgrade_click(self, pos):
        return self.view.check_upgrade_click(pos)
    
    def upgrade(self, path):
        return self.stats.upgrade(path)

    def get_upgrade_cost(self, path):
        return self.stats.get_upgrade_cost(path)

    def draw(self, surface):
        self.view.draw(surface)

class TowerFactory:
    def __init__(self):
        self.tower_image_path = "images/wieza.png"

    def create_tower(self, x, y):
        image = pygame.image.load(self.tower_image_path).convert_alpha()
        return Tower(x, y, image=image)