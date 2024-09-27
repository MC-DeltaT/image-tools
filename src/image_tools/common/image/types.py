# Width, height
IntSize = tuple[int, int]

# X, Y
IntPos = tuple[int, int]


def size_to_str(size: tuple[int, int]) -> str:
    return f"{size[0]}x{size[1]}"
