import noise
import numpy

from src.constants import chunk_block_size, demult, perlin_1_scale, perlin_1_octaves, perlin_1_persistence, \
    perlin_1_lacunarity, perlin_2_scale, perlin_2_octaves, perlin_2_persistence, perlin_2_lacunarity, identity
from src.utils.physics import Pos
from src.utils.utils import get_mask_color_by_height


class Chunk:
    """block of the gmap"""

    def __init__(self, starting_pos: Pos, gmap):
        """generate terrain by block"""
        self.gmap = gmap
        self.starting_pos: Pos = starting_pos

        self.height_map: numpy.ndarray = numpy.zeros((chunk_block_size, chunk_block_size), numpy.uint8)
        self.colored_map: numpy.ndarray = numpy.zeros((chunk_block_size, chunk_block_size, 3), numpy.uint8)
        self.mask_map: numpy.ndarray = numpy.zeros((chunk_block_size, chunk_block_size, 4), numpy.uint8)
        self.generate_terrain()

    def generate_terrain(self):

        for i in range(0, chunk_block_size, demult):
            for j in range(0, chunk_block_size, demult):
                new_i = i + self.starting_pos.x
                new_j = j + self.starting_pos.y

                height = 0.8 * noise.pnoise3(new_i / perlin_1_scale, new_j / perlin_1_scale,
                                             self.gmap.seed,
                                             octaves=perlin_1_octaves,
                                             persistence=perlin_1_persistence,
                                             lacunarity=perlin_1_lacunarity,
                                             repeatx=10000000, repeaty=10000000, base=0)
                height += 0.2 * noise.pnoise3(new_i / perlin_2_scale, new_j / perlin_2_scale,
                                              self.gmap.seed,
                                              octaves=perlin_2_octaves,
                                              persistence=perlin_2_persistence,
                                              lacunarity=perlin_2_lacunarity,
                                              repeatx=10000000, repeaty=10000000, base=0)

                self.height_map[i: i + demult, j: j + demult] = int((height + 1) * 128) * identity
        for i in range(chunk_block_size):
            for j in range(chunk_block_size):
                self.colored_map[i, j] = self.gmap.get_color_by_height(self.height_map[i, j])
                self.mask_map[i, j] = get_mask_color_by_height(self.height_map[i, j])
        """print("Chunk ", self.starting_pos, ": min moy max")
        print(numpy.min(self.height_map))
        print(numpy.sum(self.height_map) / Chunk.block_size ** 2)
        print(numpy.max(self.height_map))"""

    def __str__(self):
        return "Chunk: " + str(self.starting_pos)
