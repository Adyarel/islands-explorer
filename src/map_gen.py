import random
import noise
import numpy

from src.physics import Pos

color_sea = [65, 105, 225]
color_sand = [210, 180, 140]
color_grass = [34, 139, 34]


class GMap:
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

        if seed == 0:
            self.seed = random.randint(0, 0x7FFFFFFF)
        else:
            self.seed = seed

        self.map_blocks = {}

    def get_map_block(self, block_starting_pos: Pos):
        if block_starting_pos.get_tuple() in self.map_blocks:
            return self.map_blocks[block_starting_pos]
        else:
            self.map_blocks[block_starting_pos.get_tuple()] = Chunk(block_starting_pos, self)
            return self.map_blocks[block_starting_pos.get_tuple()]


class Chunk:
    """block of the gmap"""
    block_size = 16

    def __init__(self, starting_pos: Pos, gmap: GMap):
        """generate terrain by block"""
        self.gmap = gmap
        self.starting_pos = starting_pos

        self.height_map = numpy.zeros((self.block_size, self.block_size), numpy.uint8)
        self.colored_map = numpy.zeros((self.block_size, self.block_size, 3), numpy.uint8)

        for i in range(Chunk.block_size):
            for j in range(Chunk.block_size):
                new_i = i + starting_pos.y
                new_j = j + starting_pos.x

                self.height_map[i][j] = int(noise.pnoise3(new_i / self.gmap.scale, new_j / self.gmap.scale,
                                                          self.gmap.seed,
                                                          octaves=self.gmap.octaves,
                                                          persistence=self.gmap.persistence,
                                                          lacunarity=self.gmap.lacunarity,
                                                          repeatx=10000000, repeaty=10000000, base=0)
                                            + 1) * 128

                if self.height_map[i][j] <= self.gmap.sea_level:
                    self.colored_map[i][j] = color_sea
                elif self.height_map[i][j] <= self.gmap.sea_level + self.gmap.sand_height:
                    self.colored_map[i][j] = color_sand
                else:
                    self.colored_map[i][j] = color_grass
