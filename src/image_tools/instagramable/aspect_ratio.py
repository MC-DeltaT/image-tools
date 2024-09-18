import logging

logger = logging.getLogger(__name__)


def adjust_aspect_ratio(base_aspect_ratio: float) -> float:
    """Picks the nearest aspect ratio that's valid for Instagram."""

    # Instagram will crop the image if the aspect ratio is not 0.8 or in the range [1, 1.9].
    # Discovered this by trial and error.
    # However large aspect ratios don't look great in my opinion, so limit it to 1.25 (inverse of 0.8).
    if base_aspect_ratio < 0.9:
        new_aspect = 0.8
    else:
        new_aspect = max(1, min(base_aspect_ratio, 1 / 0.8))
    logger.debug(f"Adjusted aspect ratio {base_aspect_ratio:.2f} -> {new_aspect:.2f}")
    return new_aspect
