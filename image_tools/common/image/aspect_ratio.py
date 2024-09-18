import logging
from math import ceil

from image_tools.common.image.types import IntSize, size_to_str


logger = logging.getLogger(__name__)


def aspect_ratio(size: tuple[float, float]) -> float:
    return size[0] / size[1]


def additive_adjust_size_for_aspect_ratio(size: IntSize, desired_aspect_ratio: float) -> IntSize:
    """Adjusts a size to a desired aspect ratio by adding to width or height."""

    aspect = aspect_ratio(size)
    if aspect < desired_aspect_ratio:
        # Too tall, add to width.
        new_height = size[1]
        new_width = ceil(desired_aspect_ratio * new_height)
    elif aspect > desired_aspect_ratio:
        # Too wide, add to height.
        new_width = size[0]
        new_height = ceil(new_width / desired_aspect_ratio)
    else:
        new_width = size[0]
        new_height = size[1]
    new_size = new_width, new_height
    logger.debug(f'Adjusted size: {size_to_str(size)} -> {size_to_str(new_size)}')
    # This function should never decrease the image size.
    assert new_width >= size[0]
    assert new_height >= size[1]
    return new_size
