from typing import Tuple

import numpy

# --- map ---
deepsea_level: int = 114
sea_level: int = 136
sand_level: int = 140
grass_level: int = 166

"""
scale : niveau de zoom, 100 dézoomé, 500 zoomé
octave : lissage fin de la carte, 4 très lisse, 10 dentelé
persistence :
lacunarity : lissage large de la carte, 1 très lisse, 3 dentellé
"""

perlin_1_scale: int = 500
perlin_1_octaves: int = 4
perlin_1_persistence: float = 0.6
perlin_1_lacunarity: float = 2.0

perlin_2_scale: int = 250
perlin_2_octaves: int = 8
perlin_2_persistence: float = 0.6
perlin_2_lacunarity: float = 2.0

chunk_block_size: int = 256

color_deep_sea: Tuple[int, int, int] = (16, 56, 179)
color_sea: Tuple[int, int, int] = (65, 105, 225)
color_sand: Tuple[int, int, int] = (210, 180, 140)
color_grass: Tuple[int, int, int] = (34, 139, 34)
color_dirt: Tuple[int, int, int] = (118, 88, 67)

mask_color_transparent: Tuple[int, int, int, int] = (0, 0, 255, 0)
mask_color_opaque: Tuple[int, int, int, int] = (0, 255, 0, 255)


# --- Chunk ---

demult = 1
identity = numpy.ones((demult, demult), dtype=numpy.uint8)

# --- boat ---

black: Tuple[int, int, int] = (0, 0, 0)
green: Tuple[int, int, int] = (65, 225, 77)
