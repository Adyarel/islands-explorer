import pygame
import numpy


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
