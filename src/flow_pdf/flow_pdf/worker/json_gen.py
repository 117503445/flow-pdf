import io
from .common import PageWorker, is_common_span, get_min_bounding_rect
from .common import (
    DocInputParams,
    PageInputParams,
    DocOutputParams,
    PageOutputParams,
    LocalPageOutputParams,
)
from fitz import Document, Page, TextPage  # type: ignore
from htutil import file
import fitz
import fitz.utils
from pathlib import Path

from dataclasses import dataclass
from PIL import Image, ImageChops

from .flow_type import (
    MSimpleBlock,
    MPage,
    init_mpage_from_mupdf,
    Rectangle,
    Range,
    MTextBlock,
    Shot,
    ShotR,
    MLine,
    MSpan,
)


@dataclass
class DocInParams(DocInputParams):
    most_common_font: str
    common_size_range: Range

    big_text_width_range: Range
    big_text_columns: list[Range]

    core_y: Range


@dataclass
class PageInParams(PageInputParams):
    big_blocks: list[list[MTextBlock]]  # column -> blocks
    shot_rects: list[list[Shot]]  # column -> shots


@dataclass
class DocOutParams(DocOutputParams):
    pass


@dataclass
class PageOutParams(PageOutputParams):
    inline_shots: list[ShotR]


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    elements: list


class JSONGenWorker(PageWorker):
    def __init__(self) -> None:
        super().__init__()

        self.disable_cache = True

    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        with fitz.open(doc_in.file_input) as doc:  # type: ignore
            page: Page = doc.load_page(page_index)

            def crop_image(f: Path):
                with Image.open(f) as img:
                    bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
                    img = img.crop(ImageChops.difference(img, bg).getbbox())
                    img.save(f)

            def save_shot_pixmap(shot: list[Rectangle], file_dest: Path):
                x = []
                for s in shot:
                    x.append(s.__dict__)
                if len(shot) == 1:
                    page.get_pixmap(clip=get_min_bounding_rect(shot).to_tuple(), dpi=288).save(file_dest)  # type: ignore
                    return

                for i in range(len(shot) - 1):
                    if shot[i].x1 >= shot[i + 1].x0:
                        self.logger.warning(
                            f"Shot rect not increasing in x: {shot[i]} {shot[i+1]}"
                        )
                        page.get_pixmap(clip=get_min_bounding_rect(shot).to_tuple(), dpi=288).save(file_dest)  # type: ignore
                        return

                page_shot: Page = doc.load_page(page_index)
                min_y = min([s.y0 for s in shot])
                max_y = max([s.y1 for s in shot])
                for r in shot:
                    color = fitz.utils.getColor("white")
                    if r.y0 > min_y:
                        page_shot.draw_rect((r.x0, min_y, r.x1, r.y0), color=color, fill=color)  # type: ignore
                    if r.y1 < max_y:
                        page_shot.draw_rect((r.x0, r.y1, r.x1, max_y), color=color, fill=color)  # type: ignore
                page_shot.get_pixmap(clip=get_min_bounding_rect(shot).to_tuple(), dpi=288).save(file_dest)  # type: ignore

            def get_span_type(span: MSpan):
                if is_common_span(
                    span, doc_in.most_common_font, doc_in.common_size_range
                ):
                    span_type = "text"
                else:
                    span_type = "shot"
                return span_type

            inline_shots: list[ShotR] = []

            SpanGroup = list[MSpan]

            def make_groups(line: MLine) -> list[SpanGroup]:
                """
                group spans by type
                """

                spans = line.spans

                groups: list[SpanGroup] = []
                current_type = None
                current_group: SpanGroup = []

                for span in spans:
                    if get_span_type(span) != current_type:
                        if current_type is not None:
                            groups.append(current_group)
                        current_type = get_span_type(span)
                        current_group = []
                    current_group.append(span)

                groups.append(current_group)
                return groups

            shot_counter = 0

            block_elements = []

            for column_index in range(len(doc_in.big_text_columns)):
                blocks = page_in.big_blocks[column_index]

                column_block_elements = []
                for b in blocks:
                    p = {
                        "type": "paragraph",
                        "children": [],
                        "y0": b.lines[0].bbox.y0,
                    }
                    chidren: list = p["children"]  # type: ignore
                    for line in b.lines:
                        groups = make_groups(line)

                        for j, group in enumerate(groups):
                            if get_span_type(group[0]) == "text":
                                t = ""
                                for span in group:
                                    for char in span.chars:
                                        t += char.c

                                if len(chidren) > 0 and chidren[-1]["type"] == "text":
                                    # when last text item end with '-', no need to add extra space
                                    if chidren[-1]["text"][-1] not in "- ":
                                        t = " " + t
                                    chidren[-1]["text"] += t
                                else:
                                    chidren.append(
                                        {
                                            "type": "text",
                                            "text": t,
                                        }
                                    )
                            elif get_span_type(group[0]) == "shot":
                                if not (
                                    len(group) == 1
                                    and len(group[0].chars) == 1
                                    and group[0].chars[0].c == " "
                                ):  # space shoud be ignored, like zero.pdf
                                    file_shot = (
                                        doc_in.dir_output
                                        / "output"
                                        / "assets"
                                        / f"page_{page_index}_shot_{shot_counter}.png"
                                    )
                                    shot_counter += 1
                                    x0 = group[0].bbox.x0
                                    if j != 0:
                                        x0 = min(x0, groups[j - 1][-1].bbox.x1)

                                    x1 = group[-1].bbox.x1
                                    if j != len(groups) - 1:
                                        x1 = max(x0, groups[j + 1][0].bbox.x0)

                                    r = Rectangle(x0, line.bbox.y0, x1, line.bbox.y1)
                                    inline_shots.append(r)

                                    r_tuple = r.to_tuple()

                                    MIN_SIDE_LEN = 1
                                    if (
                                        r_tuple[0] + MIN_SIDE_LEN >= r_tuple[2]
                                        or r_tuple[1] + MIN_SIDE_LEN >= r_tuple[3]
                                    ):
                                        self.logger.warning(
                                            f"page[{page_index}] Shot rect invalid: {r}"
                                        )
                                    else:
                                        page.get_pixmap(clip=r_tuple, dpi=576).save(file_shot)  # type: ignore

                                    chidren.append(
                                        {
                                            "type": "shot",
                                            "path": f"./assets/{file_shot.name}",
                                        }
                                    )
                    column_block_elements.append(p)

                shots = page_in.shot_rects[column_index]
                for shot in shots:
                    rect = get_min_bounding_rect(shot)
                    file_shot = (
                        doc_in.dir_output
                        / "output"
                        / "assets"
                        / f"page_{page_index}_shot_{shot_counter}.png"
                    )
                    save_shot_pixmap(shot, file_shot)
                    # crop_image(file_shot)

                    shot_counter += 1

                    column_block_elements.append(
                        {
                            "type": "shot",
                            "y0": rect.y0,
                            "path": f"./assets/{file_shot.name}",
                        }
                    )

                column_block_elements.sort(key=lambda x: x["y0"])  # type: ignore
                for e in column_block_elements:
                    del e["y0"]
                block_elements.extend(column_block_elements)

        return PageOutParams(inline_shots), LocalPageOutParams(block_elements)

    def post_run_page(self, doc_in: DocInParams, page_in: list[PageInParams]):  # type: ignore[override]
        (doc_in.dir_output / "output" / "assets").mkdir(parents=True, exist_ok=True)

    def after_run_page(  # type: ignore[override]
        self,
        doc_in: DocInParams,
        page_in: list[PageInParams],
        page_out: list[PageOutParams],
        local_page_out: list[LocalPageOutParams],
    ) -> DocOutParams:
        elements = []
        for p in local_page_out:
            elements.extend(p.elements)

        # combine paragraphs
        for i in reversed(range(1, len(elements))):
            cur = elements[i]
            prev = elements[i - 1]

            if cur["type"] == "paragraph" and prev["type"] == "paragraph":
                cur_first_c = ""
                for sp in cur["children"]:
                    if sp["type"] == "text":
                        cur_first_c = sp["text"][0]
                        break
                if not cur_first_c:
                    continue

                prev_last_c = ""
                for sp in reversed(prev["children"]):
                    if sp["type"] == "text":
                        prev_last_c = sp["text"][-1]
                        break
                if not prev_last_c:
                    continue

                def is_valid(c: str):
                    return c.islower() or c in " "

                if is_valid(cur_first_c) and is_valid(prev_last_c):
                    elements[i - 1]["children"].extend(elements[i]["children"])
                    del elements[i]

        file.write_json(
            doc_in.dir_output / "output" / "doc.json",
            {"meta": {"flow-pdf-version": self.version}, "elements": elements},
        )

        return DocOutParams()
