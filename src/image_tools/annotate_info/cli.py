import logging
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from dataclasses import dataclass
from pathlib import Path

from colour import Color
from PIL import Image

from .metadata import get_image_metadata
from image_tools.annotate_info.text import AnnotationOptions, TextPosition, create_annotation_text, draw_annotation_text
from image_tools.common.cli.batch import (
    get_image_input_file_paths,
    get_output_image_path,
    validate_output_paths,
)
from image_tools.common.cli.exception import AppError
from image_tools.common.cli.logging import log_config, suppress_external_logging
from image_tools.common.image.imageio import get_pil_image_write_params

logger = logging.getLogger()
logging.basicConfig(style="{", format="{levelname}: {message}")


@dataclass(frozen=True)
class AppConfig:
    input_path: str  # File name or glob
    output_directory: Path | None  # If none, output to input directory
    output_file_name_suffix: str
    allow_overwrite: bool
    dry_run: bool
    verbose: bool
    text_position: TextPosition
    text_colour: Color
    annotate: AnnotationOptions


def get_config(args: list[str]) -> AppConfig:
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("files", type=str, help="File path, directory path, or path glob to process.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory path. Defaults to output in the same directory as the input.",
    )
    parser.add_argument("--output-suffix", type=str, default="-annotated", help="Output file name suffix.")
    parser.add_argument(
        "--overwrite", action="store_true", default=False, help="Allow overwriting files which already exist."
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=False, help="Simulate the operation without writing any files."
    )
    parser.add_argument(
        "--verbose", action="store_true", default=False, help="Print more information about the operation."
    )
    parser.add_argument(
        "--text-position",
        type=TextPosition,
        choices=list(TextPosition),
        default=TextPosition.TOP_LEFT,
        help="Where to place the annotation text on the image.",
    )
    parser.add_argument("--text-colour", type=Color, default="red", help="Border colour, as a W3C colour name.")
    parser.add_argument("--camera", action="store_true", default=False, help="Annotate camera body information.")
    parser.add_argument("--lens", action="store_true", default=False, help="Annotate lens information.")
    parser.add_argument("--exposure", action="store_true", default=False, help="Annotate exposure information.")
    parser.add_argument("--all-info", action="store_true", default=False, help="Annotate all supported information.")

    parsed = parser.parse_args(args)

    annotation_options = AnnotationOptions(
        camera=parsed.camera or parsed.all_info,
        lens=parsed.lens or parsed.all_info,
        exposure=parsed.exposure or parsed.all_info,
    )
    if not annotation_options.any:
        parser.error("At least one annotation option is required")

    return AppConfig(
        input_path=parsed.files,
        output_directory=parsed.output_dir,
        output_file_name_suffix=parsed.output_suffix,
        allow_overwrite=parsed.overwrite,
        dry_run=parsed.dry_run,
        verbose=parsed.verbose,
        text_position=parsed.text_position,
        text_colour=parsed.text_colour,
        annotate=annotation_options,
    )


def process_image(input_path: Path, output_path: Path, config: AppConfig) -> None:
    logger.info(f"Processing '{input_path}'")

    # Note if the file is not a valid image, we fail everything. User probably needs to take action.
    image = Image.open(input_path)

    # We're trying to preserve as much as possible from the original image, so save the info now in case it's changed.
    write_params = get_pil_image_write_params(image)

    metadata = get_image_metadata(image)
    annotation_text = create_annotation_text(metadata, config.annotate)
    image = draw_annotation_text(image, annotation_text, config.text_position, config.text_colour)

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

        input_file_paths = get_image_input_file_paths(config.input_path)
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
