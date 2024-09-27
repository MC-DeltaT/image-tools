import logging
from dataclasses import dataclass

from PIL import ExifTags
from PIL.Image import Image

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImageMetadata:
    camera_model: str | None
    lens_model: str | None
    focal_length: float | None  # mm
    f_number: float | None
    exposure_time: float | None  # seconds
    iso: int | None


def get_image_metadata(img: Image) -> ImageMetadata:
    exif = img.getexif()
    ifd_exif = exif.get_ifd(ExifTags.IFD.Exif)

    metadata = ImageMetadata(
        camera_model=exif.get(ExifTags.Base.Model),
        lens_model=ifd_exif.get(ExifTags.Base.LensModel),
        focal_length=ifd_exif.get(ExifTags.Base.FocalLength),
        f_number=ifd_exif.get(ExifTags.Base.FNumber),
        exposure_time=ifd_exif.get(ExifTags.Base.ExposureTime),
        iso=ifd_exif.get(ExifTags.Base.ISOSpeedRatings),
    )
    logger.debug(f"Read image metadata: {metadata}")
    return metadata
