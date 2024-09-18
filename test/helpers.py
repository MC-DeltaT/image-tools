from pathlib import Path

from PIL import Image


def get_test_data(path: str) -> Path:
    return Path(__file__).parent / "data" / path


def get_test_data_image(path: str) -> Image.Image:
    return Image.open(get_test_data(path))
