from src.utils.physics import Pos
from src.constants import *


def get_starting_pos_chunk(pos: Pos) -> Pos:
    return Pos((pos.x // chunk_block_size) * chunk_block_size,
               (pos.y // chunk_block_size) * chunk_block_size)


def get_mask_color_by_height(height) -> Tuple[int, int, int, int]:
    if height < sand_level:
        return mask_color_transparent
    else:
        return mask_color_opaque
