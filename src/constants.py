
# --- map ---
deepsea_level = 114
sea_level = 135
sand_level = 141
grass_level = 165

"""
scale : niveau de zoom, 100 dézoomé, 500 zoomé
octave : lissage fin de la carte, 4 très lisse, 10 dentelé
persistence :
lacunarity : lissage large de la carte, 1 très lisse, 3 dentellé
"""

perlin_1_scale = 500
perlin_1_octaves = 4
perlin_1_persistence = 0.6
perlin_1_lacunarity = 2.0

perlin_2_scale = 250
perlin_2_octaves = 8
perlin_2_persistence = 0.6
perlin_2_lacunarity = 2.0

chunk_block_size = 256

color_deep_sea = [16, 56, 179]
color_sea = [65, 105, 225]
color_sand = [210, 180, 140]
color_grass = [34, 139, 34]
color_dirt = [118, 88, 67]

mask_color_transparent = [0, 0, 255, 0]
mask_color_opaque = [0, 255, 0, 255]

# --- boat ---

black = (0, 0, 0)
green = (65, 225, 77)
