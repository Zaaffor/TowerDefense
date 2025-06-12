import pygame

class BuildManager:
    def __init__(self, build_zones, tower_size):

        self.build_zones = build_zones
        self.tower_size = tower_size
        self._build_cells = self._generate_build_cells()

    def _generate_build_cells(self):
        build_cells = []
        for rect in self.build_zones:
            for x in range(rect.left, rect.right, self.tower_size):
                for y in range(rect.top, rect.bottom, self.tower_size):
                    cell_rect = pygame.Rect(x, y, self.tower_size, self.tower_size)
                    if rect.contains(cell_rect):
                        build_cells.append((x, y))
        return build_cells

    def is_valid_cell(self, pos):
        for cell_x, cell_y in self._build_cells:
            cell_rect = pygame.Rect(cell_x, cell_y, self.tower_size, self.tower_size)
            if cell_rect.collidepoint(pos):
                return True
        return False

    def get_cell_coords(self, pos):
        for cell_x, cell_y in self._build_cells:
            cell_rect = pygame.Rect(cell_x, cell_y, self.tower_size, self.tower_size)
            if cell_rect.collidepoint(pos):
                return (cell_x, cell_y)
        return None

    def get_all_cells(self):
        return self._build_cells