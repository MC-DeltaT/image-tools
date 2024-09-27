import logging
from dataclasses import dataclass
from enum import Enum

from colour import Color
from PIL import ImageDraw
from PIL.Image import Image

from image_tools.annotate_info.metadata import ImageMetadata
from image_tools.common.image.types import IntPos, IntSize

logger = logging.getLogger(__name__)


class TextPosition(Enum):
    TOP_LEFT = "top-left"
    TOP_MIDDLE = "top-middle"
    TOP_RIGHT = "top-right"
    MIDDLE_LEFT = "middle-left"
    MIDDLE = "middle"
    MIDDLE_RIGHT = "middle-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_MIDDLE = "bottom-middle"
    BOTTOM_RIGHT = "bottom-right"

    # For argparse help output.
    def __str__(self):
        return self.value


@dataclass(frozen=True)
class AnnotationOptions:
    camera: bool  # Camera body model
    lens: bool  # Lens model, focal length
    exposure: bool  # Aperture, shutter speed, ISO

    @property
    def any(self) -> bool:
        return any((self.camera, self.lens, self.exposure))


def create_annotation_text(metadata: ImageMetadata, options: AnnotationOptions) -> str:
    lines: list[str] = []

    if options.camera:
        camera_model = metadata.camera_model or "??? camera"
        lines.append(camera_model)

    if options.lens:
        lens_model = metadata.lens_model or "??? lens"
        if metadata.focal_length:
            focal_length = str(metadata.focal_length)
        else:
            focal_length = "???"
        lines.append(f"{lens_model}  @ {focal_length}mm")

    if options.exposure:
        if metadata.f_number and metadata.f_number > 0:
            f_number = str(metadata.f_number)
        else:
            f_number = "???"
        if metadata.exposure_time and metadata.exposure_time > 0:
            if metadata.exposure_time >= 0.1:
                exposure_time = str(metadata.exposure_time)
            else:
                exposure_time = f"1/{1 / metadata.exposure_time}"
        else:
            exposure_time = "???"
        if metadata.iso and metadata.iso > 0:
            iso = metadata.iso
        else:
            iso = "???"
        lines.append(f"f/{f_number}  {exposure_time}s  ISO{iso}")

    for line in lines:
        logger.debug(f"Annotation text: {line}")

    text = "\n".join(lines)
    return text


def calculate_text_position_and_anchor(image_size: IntSize, position: TextPosition) -> tuple[IntPos, str]:
    """Calculates the position and anchor to pass to PIL.ImageDraw.text()"""

    # Space between image edge and text. Kinda arbitrarily chosen.
    padding = int(min(image_size) * 0.05)

    width, height = image_size

    x_middle = int(round(width / 2))
    y_middle = int(round(height / 2))
    left = padding
    right = width - padding
    top = padding
    bottom = height - padding

    match position:
        case TextPosition.TOP_LEFT:
            return (left, top), "la"
        case TextPosition.TOP_MIDDLE:
            return (x_middle, top), "ma"
        case TextPosition.TOP_RIGHT:
            return (right, top), "ra"
        case TextPosition.MIDDLE_LEFT:
            return (left, y_middle), "lm"
        case TextPosition.MIDDLE:
            return (x_middle, y_middle), "mm"
        case TextPosition.MIDDLE_RIGHT:
            return (right, y_middle), "rm"
        case TextPosition.BOTTOM_LEFT:
            return (left, bottom), "ld"
        case TextPosition.BOTTOM_MIDDLE:
            return (x_middle, bottom), "md"
        case TextPosition.BOTTOM_RIGHT:
            return (right, bottom), "rd"
        case _:
            raise AssertionError(f"Unhandled TextPosition: {position}")


def calculate_font_size(image_size: IntSize) -> int:
    # Completely empirical and arbitrary.
    # May need adjustment or may need to be configurable.
    return int(image_size[0] / 1000 * 30)


def draw_annotation_text(image: Image, text: str, position: TextPosition, colour: Color) -> Image:
    font_size = calculate_font_size(image.size)
    logger.debug(f"Using font size {font_size}")
    position_pixels, anchor = calculate_text_position_and_anchor(image.size, position)
    logger.debug(f"Drawing text at position={position_pixels} anchor={anchor}")
    draw = ImageDraw.Draw(image)
    draw.text(xy=position_pixels, anchor=anchor, text=text, fill=colour.get_hex_l(), font_size=font_size)
    return image
