from typing import Union

Point = tuple[float, float]
Rectangle = tuple[float, float, float, float]

# `color` is the text color encoded in sRGB (int) format, e.g. 0xFF0000 for red. There are functions for converting this integer back to formats (r, g, b) (PDF with float values from 0 to 1) sRGB_to_pdf(), or (R, G, B), sRGB_to_rgb() (with integer values from 0 to 255).
RGB = int

# `flags` is an integer, which represents font properties except for the first bit 0. They are to be interpreted like this:
# bit 0: superscripted (20) – not a font property, detected by MuPDF code.
# bit 1: italic (21)
# bit 2: serifed (22)
# bit 3: monospaced (23)
# bit 4: bold (24)
Flag = int


# writing mode (int): 0 = horizontal, 1 = vertical
WritingMode = int

class MChar:
    bbox: Rectangle
    c: str
    origin: Point


class MSpan:
    bbox: Rectangle
    color: RGB
    font: str
    # font size
    size: int
    flags: int
    origin: Point    
    chars: list[MChar]

class MLine:
    bbox: Rectangle
    wmode: WritingMode
    # writing direction, point_like
    dir: Point
    spans: list[MSpan]

class MTextBlock:
    type: int
    bbox: Rectangle
    number: int
    lines: list[MLine]

class MImageBlock:
    type: int
    bbox: Rectangle
    number: int
    # TODO

class MPage:
    weight: int
    height: int
    
    blocks: list[Union[MTextBlock, MImageBlock]]