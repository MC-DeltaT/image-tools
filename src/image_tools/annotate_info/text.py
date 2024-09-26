from dataclasses import dataclass
from enum import Enum

from colour import Color
from PIL import ImageDraw
from PIL.Image import Image

from image_tools.annotate_info.metadata import ImageMetadata
from image_tools.common.image.types import IntPos, IntSize


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


def create_annotation_text(metadata: ImageMetadata, options: AnnotationOptions) -> str:
    text = ""

    if options.camera:
        camera_model = metadata.camera_model or "??? camera"
        text += camera_model

    if options.lens:
        lens_model = metadata.lens_model or "??? lens"
        if metadata.focal_length:
            focal_length = str(metadata.focal_length)
        else:
            focal_length = "???"
        text += f"\n{lens_model}  @ {focal_length}mm"

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
        text += f"\nf/{f_number}  {exposure_time}s  ISO {iso}"

    return text


def calculate_text_position_pixels(image_size: IntSize, position: TextPosition) -> IntPos: ...  # TODO


def calculate_font_size(image_size: IntSize) -> int:
    # Completely empirical and arbitrary.
    # May need adjustment or may need to be configurable.
    return int(image_size[0] / 1000 * 40)


def draw_annotation_text(image: Image, text: str, position: TextPosition, colour: Color) -> Image:
    draw = ImageDraw.Draw(image)
    font_size = calculate_font_size(image.size)
    position_pixels = calculate_text_position_pixels(image.size, position)
    draw.text(position_pixels, text, colour.get_hex_l(), font_size=font_size)
    return image
