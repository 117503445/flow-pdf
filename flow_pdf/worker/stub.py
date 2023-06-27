from typing import Union


class Point:
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


def init_point_from_mupdf(mupdf_point) -> Point:
    x = mupdf_point[0]
    y = mupdf_point[1]
    return Point(x, y)


class Rectangle:
    x0: float
    y0: float
    x1: float
    y1: float

    def __init__(self, x0: float, y0: float, x1: float, y1: float):
        if x0 > x1:
            raise ValueError("x0 must be less than or equal to x1")
        if y0 > y1:
            raise ValueError("y0 must be less than or equal to y1")

        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1


def init_rectangle_from_mupdf(mupdf_rect) -> Rectangle:
    x0 = mupdf_rect[0]
    y0 = mupdf_rect[1]
    x1 = mupdf_rect[2]
    y1 = mupdf_rect[3]
    return Rectangle(x0, y0, x1, y1)


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

    def __init__(self, bbox: Rectangle, c: str, origin: Point):
        self.bbox = bbox
        self.c = c
        self.origin = origin


def init_mchar_from_mupdf(mupdf_char) -> MChar:
    bbox = init_rectangle_from_mupdf(mupdf_char.bbox)
    c = mupdf_char.c
    origin = init_point_from_mupdf(mupdf_char.origin)
    return MChar(bbox, c, origin)


class MSpan:
    bbox: Rectangle
    color: RGB
    font: str
    # font size
    size: int
    flags: int
    origin: Point
    chars: list[MChar]

    def __init__(
        self,
        bbox: Rectangle,
        color: RGB,
        font: str,
        size: int,
        flags: int,
        origin: Point,
        chars: list[MChar],
    ):
        self.bbox = bbox
        self.color = color
        self.font = font
        self.size = size
        self.flags = flags
        self.origin = origin
        self.chars = chars


def init_mspan_from_mupdf(mupdf_span) -> MSpan:
    bbox = init_rectangle_from_mupdf(mupdf_span.bbox)
    color = mupdf_span.color
    font = mupdf_span.font
    size = mupdf_span.size
    flags = mupdf_span.flags
    origin = init_point_from_mupdf(mupdf_span.origin)
    chars = [init_mchar_from_mupdf(mupdf_char) for mupdf_char in mupdf_span.chars]
    return MSpan(bbox, color, font, size, flags, origin, chars)


class MLine:
    bbox: Rectangle
    wmode: WritingMode
    # writing direction, point_like
    dir: Point
    spans: list[MSpan]

    def __init__(
        self, bbox: Rectangle, wmode: WritingMode, dir: Point, spans: list[MSpan]
    ):
        self.bbox = bbox
        self.wmode = wmode
        self.dir = dir
        self.spans = spans


def init_mline_from_mupdf(mupdf_line) -> MLine:
    bbox = init_rectangle_from_mupdf(mupdf_line.bbox)
    wmode = mupdf_line.wmode
    dir = init_point_from_mupdf(mupdf_line.dir)
    spans = [init_mspan_from_mupdf(mupdf_span) for mupdf_span in mupdf_line.spans]
    return MLine(bbox, wmode, dir, spans)


class MTextBlock:
    type: int
    bbox: Rectangle
    number: int
    lines: list[MLine]

    def __init__(self, type: int, bbox: Rectangle, number: int, lines: list[MLine]):
        self.type = type
        self.bbox = bbox
        self.number = number
        self.lines = lines


def init_mtextblock_from_mupdf(mupdf_block) -> MTextBlock:
    type = mupdf_block.type
    bbox = init_rectangle_from_mupdf(mupdf_block.bbox)
    number = mupdf_block.number
    lines = [init_mline_from_mupdf(mupdf_line) for mupdf_line in mupdf_block.lines]
    return MTextBlock(type, bbox, number, lines)


class MImageBlock:
    type: int
    bbox: Rectangle
    number: int

    # TODO
    def __init__(self, type: int, bbox: Rectangle, number: int):
        self.type = type
        self.bbox = bbox
        self.number = number


def init_mimageblock_from_mupdf(mupdf_block) -> MImageBlock:
    type = mupdf_block.type
    bbox = init_rectangle_from_mupdf(mupdf_block.bbox)
    number = mupdf_block.number
    return MImageBlock(type, bbox, number)


class MPage:
    weight: int
    height: int

    blocks: list[Union[MTextBlock, MImageBlock]]

    def __init__(
        self, width: int, height: int, blocks: list[Union[MTextBlock, MImageBlock]]
    ):
        self.width = width
        self.height = height
        self.blocks = blocks


def init_mpage_from_mupdf(mupdf_page) -> MPage:
    width = mupdf_page.width
    height = mupdf_page.height
    blocks: list[Union[MTextBlock, MImageBlock]] = []
    for mupdf_block in mupdf_page.blocks:
        if mupdf_block.type == 0:
            blocks.append(init_mtextblock_from_mupdf(mupdf_block))
        elif mupdf_block.type == 1:
            blocks.append(init_mimageblock_from_mupdf(mupdf_block))
        else:
            raise ValueError("Unknown block type")
    return MPage(width, height, blocks)
