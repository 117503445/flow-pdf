from .common import PageWorker, Block, Range
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
    big_blocks: list
    shot_rects: list


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

            for column in doc_in.big_text_columns:
                blocks = [
                    b
                    for b in page_in.big_blocks
                    if b["bbox"][0] >= column.min and b["bbox"][2] <= column.max
                ]
                shots = [
                    b
                    for b in page_in.shot_rects
                    if b[0] >= column.min and b[2] <= column.max
                ]

                column_block_elements = []
                for b in blocks:
                    block_element = {
                        "type": "block",
                        "y0": b["bbox"][1],
                        "childs": [],
                    }

                    def get_span_type(span):
                        if (
                            span["font"] != doc_in.most_common_font
                            or span["size"] != doc_in.most_common_size
                        ):
                            span_type = "shot"
                        else:
                            span_type = "text"
                        return span_type

                    for line in b["lines"]:
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
                for s in shots:
                    file_shot = (
                        doc_in.dir_output
                        / "output"
                        / "assets"
                        / f"page_{page_index}_shot_{shot_counter}.png"
                    )
                    page.get_pixmap(clip=s, dpi=288).save(file_shot)  # type: ignore
                    shot_counter += 1

                    column_block_elements.append(
                        {
                            "type": "shot",
                            "y0": s[1],
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

        file.write_json(doc_in.dir_output / "output" / "elements.json", elements)

        return DocOutParams()
