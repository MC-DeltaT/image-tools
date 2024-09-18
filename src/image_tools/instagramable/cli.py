import logging
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from colour import Color
from PIL import Image

from image_tools.common.cli.batch import (
    filter_input_file_paths,
    get_input_file_paths,
    get_output_image_path,
    validate_output_paths,
)
from image_tools.common.cli.exception import AppError
from image_tools.common.cli.logging import log_config, suppress_external_logging
from image_tools.common.image.aspect_ratio import aspect_ratio
from image_tools.common.image.border import remove_border
from image_tools.common.image.imageio import get_pil_image_write_params
from image_tools.common.image.types import size_to_str
from image_tools.instagramable.border import apply_new_border
from image_tools.instagramable.sizing import adjust_image_size

logger = logging.getLogger()
logging.basicConfig(style="{", format="{levelname}: {message}")


class ExistingBorderHandling(Enum):
    ADD = "add"  # Add a border anyway
    REPLACE = "replace"  # Remove old border and add new one

    # For argparse help output.
    def __str__(self):
        return self.value


@dataclass(frozen=True)
class AppConfig:
    input_path: str  # File name or glob
    existing_border_handling: ExistingBorderHandling
    border_colour: Color
    border_baseline_size: float  # Proportional to image size
    max_dimension: int
    output_directory: Path | None  # If none, output to input directory
    output_file_name_suffix: str
    allow_overwrite: bool
    dry_run: bool
    verbose: bool


def get_config(args: list[str]) -> AppConfig:
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("files", type=str, help="File path, directory path, or path glob to process.")
    # TODO? allow excluding files
    parser.add_argument(
        "--existing-border",
        type=ExistingBorderHandling,
        choices=list(ExistingBorderHandling),
        default=ExistingBorderHandling.REPLACE,
        help="How to handle existing borders on images. "
        f"{ExistingBorderHandling.ADD}: Add the new border anyway. "
        f"{ExistingBorderHandling.REPLACE}: Replace the existing border.",
    )
    parser.add_argument("--border-colour", type=Color, default="white", help="Border colour, as a W3C colour name.")
    parser.add_argument(
        "--border-size",
        type=float,
        default=0.1,
        help="Baseline border size, as a proportion of the average image dimension.",
    )
    parser.add_argument(
        "--max-dimension", type=int, default=2000, help="Maximum image width/height. Larger images are rescaled."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory path. Defaults to output in the same directory as the input.",
    )
    parser.add_argument("--output-suffix", type=str, default="-instagram", help="Output file name suffix.")
    parser.add_argument(
        "--overwrite", action="store_true", default=False, help="Allow overwriting files which already exist."
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=False, help="Simulate the operation without writing any files."
    )
    parser.add_argument(
        "--verbose", action="store_true", default=False, help="Print more information about the operation"
    )

    parsed = parser.parse_args(args)

    return AppConfig(
        input_path=parsed.files,
        existing_border_handling=parsed.existing_border,
        border_colour=parsed.border_colour,
        border_baseline_size=parsed.border_size,
        max_dimension=parsed.max_dimension,
        output_directory=parsed.output_dir,
        output_file_name_suffix=parsed.output_suffix,
        allow_overwrite=parsed.overwrite,
        dry_run=parsed.dry_run,
        verbose=parsed.verbose,
    )


def log_final_image_info(image: Image.Image) -> None:
    logger.info(f"New image dimensions: {size_to_str(image.size)}, aspect ratio {aspect_ratio(image.size):.2f}")


def process_image(input_path: Path, output_path: Path, config: AppConfig) -> None:
    logger.info(f"Processing '{input_path}'")
    try:
        image = Image.open(input_path)
    except Image.UnidentifiedImageError as e:
        logger.warning(str(e))
        return

    # We're trying to preserve as much as possible from the original image, so save the info now in case it's changed.
    write_params = get_pil_image_write_params(image)

    def apply_border_func(image: Image.Image) -> Image.Image:
        return apply_new_border(image, config.border_colour, config.border_baseline_size)

    match config.existing_border_handling:
        case ExistingBorderHandling.ADD:
            image = apply_border_func(image)
        case ExistingBorderHandling.REPLACE:
            image = remove_border(image)
            image = apply_border_func(image)
        case v:  # type: ignore
            raise AssertionError(f"Unhandled ExistingBorderHandling {v}")

    image = adjust_image_size(image, config.max_dimension)

    log_final_image_info(image)

    if config.dry_run:
        logger.info(f"Dry run: Would save image to '{output_path}'")
    else:
        # Create the output directory if required.
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if not config.allow_overwrite and output_path.exists():
            raise AppError(f"Would overwrite existing file: '{output_path}'")
        image.save(output_path, **write_params)
        logger.info(f"Saved image to '{output_path}'")


def main():
    try:
        config = get_config(sys.argv[1:])

        if config.verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        suppress_external_logging()

        log_config(config)

        input_file_paths = get_input_file_paths(config.input_path)
        input_file_paths = filter_input_file_paths(input_file_paths)
        if not input_file_paths:
            logger.info("No files to process")
            return

        output_file_paths = [
            get_output_image_path(p, config.output_directory, config.output_file_name_suffix) for p in input_file_paths
        ]

        validate_output_paths(output_file_paths, config.allow_overwrite)

        for input_path, output_path in zip(input_file_paths, output_file_paths):
            process_image(input_path, output_path, config)

        logger.info("Success")
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
