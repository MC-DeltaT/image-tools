import logging
from math import ceil

import numpy as np
from colour import Color
from PIL import ImageOps
from PIL.Image import Image

from image_tools.common.image.aspect_ratio import additive_adjust_size_for_aspect_ratio, aspect_ratio
from image_tools.common.image.border import BorderSize
from image_tools.common.image.types import IntSize, size_to_str
from image_tools.instagramable.aspect_ratio import adjust_aspect_ratio

logger = logging.getLogger(__name__)


def calculate_baseline_border_size(image_size: IntSize, baseline_border_amount: float) -> BorderSize:
    """Calculates the baseline border size for an image based off its dimensions.
    This border size is not final, it may need to be adjusted for aspect ratio."""

    avg_dim = np.mean(image_size)
    border_width = int(round(baseline_border_amount * avg_dim))
    border_height = int(round(baseline_border_amount * avg_dim))
    border_size = BorderSize(top=border_height, bottom=border_height, left=border_width, right=border_width)
    logger.debug(f"Baseline border size: {border_size}")
    return border_size


def adjust_border_for_aspect_ratio(image_size: IntSize, baseline_border: BorderSize) -> BorderSize:
    """Adjusts the baseline border size so the aspect ratio is appropriate for Instagram."""

    # Calculate the image size and aspect ratio with  the baseline border, then adjust it by adding size.
    size_with_baseline_border = (
        image_size[0] + baseline_border.left + baseline_border.right,
        image_size[1] + baseline_border.top + baseline_border.bottom,
    )
    adjusted_aspect_ratio = adjust_aspect_ratio(aspect_ratio(size_with_baseline_border))
    adjusted_image_size = additive_adjust_size_for_aspect_ratio(size_with_baseline_border, adjusted_aspect_ratio)

    # Calculate backwards to the adjusted border size.
    new_border_width = adjusted_image_size[0] - image_size[0]
    new_border_height = adjusted_image_size[1] - image_size[1]
    # Note image is always centered. Border is split evenly between each side.
    new_border_top_bottom = ceil(new_border_height / 2)
    new_border_left_right = ceil(new_border_width / 2)
    new_border = BorderSize(
        top=new_border_top_bottom, bottom=new_border_top_bottom, left=new_border_left_right, right=new_border_left_right
    )

    logger.debug(f"Adjusted border size: {new_border}")
    assert new_border.all_sides
    return new_border


def calculate_new_border_size(image_size: IntSize, baseline_border_size: float) -> BorderSize:
    """Calculates the border size in pixels."""

    # Try to create a constant-sized border according to baseline_border_size.
    # If the resulting image falls outside the aspect ratio constraint, expand the border in one dimension such that the
    # aspect ratio becomes valid.
    baseline_border = calculate_baseline_border_size(image_size, baseline_border_size)
    border = adjust_border_for_aspect_ratio(image_size, baseline_border)
    return border


def apply_new_border(image: Image, colour: Color, baseline_size: float) -> Image:
    border_size = calculate_new_border_size(image.size, baseline_size)
    new_image = ImageOps.expand(image, border=border_size.pil_tuple, fill=colour.get_hex_l())
    logger.debug(
        f"Dimensions after border {size_to_str(new_image.size)} (aspect ratio {aspect_ratio(new_image.size):.2f})"
    )
    return new_image
