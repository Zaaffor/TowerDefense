import pygame
from abc import ABC, abstractmethod

class Fala(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_enemy_count(self, wave_num: int) -> int:
        pass

    @abstractmethod
    def get_spawn_count(self, wave_num: int) -> int:
        pass

    @abstractmethod
    def has_boss(self, wave_num: int) -> bool:
        pass

class FalaStandard(Fala):
    def get_enemy_count(self, wave_num: int) -> int:
        return 5 + (wave_num - 1) * 2
    
    def get_spawn_count(self, wave_num: int) -> int:
        return max(500, 2000 - (wave_num - 1) * 200)
    
    def has_boss(self, wave_num):
        return wave_num % 5 == 0
    
class FalaCiezka(Fala):
    def get_enemy_count(self, wave_num: int) -> int:
        return 8 + (wave_num - 1) * 3
    
    def get_spawn_count(self, wave_num: int) -> int:
        return max(300, 1500 - (wave_num - 1) * 150)
    
    def has_boss(self, wave_num):
        return wave_num % 3 == 0

class FalaManager:
    def __init__(self, wave_strategy: Fala, break_duration=5000):
        self.wave_strategy = wave_strategy
        self.current_wave = 1
        self.enemies_to_spawn = self.wave_strategy.get_enemy_count(self.current_wave)
        self.spawned = 0
        self.spawn_interval = self.wave_strategy.get_spawn_count(self.current_wave)
        self.last_spawn = pygame.time.get_ticks()
        self.last_wave = pygame.time.get_ticks()
        self.break_duration = break_duration
        self.in_break = False
        self.boss_spawned = False

    def update(self):
        teraz = pygame.time.get_ticks()
        if self.in_break and teraz - self.last_wave > self.break_duration:
            self.next_wave(teraz)

    def next_wave(self, czas):
        self.current_wave += 1
        self.enemies_to_spawn = self.wave_strategy.get_enemy_count(self.current_wave)
        self.spawn_interval = self.wave_strategy.get_spawn_count(self.current_wave)
        self.spawned = 0
        self.last_wave = czas
        self.in_break = False
        self.boss_spawned = False

    def should_spawn(self) -> bool:
        teraz = pygame.time.get_ticks()
        return (not self.in_break and self.spawned < self.enemies_to_spawn and teraz - self.last_spawn >= self.spawn_interval)
    
    def rejestr(self):
        self.spawned += 1
        self.last_spawn = pygame.time.get_ticks()
        if self.spawned >= self.enemies_to_spawn:
            self.in_break = True
            self.last_wave = pygame.time.get_ticks()

    def is_boss_wave(self) -> bool:
        return self.wave_strategy.has_boss(self.current_wave)

    def boss_already_spawned(self) -> bool:
        return self.boss_spawned

    def set_boss_spawned(self):
        self.boss_spawned = True

    def get_current_wave(self) -> int:
        return self.current_wave

    def get_enemies_left_to_spawn(self) -> int:
        return self.enemies_to_spawn - self.spawned

    def get_spawn_interval(self) -> int:
        return self.spawn_interval

    def in_break_time(self) -> bool:
        return self.in_break