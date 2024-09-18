from typing import Any

from PIL.Image import Image


def get_pil_image_write_params(image: Image) -> dict[str, Any]:
    """Get params to pass to `Image.save()` in order to preserve maximum information.
    (By default, PIL doesn't preserve all information when saving images)."""

    write_params: dict[str, Any] = {
        # Preserve metadata
        "icc_profile": image.info.get("icc_profile"),  # Colour profile
        "exif": image.getexif(),  # Camera info and such
    }
    if image.format == "JPEG":
        # Default JPG writing settings are garbage. Aim to preserve quality as much as possible.
        write_params |= {"quality": 95, "subsampling": 0, "optimize": True}
    return write_params
