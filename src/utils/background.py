import pygame
import numpy

from src.constants import *
from src.map_gen import Map
from src.utils.physics import Pos
from src.utils.utils import get_starting_pos_chunk


class BackGround(pygame.sprite.Sprite):

    def __init__(self, image, mask, rect, *groups):
        super().__init__(*groups)
        self.image = image
        self.mask = mask
        self.rect = rect


def get_map_bg(game):
    cbs = chunk_block_size
    cam_pos = Pos(int(game.camera_pos.x), int(game.camera_pos.y))

    # first, get the chunk we need to draw bg
    chunks_needed = []
    i = 0
    while ((cam_pos.x + cbs * i) // cbs) * cbs < cam_pos.x + game.screen_size[0]:
        chunks_needed.append([])
        j = 0
        while ((cam_pos.y + cbs * j) // cbs) * cbs < cam_pos.y + game.screen_size[1]:
            chunks_needed[i] += [Pos(((cam_pos.x + cbs * i) // cbs) * cbs,
                                     ((cam_pos.y + cbs * j) // cbs) * cbs)]
            j += 1
        i += 1

    # then, make a huge map made of the chunks

    bigcolormap = numpy.zeros((len(chunks_needed) * cbs, len(chunks_needed[0]) * cbs, 3), numpy.uint8)
    bigmaskmap = numpy.zeros((len(chunks_needed) * cbs, len(chunks_needed[0]) * cbs, 4), numpy.uint8)

    for i in range(len(chunks_needed)):
        for j in range(len(chunks_needed[i])):
            bigcolormap[i * cbs: (i + 1) * cbs, j * cbs: (j + 1) * cbs] = \
                game.map.get_map_block_colored(chunks_needed[i][j])
            bigmaskmap[i * cbs: (i + 1) * cbs, j * cbs: (j + 1) * cbs] = \
                game.map.get_map_block_masked(chunks_needed[i][j])

    # finally, reduce to the screen size

    colormap = bigcolormap[cam_pos.x % cbs: cam_pos.x % cbs + game.screen_size[0],
                           cam_pos.y % cbs: cam_pos.y % cbs + game.screen_size[1]]
    maskmap = bigmaskmap[cam_pos.x % cbs: cam_pos.x % cbs + game.screen_size[0],
                         cam_pos.y % cbs: cam_pos.y % cbs + game.screen_size[1]]

    image = pygame.surfarray.make_surface(colormap)
    mask = pygame.mask.from_surface(make_surface_rgba(maskmap))
    rect = image.get_rect()
    return BackGround(image, mask, rect)


def get_next_chunk_to_generate(near_pos: Pos, map_data: Map):
    # todo produit scalaire pour la direction, norme pour la distance
    found = False
    potential_chunk = get_starting_pos_chunk(near_pos)
    while not found:
        if not map_data.is_chunk_exist(potential_chunk):
            return potential_chunk


def make_surface_rgba(array):
    """Returns a surface made from a [w, h, 4] numpy array with per-pixel alpha"""
    shape = array.shape
    if len(shape) != 3 and shape[2] != 4:
        raise ValueError("Array not RGBA")

    # Create a surface the same width and height as array and with per-pixel alpha
    surface = pygame.Surface(shape[0:2], pygame.SRCALPHA, 32)

    # Copy the rgb part of array to the new surface.
    pygame.pixelcopy.array_to_surface(surface, array[:, :, 0:3])

    # Copy the alpha part of array to the surface using a pixels-alpha view of the surface
    surface_alpha = numpy.array(surface.get_view("A"), dtype=numpy.uint8, copy=False)
    surface_alpha[:, :] = array[:, :, 3]

    return surface
