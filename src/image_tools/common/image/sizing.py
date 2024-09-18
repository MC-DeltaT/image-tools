from .types import IntSize


def clamp_max_dimension(size: IntSize, maximum_dimension: int) -> IntSize:
    """Clamps a size such that the largest dimension is <= `maximum_dimension`, while maintaining aspect ratio."""

    largest_dim = max(size)
    if largest_dim <= maximum_dimension:
        return size
    else:
        scale = maximum_dimension / largest_dim
        new_width = int(round(size[0] * scale))
        new_height = int(round(size[1] * scale))
        return new_width, new_height
