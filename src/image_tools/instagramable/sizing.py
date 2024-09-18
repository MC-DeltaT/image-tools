import logging

from PIL.Image import Image, Resampling

from image_tools.common.image.types import IntSize, size_to_str

logger = logging.getLogger(__name__)


def clamp_size_by_max_dimension(size: IntSize, maximum_dimension: int) -> IntSize:
    """Clamps a size such that the largest dimension is <= `maximum_dimension`, while maintaining aspect ratio."""

    largest_dim = max(size)
    if largest_dim <= maximum_dimension:
        return size
    else:
        scale = maximum_dimension / largest_dim
        new_width = int(round(size[0] * scale))
        new_height = int(round(size[1] * scale))
        return new_width, new_height


def adjust_image_size(image: Image, maximum_dimension: int) -> Image:
    """Clamps the image size such that the largest dimension is <= `maximum_dimension`, while maintaining aspect ratio."""

    new_size = clamp_size_by_max_dimension(image.size, maximum_dimension)
    if new_size == image.size:
        return image
    else:
        new_image = image.resize(new_size, resample=Resampling.LANCZOS)
        logging.debug(f"Resized image: {size_to_str(image.size)} -> {size_to_str(new_image.size)}")
        return new_image
