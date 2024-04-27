import random
import noise
import numpy

from src.physics import Pos

color_deep_sea = [16, 56, 179]
color_sea = [65, 105, 225]
color_sand = [210, 180, 140]
color_grass = [34, 139, 34]

mask_color_transparent = [0, 0, 255, 0]
mask_color_opaque = [0, 255, 0, 255]


class Map:
    """class to regroup the block of map """

    def __init__(self, sea_level, sand_level,
                 scale=500, octaves=4, persistence=0.6, lacunarity=2.0,
                 seed=0):
        """scale : niveau de zoom, 100 dézoomé, 500 zoomé
           octave : lissage fin de la carte, 4 très lisse, 10 dentelé
           persistence :
           lacunarity : lissage large de la carte, 1 très lisse, 3 dentellé
        """
        self.deepsea_level = int(sea_level * 11 / 13)
        self.sea_level = sea_level
        self.sand_level = sand_level
        self.grass_level = int(self.sand_level * 13 / 11)

        self.colors_by_height = numpy.zeros((256, 3), dtype=numpy.uint8)
        self.create_colors()

        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity

        if seed == 0:
            self.seed = random.randint(0, 0x7FFFFFFF)
        else:
            self.seed = seed

        self.map_blocks = {}

    def create_colors(self):
        for i in range(0, self.deepsea_level):
            self.colors_by_height[i] = color_deep_sea
        for i in range(self.deepsea_level, self.sea_level):
            color = [0, 0, 0]
            a = self.deepsea_level
            b = self.deepsea_level + 1 / 2 * (self.sea_level - self.deepsea_level)
            c = self.sea_level
            fa = color_deep_sea
            fb = [0, 0, 0]
            for j in range(3):
                fb[j] = color_deep_sea[j] + 1 / 3 * (color_sea[j] - color_deep_sea[j])
            fc = color_sea
            for j in range(3):
                color[j] = (i - b) * (i - c) / ((a - b) * (a - c)) * fa[j] + \
                           (i - a) * (i - c) / ((b - a) * (b - c)) * fb[j] + \
                           (i - a) * (i - b) / ((c - a) * (c - b)) * fc[j]
            self.colors_by_height[i] = color
        for i in range(self.sea_level, self.sand_level):
            self.colors_by_height[i] = color_sand
        for i in range(self.sand_level, 256):
            self.colors_by_height[i] = color_grass

    # --- full chunk related ---

    def get_map_block_colored(self, block_starting_pos: Pos) -> numpy.array:
        if not block_starting_pos.get_tuple() in self.map_blocks:
            self.map_blocks[block_starting_pos.get_tuple()] = Chunk(block_starting_pos, self)
        return self.map_blocks[block_starting_pos.get_tuple()].colored_map

    def get_map_block_masked(self, block_starting_pos: Pos) -> numpy.array:
        if not block_starting_pos.get_tuple() in self.map_blocks:
            self.map_blocks[block_starting_pos.get_tuple()] = Chunk(block_starting_pos, self)
        return self.map_blocks[block_starting_pos.get_tuple()].mask_map

    # --- pixel related ---
    def get_height_pixel(self, pos: Pos) -> int:
        starting_pos = Pos((pos.x // Chunk.block_size) * Chunk.block_size,
                           (pos.y // Chunk.block_size) * Chunk.block_size)
        if not starting_pos.get_tuple() in self.map_blocks:
            self.map_blocks[starting_pos.get_tuple()] = Chunk(starting_pos, self)
        chunk = self.map_blocks[starting_pos.get_tuple()]
        return chunk.height_map[int(pos.x % Chunk.block_size), int(pos.y % Chunk.block_size)]

    def get_color_by_height(self, height):
        if height <= self.sea_level:
            return color_sea
        elif height <= self.sand_level:
            return color_sand
        else:
            return color_grass

    def get_color_by_height2(self, height):
        return self.colors_by_height[height]

    def get_masked_by_height(self, height):
        if height < self.sand_level:
            return mask_color_transparent
        else:
            return mask_color_opaque


demult = 1


class Chunk:
    """block of the gmap"""
    block_size = 256

    def __init__(self, starting_pos: Pos, gmap: Map):
        """generate terrain by block"""
        self.gmap = gmap
        self.starting_pos = starting_pos

        self.height_map = numpy.zeros((self.block_size, self.block_size), numpy.uint8)
        self.colored_map = numpy.zeros((self.block_size, self.block_size, 3), numpy.uint8)
        self.mask_map = numpy.zeros((self.block_size, self.block_size, 4), numpy.uint8)
        self.generate_terrain()

    def generate_terrain(self):

        for i in range(Chunk.block_size):
            for j in range(Chunk.block_size):
                new_i = i + self.starting_pos.x
                new_j = j + self.starting_pos.y

                height = int((noise.pnoise3(new_i / self.gmap.scale, new_j / self.gmap.scale,
                                            self.gmap.seed,
                                            octaves=self.gmap.octaves,
                                            persistence=self.gmap.persistence,
                                            lacunarity=self.gmap.lacunarity,
                                            repeatx=10000000, repeaty=10000000, base=0)
                              + 1) * 128)

                self.height_map[i][j] = height
                self.colored_map[i][j] = self.gmap.get_color_by_height2(height)
                self.mask_map[i][j] = self.gmap.get_masked_by_height(height)
        print("Chunk ", self.starting_pos, ": min moy max")
        print(numpy.min(self.height_map))
        print(numpy.sum(self.height_map) / Chunk.block_size ** 2)
        print(numpy.max(self.height_map))

    def generate_terrain2(self):

        for i in range(Chunk.block_size, demult):
            for j in range(Chunk.block_size, demult):
                new_i = i + self.starting_pos.x
                new_j = j + self.starting_pos.y

                height = int((noise.pnoise3(new_i / self.gmap.scale, new_j / self.gmap.scale,
                                            self.gmap.seed,
                                            octaves=self.gmap.octaves,
                                            persistence=self.gmap.persistence,
                                            lacunarity=self.gmap.lacunarity,
                                            repeatx=10000000, repeaty=10000000, base=0)
                              + 1) * 128)

                self.height_map[i: i + demult][j: j + demult] = height * numpy.ones((demult, demult), dtype=numpy.uint8)
        print("Chunk ", self.starting_pos, ": min moy max")
        print(numpy.min(self.height_map))
        print(numpy.sum(self.height_map) / Chunk.block_size ** 2)
        print(numpy.max(self.height_map))

        """for i in range(Chunk.block_size):
            for j in range(Chunk.block_size):
                new_i = i + self.starting_pos.x
                new_j = j + self.starting_pos.y
                height = int((noise.pnoise3(new_i * demult / self.gmap.scale, new_j * demult / self.gmap.scale,
                                            self.gmap.seed,
                                            octaves=self.gmap.octaves,
                                            persistence=self.gmap.persistence,
                                            lacunarity=self.gmap.lacunarity,
                                            repeatx=10000000, repeaty=10000000, base=0)
                              + 1) * 128 / demult)
                self.height_map[i][j] += height"""

        for i in range(Chunk.block_size):
            for j in range(Chunk.block_size):
                self.colored_map[i][j] = self.gmap.get_color_by_height2(self.height_map[i][j])
                self.mask_map[i][j] = self.gmap.get_masked_by_height(self.height_map[i][j])


class SpawnPoint:
    """donne un endroit de spawn pour les bateaux"""

    def __init__(self, gmap: Map):
        self.map = gmap
        self.given_spawnpoints = []

    def get_spawn_point_near(self, pos: Pos) -> Pos:
        """obtention d'un point de spawn au hasard"""
        found = False
        actual_pos = pos - Pos(100, 0)
        while not found or actual_pos in self.given_spawnpoints:
            c_actual_pos = actual_pos.x + 1j * actual_pos.y
            c_actual_pos *= 1 + 0.5j
            actual_pos = Pos(c_actual_pos.real, c_actual_pos.imag)
            if self.map.get_height_pixel(actual_pos) + self.map.sand_level < 2 * self.map.sea_level:
                found = True
        self.given_spawnpoints.append(actual_pos)
        return actual_pos
