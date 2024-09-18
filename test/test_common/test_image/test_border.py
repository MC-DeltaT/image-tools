import pytest

from image_tools.common.image.border import BorderSize, detect_border
from test.helpers import get_test_data_image


@pytest.mark.parametrize("file", ["no_border_1.jpg", "no_border_2.png"])
def test_detect_border_no_border(file: str) -> None:
    img = get_test_data_image(file)
    border = detect_border(img)
    assert border.size == BorderSize(0, 0, 0, 0)


def test_detect_border_white_border() -> None:
    img = get_test_data_image("border_white.jpg")
    border = detect_border(img)
    assert border.size == BorderSize(top=149, bottom=151, left=274, right=274)


def test_detect_border_black_border() -> None:
    img = get_test_data_image("border_black.jpg")
    border = detect_border(img)
    assert border.size == BorderSize(top=149, bottom=151, left=349, right=351)


def test_border_size_all_sides() -> None:
    assert not BorderSize(0, 0, 0, 0).all_sides
    assert not BorderSize(1, 0, 0, 0).all_sides
    assert not BorderSize(1, 1, 0, 0).all_sides
    assert not BorderSize(1, 1, 1, 0).all_sides
    assert BorderSize(1, 1, 1, 1).all_sides
