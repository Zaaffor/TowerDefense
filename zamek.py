class Castle:
    def __init__(self, hp=100):
        self.hp = hp

    def take_damage(self, dmg):
        self.hp -= dmg

    def is_destroyed(self):
        return self.hp <= 0