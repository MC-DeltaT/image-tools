import logging

from PIL.Image import Image, Resampling

from image_tools.common.image.sizing import clamp_max_dimension
from image_tools.common.image.types import size_to_str

logger = logging.getLogger(__name__)


def adjust_image_size(image: Image, maximum_dimension: int) -> Image:
    """Clamps the image size such that the largest dimension is <= `maximum_dimension`, while maintaining aspect ratio."""

    new_size = clamp_max_dimension(image.size, maximum_dimension)
    if new_size == image.size:
        return image
    else:
        new_image = image.resize(new_size, resample=Resampling.LANCZOS)
        logging.debug(f"Resized image: {size_to_str(image.size)} -> {size_to_str(new_image.size)}")
        return new_image
