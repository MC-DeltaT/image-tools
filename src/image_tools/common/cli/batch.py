import logging
import os.path
from collections.abc import Iterable
from glob import glob
from pathlib import Path

from image_tools.common.cli.exception import AppError

logger = logging.getLogger(__name__)


def get_input_file_paths(name_or_glob: str) -> list[Path]:
    """Generic input path handling.
    Input may be: file name, directory name, file glob."""

    if os.path.isfile(name_or_glob):
        # If path is a file, process just that file.
        logger.info("Input path is a file")
        return [Path(name_or_glob)]
    elif os.path.isdir(name_or_glob):
        # If path is a directory, process all files in that directory.
        logger.info("Input path is a directory, will process all contained image files")
        return [p for p in Path(name_or_glob).iterdir() if p.is_file()]
    else:
        # Otherwise, find files via glob.
        logger.info("Input path is a glob, will process all matching files")
        return [Path(p) for p in glob(name_or_glob) if os.path.isfile(p)]


# TODO? make this configurable
SUPPORTED_IMAGE_EXTENSIONS = frozenset((".jpg", ".jpeg", ".png"))


def is_image_file_supported(p: Path) -> bool:
    return p.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS


def filter_input_file_paths(paths: Iterable[Path]) -> list[Path]:
    def filter_func(path: Path) -> bool:
        if not is_image_file_supported(path):
            logger.info(f"Ignored non-image file: '{path}'")
            return False
        return True

    return list(filter(filter_func, paths))


def get_output_image_path(input_path: Path, output_directory: Path | None, output_suffix: str) -> Path:
    out_dir = output_directory or input_path.parent
    name = input_path.name
    if output_suffix:
        parts = name.split(".")
        parts[0] = parts[0] + output_suffix
        name = ".".join(parts)
    return out_dir / name


def validate_output_paths(output_paths: Iterable[Path], allow_overwrite: bool) -> None:
    if not allow_overwrite:
        existing = [path for path in output_paths if path.exists()]
        if existing:
            existing_str = ",".join(f"'{path}'" for path in existing)
            raise AppError(f"Would overwrite existing files: {existing_str}")
