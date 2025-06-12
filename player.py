class Player:
    def __init__(self, gold=10, tower_cost=10):
        self.gold = gold
        self.tower_cost = tower_cost

    def can_afford(self, cost):
        return self.gold >= cost

    def buy_tower(self):
        if self.can_afford(self.tower_cost):
            self.gold -= self.tower_cost
            self.tower_cost += 2
            return True
        return False

    def pay_upgrade(self, cost):
        if self.can_afford(cost):
            self.gold -= cost
            return True
        return False