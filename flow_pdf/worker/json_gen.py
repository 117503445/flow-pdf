import io
from .common import PageWorker, Block, Range, is_common_span, get_min_bounding_rect
from .common import (
    DocInputParams,
    PageInputParams,
    DocOutputParams,
    PageOutputParams,
    LocalPageOutputParams,
)
from fitz import Document, Page, TextPage
from htutil import file
import fitz
import fitz.utils
from pathlib import Path

from dataclasses import dataclass
from PIL import Image, ImageChops


@dataclass
class DocInParams(DocInputParams):
    most_common_font: str
    most_common_size: int

    big_text_width_range: Range
    big_text_columns: list[Range]

    core_y: Range


@dataclass
class PageInParams(PageInputParams):
    big_blocks: list[list]  # column -> block
    shot_rects: list[list]  # column -> block


@dataclass
class DocOutParams(DocOutputParams):
    pass


@dataclass
class PageOutParams(PageOutputParams):
    pass


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

            def save_shot_pixmap(
                shot: list[tuple[float, float, float, float]], file_dest: Path
            ):
                if len(shot) == 1:
                    page.get_pixmap(clip=get_min_bounding_rect(shot), dpi=288).save(file_dest)  # type: ignore
                    return

                for i in range(len(shot) - 1):
                    if shot[i][2] >= shot[i + 1][0]:
                        self.logger.warning(
                            f"Shot rect not increasing in x: {shot[i]} {shot[i+1]}"
                        )
                        page.get_pixmap(clip=get_min_bounding_rect(shot), dpi=288).save(file_dest)  # type: ignore
                        return

                page_shot: Page = doc.load_page(page_index)
                min_y = min([s[1] for s in shot])
                max_y = max([s[3] for s in shot])
                for r in shot:
                    color = fitz.utils.getColor("white")
                    if r[1] > min_y:
                        page_shot.draw_rect((r[0], min_y, r[2], r[1]), color=color, fill=color)  # type: ignore
                    if r[3] < max_y:
                        page_shot.draw_rect((r[0], r[3], r[2], max_y), color=color, fill=color)  # type: ignore
                page_shot.get_pixmap(clip=get_min_bounding_rect(shot), dpi=288).save(file_dest)  # type: ignore


            def save_inline_shot_pixmap(
                shot: list[tuple[float, float, float, float]], file_dest: Path
            ):
                for i in range(len(shot)):
                    shot[i] = (
                        int(shot[i][0]),
                        int(shot[i][1]),
                        int(shot[i][2]),
                        int(shot[i][3]),
                    )

                r = get_min_bounding_rect(shot)
                img_d = page.get_pixmap(clip=r, dpi=288).tobytes()  # type: ignore
                img_full = Image.open(io.BytesIO(img_d))

                img = Image.new("RGB", img_full.size, (255, 255, 255))
                for s in shot:
                    img_d = page.get_pixmap(clip=s, dpi=288).tobytes()  # type: ignore
                    img_shot = Image.open(io.BytesIO(img_d))
                    img.paste(img_shot, (int(s[0] - r[0]) * 4, int(s[1] - r[1]) * 4))

                img.save(file_dest)

            shot_counter = 0

            block_elements = []

            for c_i in range(len(doc_in.big_text_columns)):
                blocks = page_in.big_blocks[c_i]
                shots = page_in.shot_rects[c_i]

                column_block_elements = []
                for b_i, b in enumerate(blocks):

                    def get_span_type(span):
                        if is_common_span(
                            span, doc_in.most_common_font, doc_in.most_common_size
                        ):
                            span_type = "text"
                        else:
                            span_type = "shot"
                        return span_type

                    p_lines_list: list[list] = [[]]
                    for i in range(len(b["lines"])):
                        line = b["lines"][i]

                        MIN_DELTA = 1
                        if i >= 1:
                            delta = line["bbox"][0] - b["bbox"][0]
                            if delta > MIN_DELTA:
                                last_line = b["lines"][i - 1]
                                if (
                                    last_line["bbox"][0] - b["bbox"][0] < MIN_DELTA
                                    and last_line["bbox"][3] < line["bbox"][1]
                                ):
                                    p_lines_list.append([])
                        p_lines_list[-1].append(line)
                    for p_lines in p_lines_list:
                        p = {
                            "type": "paragraph",
                            "children": [],
                            "y0": p_lines[0]["bbox"][1],
                        }
                        for line in p_lines:
                            spans = line["spans"]

                            result = []
                            current_value = None
                            current_group: list = []

                            for span in spans:
                                if get_span_type(span) != current_value:
                                    if current_value is not None:
                                        result.append(current_group)
                                    current_value = get_span_type(span)
                                    current_group = []
                                current_group.append(span)

                            result.append(current_group)

                            for group in result:
                                if get_span_type(group[0]) == "text":
                                    t = ""
                                    for span in group:
                                        for char in span["chars"]:
                                            t += char["c"]
                                    if (
                                        len(p["children"]) > 0
                                        and p["children"][-1]["type"] == "text"
                                    ):
                                        # TODO
                                        p["children"][-1]["text"] += f" {t}"
                                    else:
                                        p["children"].append(
                                            {
                                                "type": "text",
                                                "text": t,
                                            }
                                        )
                                elif get_span_type(group[0]) == "shot":
                                    if not (
                                        len(group) == 1
                                        and len(group[0]["chars"]) == 1
                                        and group[0]["chars"][0]["c"] == " "
                                    ): # space shoud be ignored, like zero.pdf
                                        file_shot = (
                                            doc_in.dir_output
                                            / "output"
                                            / "assets"
                                            / f"page_{page_index}_shot_{shot_counter}.png"
                                        )
                                        rects = []
                                        for r in group:
                                            rects.append(r["bbox"])
                                        save_inline_shot_pixmap(rects, file_shot)

                                        shot_counter += 1
                                        p["children"].append(
                                            {
                                                "type": "shot",
                                                "path": f"./assets/{file_shot.name}",
                                            }
                                        )
                        column_block_elements.append(p)
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
                            "y0": rect[1],
                            "path": f"./assets/{file_shot.name}",
                        }
                    )

                column_block_elements.sort(key=lambda x: x["y0"])
                for e in column_block_elements:
                    del e["y0"]
                block_elements.extend(column_block_elements)

        return PageOutParams(), LocalPageOutParams(block_elements)

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
