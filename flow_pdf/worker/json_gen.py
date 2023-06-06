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

from dataclasses import dataclass


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

            shot_counter = 0

            block_elements = []

            for c_i, column in enumerate(doc_in.big_text_columns):
                blocks = page_in.big_blocks[c_i]
                shots = page_in.shot_rects[c_i]

                column_block_elements = []
                for b in blocks:
                    block_element = {
                        "type": "block",
                        "y0": b["bbox"][1],
                        "childs": [],
                    }

                    def get_span_type(span):
                        if is_common_span(
                            span, doc_in.most_common_font, doc_in.most_common_size
                        ):
                            span_type = "text"
                        else:
                            span_type = "shot"
                        return span_type

                    for i in range(len(b["lines"])):
                        line = b["lines"][i]

                        MIN_DELTA = 1
                        if i >= 1:
                            delta = line["bbox"][0] - b["bbox"][0]
                            if delta > MIN_DELTA:
                                last_line = b["lines"][i - 1]
                                if last_line["bbox"][0] - b["bbox"][0] < MIN_DELTA:
                                    block_element["childs"].append(
                                        {
                                            "type": "new-line",
                                        }
                                    )

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
                                block_element["childs"].append(
                                    {
                                        "type": "text",
                                        "text": t,
                                    }
                                )
                            elif get_span_type(group[0]) == "shot":
                                file_shot = (
                                    doc_in.dir_output
                                    / "output"
                                    / "assets"
                                    / f"page_{page_index}_shot_{shot_counter}.png"
                                )
                                y_0 = min([s["bbox"][1] for s in group])
                                y_1 = max([s["bbox"][3] for s in group])
                                r = (
                                    group[0]["bbox"][0],
                                    y_0,
                                    group[-1]["bbox"][2],
                                    y_1,
                                )
                                page.get_pixmap(clip=r, dpi=288).save(file_shot)  # type: ignore
                                shot_counter += 1
                                block_element["childs"].append(
                                    {
                                        "type": "shot",
                                        "path": f"./assets/{file_shot.name}",
                                    }
                                )
                    column_block_elements.append(block_element)
                for shot in shots:
                    rect = get_min_bounding_rect(shot)
                    file_shot = (
                        doc_in.dir_output
                        / "output"
                        / "assets"
                        / f"page_{page_index}_shot_{shot_counter}.png"
                    )
                    page.get_pixmap(clip=rect, dpi=288).save(file_shot)  # type: ignore
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

        file.write_json(
            doc_in.dir_output / "output" / "doc.json",
            {"meta": {"flow-pdf-version": self.version}, "elements": elements},
        )

        return DocOutParams()
