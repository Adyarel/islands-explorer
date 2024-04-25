import random
import noise
import numpy

from src.physics import Pos

color_sea = [65, 105, 225]
color_sand = [210, 180, 140]
color_grass = [34, 139, 34]

mask_color_transparent = [0, 0, 255, 0]
mask_color_opaque = [0, 255, 0, 255]


class Map:
    """class to regroup the block of map """

    def __init__(self, sea_level, sand_height,
                 scale=500, octaves=4, persistence=0.6, lacunarity=2.0,
                 seed=0):
        """scale : niveau de zoom, 100 dézoomé, 500 zoomé
           octave : lissage fin de la carte, 4 très lisse, 10 dentelé
           persistence :
           lacunarity : lissage large de la carte, 1 très lisse, 3 dentellé
        """
        self.sea_level = sea_level
        self.sand_height = sand_height

        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity

        self.seed = 0
        """if seed == 0:
            self.seed = random.randint(0, 0x7FFFFFFF)
        else:
            self.seed = seed"""

        self.map_blocks = {}

    def get_map_block_colored(self, block_starting_pos: Pos) -> numpy.array:
        if not block_starting_pos.get_tuple() in self.map_blocks:
            self.map_blocks[block_starting_pos.get_tuple()] = Chunk(block_starting_pos, self)
        return self.map_blocks[block_starting_pos.get_tuple()].colored_map

    def get_map_block_masked(self, block_starting_pos: Pos) -> numpy.array:
        if not block_starting_pos.get_tuple() in self.map_blocks:
            self.map_blocks[block_starting_pos.get_tuple()] = Chunk(block_starting_pos, self)
        return self.map_blocks[block_starting_pos.get_tuple()].mask_map
    
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
        elif height <= self.sea_level + self.sand_height:
            return color_sand
        else:
            return color_grass

    def get_masked_by_height(self, height):
        if height < (self.sea_level + self.sand_height):
            return mask_color_transparent
        else:
            return mask_color_opaque


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

        for i in range(Chunk.block_size):
            for j in range(Chunk.block_size):
                new_i = i + starting_pos.x
                new_j = j + starting_pos.y

                height = int((noise.pnoise3(new_i / self.gmap.scale, new_j / self.gmap.scale,
                                            self.gmap.seed,
                                            octaves=self.gmap.octaves,
                                            persistence=self.gmap.persistence,
                                            lacunarity=self.gmap.lacunarity,
                                            repeatx=10000000, repeaty=10000000, base=0)
                              + 1) * 128)

                self.height_map[i][j] = height
                self.colored_map[i][j] = self.gmap.get_color_by_height(height)
                self.mask_map[i][j] = self.gmap.get_masked_by_height(height)


class SpawnPoint:
    """donne un endroit de spawn pour les bateaux"""

    def __init__(self, gmap: Map):
        self.map = gmap
        self.given_spawnpoints = []

    def get_spawn_point_near(self, pos: Pos) -> Pos:
        return Pos(-100, 0)

        # todo
        """obtention d'un point de spawn au hasard"""
        finded = False
        actual_pos = pos
        while not finded:
            c_actual_pos = actual_pos.x + 1j * actual_pos.y
            c_actual_pos *= 1.1 + 0.1j
            actual_pos = Pos(c_actual_pos.real, c_actual_pos.imag)
            if self.map.get_height_pixel(actual_pos) < self.map.sea_level - self.map.sand_height:
                finded = True
        self.given_spawnpoints.append(actual_pos)
        return actual_pos
