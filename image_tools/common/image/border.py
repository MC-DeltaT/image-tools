from dataclasses import dataclass
import logging

import numpy as np
from PIL.Image import Image


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BorderSize:
    # Size in pixels of the border on each side.
    top: int
    bottom: int
    left: int
    right: int

    @property
    def pil_tuple(self) -> tuple[int, int, int, int]:
        """As used in various PIL functions: left, top, right, bottom."""

        return (self.left, self.top, self.right, self.bottom)

    @property
    def all_sides(self) -> bool:
        """Returns true if there is a border on all sides."""

        return all(b > 0 for b in (self.top, self.bottom, self.left, self.right))

    @property
    def any_side(self) -> bool:
        """Returns true if there is a border on any side."""

        return any(b > 0 for b in (self.top, self.bottom, self.left, self.right))


# Relative diff above which pixels are considered to be different colours for the purpose of border detection.
BORDER_DIFF_COLOUR_THRESHOLD = 0.05

# Proportion of pixels in a border size that are allowed to be different.
BORDER_DIFF_PROPORTION_THRESHOLD = 0.01


def detect_border(image: Image, channel_diff_threshold: float = BORDER_DIFF_COLOUR_THRESHOLD,
        pixel_count_threshold: float = BORDER_DIFF_PROPORTION_THRESHOLD) -> BorderSize:
    """Infers the size of an image's border from pixel values.
        The border must be uniform colour on all sides."""

    data = np.array(image)
    # Shape is (height, width, channels)

    # Reference top left pixel, to which colours are compared
    ref_colour = data[0, 0].astype(float)
    # Relative differences are a proportion of the max pixel value.
    diff_ref = np.max(data, axis=(0, 1))

    def is_same_colour(pixels: np.ndarray) -> bool:
        # Cast to avoid clipping on unsigned pixel types.
        pixels = pixels.astype(float)
        diffs = pixels - ref_colour
        # Each channel must be within the threshold.
        different = np.abs(diffs) > channel_diff_threshold * diff_ref
        total_pixels = pixels.shape[0] * pixels.shape[1]
        different_proportion = np.count_nonzero(different) / total_pixels
        overall_same = different_proportion <= pixel_count_threshold
        return overall_same

    def find_border(axis: int, reverse: bool) -> int:
        depth = 1
        while True:
            index = -depth if reverse else depth - 1
            side = data[index, :] if axis == 0 else data[:, index]
            if not is_same_colour(side):
                return depth - 1
            depth += 1

    border_size = BorderSize(
        top=find_border(0, False),
        bottom=find_border(0, True),
        left=find_border(1, False),
        right=find_border(1, True)
    )
    logger.debug(f'Detected border: {border_size}')
    return border_size


def remove_border(image: Image, border: BorderSize | None = None) -> Image:
    """Crop an image to remove its border.
    
        :param border: Known border size. If `None`, inferred from the image content."""

    if border is None:
        border = detect_border(image)
    if border.any_side:
        new_size = (
            border.left,   # Left
            border.top,    # Top
            image.width - border.right,    # Right
            image.height - border.bottom,  # Bottom
        )
        logger.debug(f'Removing border, cropping to {new_size}')
        new_image = image.crop(new_size)
        return new_image
    else:
        return image
