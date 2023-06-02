from .common import PageWorker, Range, Block
from .common import (
    DocInputParams,
    PageInputParams,
    DocOutputParams,
    PageOutputParams,
    LocalPageOutputParams,
)

from dataclasses import dataclass

from htutil import file
from fitz import Page
import fitz
import fitz.utils


@dataclass
class DocInParams(DocInputParams):
    most_common_font: str
    most_common_size: int

    big_text_width_range: Range
    big_text_columns: list[Range]

    core_y: Range


@dataclass
class PageInParams(PageInputParams):
    raw_dict: dict
    big_blocks: list
    image_blocks: list[dict]
    shot_rects: list


@dataclass
class DocOutParams(DocOutputParams):
    pass


@dataclass
class PageOutParams(PageOutputParams):
    pass


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    pass


class DumpWorker(PageWorker):
    def __init__(self) -> None:
        super().__init__()

        self.disable_cache = True

    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        with fitz.open(doc_in.file_input) as doc:  # type: ignore
            page: Page = doc.load_page(page_index)
            file.write_text(doc_in.dir_output / "raw_dict" / f"{page_index}.json", page.get_text("rawjson"))  # type: ignore

            page.get_pixmap(dpi=150).save(doc_in.dir_output / "raw" / f"{page_index}.png")  # type: ignore

            def add_annot(page, rects, annot: str, color):
                if not rects:
                    return

                for rect in rects:
                    page.add_freetext_annot(
                        (rect[0], rect[1], rect[0] + len(annot) * 5, rect[1] + 10),
                        annot,
                        fill_color=fitz.utils.getColor("white"),
                        border_color=fitz.utils.getColor("black"),
                    )

                    page.draw_rect(rect, color=fitz.utils.getColor(color))  # type: ignore

            rects = []
            for block in page_in.raw_dict['blocks']:
                rects.append(block["bbox"])
            add_annot(page, rects, "block", "blue")

            # rects = []
            # for block in page_in.big_blocks:
            #     rects.append(block["bbox"])
            # add_annot(page, rects, "big-block", "blue")

            # if 'drawings' in self.params:
            #     add_annot(page, self.params['drawings'][page_index], 'drawings', 'red')

            rects = []
            for block in page_in.image_blocks:
                rects.append(block["bbox"])
            add_annot(page, rects, "images", "red")

            add_annot(page, page_in.shot_rects, "shot", "green")

            page.get_pixmap(dpi=150).save(doc_in.dir_output / "marked" / f"{page_index}.png")  # type: ignore

        return PageOutParams(), LocalPageOutParams()

    def post_run_page(self, doc_in: DocInParams, page_in: list[PageInParams]):  # type: ignore[override]
        for p in ["marked", "raw_dict", "raw"]:
            (doc_in.dir_output / p).mkdir(parents=True, exist_ok=True)

    def after_run_page(  # type: ignore[override]
        self,
        doc_in: DocInParams,
        page_in: list[PageInParams],
        page_out: list[PageOutParams],
        local_page_out: list[LocalPageOutParams],
    ) -> DocOutParams:
        file.write_json(
            doc_in.dir_output / "meta.json", {"page_count": doc_in.page_count}
        )

        file_meta = doc_in.dir_output / "meta.json"
        file.write_json(
            file_meta,
            {
                "most_common_font": doc_in.most_common_font,
                "most_common_size": doc_in.most_common_size,
                "big_text_width_range": doc_in.big_text_width_range,
                "big_text_columns": doc_in.big_text_columns,
                "core_y": doc_in.core_y,
            },
        )

        return DocOutParams()
