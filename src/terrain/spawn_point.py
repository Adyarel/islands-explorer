from src.constants import deepsea_level
from src.terrain.Gmap import Gmap
from src.utils.physics import Pos


class SpawnPoint:
    """donne un endroit de spawn pour les bateaux"""

    def __init__(self, gmap: Gmap):
        self.map = gmap
        self.given_spawn_points = []

    def get_spawn_point_near(self, pos: Pos) -> Pos:
        """obtention d'un point de spawn au hasard"""
        found = False
        actual_pos = pos - Pos(100, 0)
        while not found or actual_pos in self.given_spawn_points:
            c_actual_pos = actual_pos.x + 1j * actual_pos.y
            c_actual_pos *= 1 + 0.5j
            actual_pos = Pos(c_actual_pos.real, c_actual_pos.imag)
            if self.map.get_height_pixel(actual_pos) < deepsea_level:
                found = True
        self.given_spawn_points.append(actual_pos)
        return actual_pos
